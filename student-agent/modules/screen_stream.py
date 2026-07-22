import asyncio
import base64
import sys
import cv2
import numpy as np
import mss
import config
from message_builder import build_message

class ScreenStream:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.task = None

    def start(self):
        """Starts the screen capture stream loop as a background task."""
        self.running = True
        self.task = asyncio.create_task(self.stream_loop())

    async def stream_loop(self):
        """Asynchronously captures, compresses, and sends screen frames."""
        error_logged = False
        with mss.mss() as sct:
            # Capture the primary monitor
            monitor = sct.monitors[1]
            
            while self.running:
                start_time = asyncio.get_event_loop().time()
                if self.client.connected:
                    try:
                        screenshot = sct.grab(monitor)
                        img = np.array(screenshot)
                        
                        # Convert BGRA to BGR (OpenCV format)
                        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                        
                        # Resize to config width (e.g., 1024) preserving aspect ratio
                        h, w = img_bgr.shape[:2]
                        target_width = getattr(config, "SCREEN_WIDTH", 1024)
                        if w > target_width:
                            target_height = int(h * (target_width / w))
                            img_bgr = cv2.resize(img_bgr, (target_width, target_height), interpolation=cv2.INTER_AREA)
                        
                        # Compress to JPEG
                        quality = getattr(config, "JPEG_QUALITY", 50)
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                        result, encimg = cv2.imencode('.jpg', img_bgr, encode_param)
                        
                        if result:
                            # Convert to base64
                            base64_data = base64.b64encode(encimg).decode('utf-8')
                            
                            # Construct message
                            message = build_message(
                                msg_type="screen",
                                data={"image": base64_data}
                            )
                            await self.client.send(message)
                            error_logged = False
                    except Exception as e:
                        if not error_logged:
                            print(f"Screen Capture Error: {e}. Subsequent errors silenced.")
                            sys.stdout.flush()
                            error_logged = True
                
                # Maintain configurable FPS rate
                fps = getattr(config, "FPS", 10)
                elapsed = asyncio.get_event_loop().time() - start_time
                delay = max(0.01, (1.0 / fps) - elapsed)
                await asyncio.sleep(delay)

    def stop(self):
        """Stops the screen stream loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
