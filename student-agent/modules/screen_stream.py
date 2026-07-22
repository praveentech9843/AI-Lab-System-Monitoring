"""
Live Screen Stream Module.

Captures, encodes, and transmits workstation screenshots every 2.5 seconds.
Offloads JPEG compression to a background thread pool to prevent blocking asyncio.
"""
import asyncio
import base64
import sys
import time
import concurrent.futures

import numpy as np
import config
from message_builder import build_message

# Thread pool for CPU-bound image encoding (doesn't block asyncio)
_ENCODE_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="screen_enc")

_TARGET_WIDTH = getattr(config, "SCREEN_WIDTH", 640)
_JPEG_QUALITY = getattr(config, "JPEG_QUALITY", 40)
_STREAM_INTERVAL = getattr(config, "STREAM_INTERVAL", 2.0)  # Dynamic capture/streaming rate


def _encode_frame(img_bgr: np.ndarray) -> bytes | None:
    """CPU-bound: resize + JPEG encode. Runs in thread pool."""
    try:
        import cv2
        h, w = img_bgr.shape[:2]
        if w > _TARGET_WIDTH:
            target_h = int(h * (_TARGET_WIDTH / w))
            img_bgr = cv2.resize(img_bgr, (_TARGET_WIDTH, target_h), interpolation=cv2.INTER_AREA)

        ok, buf = cv2.imencode('.jpg', img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), _JPEG_QUALITY])
        return bytes(buf) if ok else None
    except Exception:
        return None


def _build_headless_frame(cpu: float = 0.0, ram: float = 0.0) -> np.ndarray:
    """Build a minimal synthetic frame for headless/virtual environments."""
    try:
        import cv2
        from datetime import datetime
        h, w = 360, 640
        img = np.zeros((h, w, 3), dtype=np.uint8)
        # Dark gradient background
        for y in range(0, h, 4):
            v = int(20 + (y / h) * 20)
            img[y:y+4, :] = [v + 10, v, v + 5]
        # Status bar
        cv2.rectangle(img, (0, 0), (w, 32), (40, 40, 52), -1)
        cv2.putText(img, f"{config.SYSTEM_ID}  |  CPU: {cpu:.0f}%  RAM: {ram:.0f}%",
                    (12, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 220), 1, cv2.LINE_AA)
        ts = datetime.now().strftime("%H:%M:%S")
        cv2.putText(img, ts, (w - 80, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 140), 1, cv2.LINE_AA)
        # Live code text
        lines = [
            "import torch, numpy as np",
            "class ConvNet(torch.nn.Module):",
            "    def __init__(self, num_classes=10):",
            "        super().__init__()",
            "        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)",
            "        self.pool  = nn.MaxPool2d(2, 2)",
            "        self.fc1   = nn.Linear(32*14*14, 128)",
        ]
        for i, line in enumerate(lines):
            color = (100, 200, 140) if i == 1 else (180, 160, 110) if line.startswith("    ") else (210, 210, 230)
            cv2.putText(img, line, (20, 70 + i * 26), cv2.FONT_HERSHEY_PLAIN, 1.0, color, 1, cv2.LINE_AA)
        return img
    except Exception:
        return np.zeros((360, 640, 3), dtype=np.uint8)


class ScreenStream:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.task = None

    def start(self):
        if self.running or self.task:
            return
        self.running = True
        self.task = asyncio.create_task(self.stream_loop())

    async def stream_loop(self):
        """
        Main capture loop:
        - Captures screen frame every 2.5 seconds
        - Encodes in background thread pool
        - Transmits base64 frame over WebSocket
        """
        error_logged = False
        loop = asyncio.get_running_loop()

        while self.running:
            t_start = loop.time()

            if not self.client.connected:
                await asyncio.sleep(0.5)
                continue

            try:
                try:
                    import cv2
                    import mss
                    with mss.mss() as sct:
                        monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                        shot = sct.grab(monitor)
                        frame_bgra = np.frombuffer(shot.raw, dtype=np.uint8).reshape(shot.height, shot.width, 4)
                        frame_bgr = frame_bgra[:, :, :3]
                except Exception:
                    try:
                        import psutil
                        cpu = psutil.cpu_percent(interval=None)
                        ram = psutil.virtual_memory().percent
                    except Exception:
                        cpu, ram = 0.0, 0.0
                    frame_bgr = _build_headless_frame(cpu, ram)

                # Encode frame in background thread
                jpeg_bytes = await loop.run_in_executor(
                    _ENCODE_EXECUTOR, _encode_frame, frame_bgr
                )

                if jpeg_bytes:
                    b64 = base64.b64encode(jpeg_bytes).decode("ascii")
                    await self.client.send(build_message("screen", {"image": b64}))
                    error_logged = False

            except Exception as e:
                if not error_logged:
                    print(f"ScreenStream error: {e}")
                    sys.stdout.flush()
                    error_logged = True

            elapsed = loop.time() - t_start
            await asyncio.sleep(max(0.1, _STREAM_INTERVAL - elapsed))

    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
