import os

SERVER_URL = os.getenv("SERVER_URL", "ws://127.0.0.1:8000/ws")
SYSTEM_ID = os.getenv("SYSTEM_ID", "SYSTEM_01")

# Screen Capture Configuration
SCREEN_FPS = int(os.getenv("SCREEN_FPS", "10"))
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "50"))

