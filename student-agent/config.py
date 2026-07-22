import os

# WebSocket Configuration
SERVER_URL = os.getenv("SERVER_URL", "ws://192.168.1.100:8000/ws")

# Agent Configuration
STUDENT_ID = os.getenv("STUDENT_ID", "STUDENT_001")
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "10"))  # in seconds

# Screen Stream Configuration
SCREEN_STREAM_ENABLED = True
SCREEN_FPS = int(os.getenv("SCREEN_FPS", "10"))
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "50"))  # JPEG quality 0-100

# Monitoring Configuration
ACTIVE_WINDOW_ENABLED = True
PROCESS_MONITOR_ENABLED = True
PROCESS_MONITOR_INTERVAL = int(os.getenv("PROCESS_MONITOR_INTERVAL", "10"))  # in seconds

KEYBOARD_MONITOR_ENABLED = True
CLIPBOARD_MONITOR_ENABLED = True

# Aliases for backward compatibility
WS_SERVER_URL = SERVER_URL
AGENT_ID = STUDENT_ID
SCREEN_QUALITY = JPEG_QUALITY

