# ─────────────────────────────────────────────────────────────────
# Student Monitoring Agent — Configuration
# Edit these values before deploying to each lab computer.
# ─────────────────────────────────────────────────────────────────

# ── Identity ──────────────────────────────────────────────────────
COMPUTER_ID   = "PC-01"            # Unique identifier for this workstation
STUDENT_EMAIL = "student@lab.com"  # Registered student email
STUDENT_PASS  = "password123"      # Student password
SESSION_ID    = ""                 # Set by coordinator before exam (UUID string)
                                   # Leave empty to auto-detect latest active session

# ── Backend ───────────────────────────────────────────────────────
BACKEND_URL    = "http://localhost:8000"
REQUEST_TIMEOUT = 8                # seconds
MAX_RETRIES     = 3
RETRY_BACKOFF   = 2.0              # seconds between retries

# ── Polling Intervals (seconds) ───────────────────────────────────
POLL_SYSTEM_INTERVAL      = 5     # CPU / RAM / idle
POLL_APP_INTERVAL         = 3     # Active application
POLL_BROWSER_INTERVAL     = 3     # Active browser tab / website
POLL_USB_INTERVAL         = 5     # USB device changes
POLL_CLIPBOARD_INTERVAL   = 2     # Copy/paste detection
SCREENSHOT_INTERVAL       = 30    # Screenshot capture

# ── Thresholds ────────────────────────────────────────────────────
IDLE_THRESHOLD_SECONDS    = 60    # Seconds before marking as idle
CPU_SPIKE_THRESHOLD       = 85    # % CPU that triggers an alert event
BLOCKED_DOMAINS           = [     # Domains that trigger 'blocked_website' event
    "chatgpt.com",
    "deepseek.com",
    "gemini.google.com",
    "youtube.com",
    "reddit.com",
    "facebook.com",
    "instagram.com",
]

# ── Offline Queue ─────────────────────────────────────────────────
QUEUE_DB_PATH    = "agent_queue.db"   # SQLite file for offline event storage
MAX_QUEUE_SIZE   = 1000               # Max events held while offline
FLUSH_BATCH_SIZE = 20                 # Events sent per flush cycle

# ── Screenshot ────────────────────────────────────────────────────
SCREENSHOT_ENABLED     = True
SCREENSHOT_QUALITY     = 60          # JPEG quality 0–100
SCREENSHOT_MAX_WIDTH   = 1280        # Resize if larger
