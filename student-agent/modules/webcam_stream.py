"""
Live Webcam Stream Module.

Captures, encodes, and transmits webcam images every 3 seconds.
Runs initialization, frame capture, and device release in a background thread executor
to prevent blocking the main asyncio event loop.
"""
import asyncio
import base64
import sys
import concurrent.futures
import numpy as np
import config
from message_builder import build_message

# Thread pool for CPU-bound image encoding and device access
_WEBCAM_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="webcam_stream")

_TARGET_WIDTH = 320  # Smaller width for webcam (saves bandwidth)
_JPEG_QUALITY = 30   # Slightly lower JPEG quality to save bandwidth
_STREAM_INTERVAL = getattr(config, "WEBCAM_INTERVAL", 3.0)


def _capture_and_encode_frame(cap) -> bytes | None:
    """Captures, resizes, and encodes frame to JPEG. Runs in thread pool."""
    try:
        import cv2
        if cap is None or not cap.isOpened():
            return None
        ret, frame = cap.read()
        if not ret or frame is None:
            return None

        h, w = frame.shape[:2]
        if w > _TARGET_WIDTH:
            target_h = int(h * (_TARGET_WIDTH / w))
            frame = cv2.resize(frame, (_TARGET_WIDTH, target_h), interpolation=cv2.INTER_AREA)

        ok, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), _JPEG_QUALITY])
        return bytes(buf) if ok else None
    except Exception:
        return None


class WebcamStream:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.task = None
        self.cap = None

    def start(self):
        if self.running or self.task:
            return
        self.running = True
        self.task = asyncio.create_task(self.stream_loop())

    async def stream_loop(self):
        """
        Main webcam capture loop:
        - Initializes/re-initializes camera
        - Captures frame every WEBCAM_INTERVAL seconds
        - Encodes in background thread pool
        - Transmits base64 frame over WebSocket
        """
        loop = asyncio.get_running_loop()
        camera_error_logged = False

        # Attempt to initialize camera in executor
        self.cap = await loop.run_in_executor(_WEBCAM_EXECUTOR, self._init_camera_sync)
        if not self.cap or not self.cap.isOpened():
            print("[WebcamStream] Webcam device not found or unavailable. Will retry periodically.")
            sys.stdout.flush()

        while self.running:
            t_start = loop.time()

            if not self.client.connected:
                await asyncio.sleep(0.5)
                continue

            try:
                # If camera was lost or not opened, try to re-init
                if not self.cap or not self.cap.isOpened():
                    self.cap = await loop.run_in_executor(_WEBCAM_EXECUTOR, self._init_camera_sync)

                if self.cap and self.cap.isOpened():
                    jpeg_bytes = await loop.run_in_executor(
                        _WEBCAM_EXECUTOR, _capture_and_encode_frame, self.cap
                    )

                    if jpeg_bytes:
                        b64 = base64.b64encode(jpeg_bytes).decode("ascii")
                        await self.client.send(build_message("webcam", {"image": b64}))
                        camera_error_logged = False
                else:
                    if not camera_error_logged:
                        print("[WebcamStream] Skipping frame capture (device offline/blocked).")
                        sys.stdout.flush()
                        camera_error_logged = True
            except Exception as e:
                print(f"[WebcamStream] Error in stream loop: {e}")
                sys.stdout.flush()

            elapsed = loop.time() - t_start
            await asyncio.sleep(max(0.1, _STREAM_INTERVAL - elapsed))

    def _init_camera_sync(self):
        try:
            import cv2
            # Use DirectShow on Windows to speed up initialization
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(0)
            # Set small resolution to capture fast
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            if cap.isOpened():
                return cap
        except Exception:
            pass
        return None

    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
        if self.cap:
            try:
                cap_to_release = self.cap
                self.cap = None
                # Release camera device in executor to prevent blocking the event loop
                _WEBCAM_EXECUTOR.submit(cap_to_release.release)
            except Exception:
                pass
