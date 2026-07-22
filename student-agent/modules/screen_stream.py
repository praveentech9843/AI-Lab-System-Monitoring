import asyncio
import base64
import sys
import cv2
import numpy as np
import mss
import config
from utils.helpers import build_message

async def screen_stream_loop(client):
    """Captures, processes, compresses, and streams screen frames over WebSocket."""
    with mss.mss() as sct:
        # Get primary monitor details
        monitor = sct.monitors[1]
        
        # Track logging to prevent console spam in headless/CI test runners
        error_logged = False
        
        while client.connected:
            start_time = asyncio.get_event_loop().time()
            try:
                # Capture primary monitor screen
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                img = np.array(screenshot)
                
                # Convert from BGRA to BGR (OpenCV format)
                img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Resize to standard width of 1024 to save bandwidth
                h, w = img_bgr.shape[:2]
                target_width = 1024
                if w > target_width:
                    target_height = int(h * (target_width / w))
                    img_bgr = cv2.resize(img_bgr, (target_width, target_height), interpolation=cv2.INTER_AREA)
                
                # Compress to JPEG
                quality = getattr(config, "JPEG_QUALITY", 50)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                result, encimg = cv2.imencode('.jpg', img_bgr, encode_param)
                
                if result:
                    # Convert to base64 string
                    base64_data = base64.b64encode(encimg).decode('utf-8')
                    
                    # Create payload using the build_message helper
                    message = build_message(
                        type="screen",
                        data={
                            "frame": base64_data
                        }
                    )
                    await client.send(message)
                    error_logged = False  # Reset error logged state on success
            except Exception as e:
                if not error_logged:
                    print(f"Screen stream error: {e}. Subsequent errors will be silenced.")
                    sys.stdout.flush()
                    error_logged = True
            
            # Maintain FPS rate
            fps = getattr(config, "SCREEN_FPS", 10)
            elapsed = asyncio.get_event_loop().time() - start_time
            delay = max(0.01, (1.0 / fps) - elapsed)
            await asyncio.sleep(delay)
