import time
import threading
import logging
import cv2
import numpy as np
import mss
import config

logger = logging.getLogger("ScreenStream")

class ScreenStreamer:
    def __init__(self, ws_client):
        self.ws_client = ws_client
        self.running = False
        self.thread = None
        self.error_logged = False

    def start(self):
        if config.SCREEN_STREAM_ENABLED:
            self.running = True
            self.error_logged = False
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Screen stream monitor started")

    def _run(self):
        with mss.mss() as sct:
            # Monitor index (e.g. 1 is primary monitor)
            monitor = sct.monitors[1]
            
            while self.running:
                start_time = time.time()
                try:
                    # Capture screen
                    screenshot = sct.grab(monitor)
                    
                    # Convert to numpy array
                    img = np.array(screenshot)
                    
                    # Convert from BGRA to BGR
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    
                    # Compress to JPEG
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.SCREEN_QUALITY]
                    result, encimg = cv2.imencode('.jpg', img_bgr, encode_param)
                    
                    if result:
                        # Convert to base64 or send as raw binary
                        # For JSON websocket client, we can send base64 encoded string
                        import base64
                        base64_data = base64.b64encode(encimg).decode('utf-8')
                        
                        from utils.helpers import create_message
                        payload = create_message("screen", {
                            "frame": base64_data
                        })
                        self.ws_client.send_message(payload)
                        self.error_logged = False  # Reset error logging state on success
                except Exception as e:
                    if not self.error_logged:
                        logger.error(f"Error capturing or sending screen frame: {e}. Subsequent capture errors will be silenced.")
                        self.error_logged = True

                # Sleep to maintain FPS
                elapsed = time.time() - start_time
                delay = max(0, (1.0 / config.SCREEN_FPS) - elapsed)
                time.sleep(delay)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Screen stream monitor stopped")
