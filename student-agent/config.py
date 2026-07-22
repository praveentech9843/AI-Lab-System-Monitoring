import os

# Server connection configuration
SERVER_URL = os.getenv("SERVER_URL", "ws://127.0.0.1:8000/ws")
SYSTEM_ID = os.getenv("SYSTEM_ID", "SYSTEM_01")

# Screen Capture Configuration
FPS = int(os.getenv("FPS", "10"))
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "50"))
SCREEN_WIDTH = int(os.getenv("SCREEN_WIDTH", "1024"))

# Monitoring Intervals (in seconds)
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "10"))
PROCESS_SCAN_INTERVAL = int(os.getenv("PROCESS_SCAN_INTERVAL", "30"))
WINDOW_SCAN_INTERVAL = float(os.getenv("WINDOW_SCAN_INTERVAL", "1.0"))

# Feature Toggles
KEYBOARD_ENABLED = True
CLIPBOARD_ENABLED = True
