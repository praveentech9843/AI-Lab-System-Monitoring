import time
import threading
import logging
import sys
import config

logger = logging.getLogger("ActiveWindow")

# Windows-specific imports
if sys.platform == "win32":
    try:
        import win32gui
        import win32process
        import psutil
        win32_available = True
    except ImportError:
        win32_available = False
        logger.warning("pywin32 or psutil not installed. Active window monitoring will not work properly on Windows.")
else:
    win32_available = False

class ActiveWindowMonitor:
    def __init__(self, ws_client):
        self.ws_client = ws_client
        self.running = False
        self.thread = None
        self.last_active_window = None

    def start(self):
        if config.ACTIVE_WINDOW_ENABLED:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Active window monitor started")

    def _get_active_window_info(self):
        if not win32_available:
            return "Unknown", "Unknown"

        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            return title, proc_name
        except Exception as e:
            # Can happen if the process just closed or is running as admin
            return "Unknown", "Unknown"

    def _run(self):
        while self.running:
            title, proc_name = self._get_active_window_info()
            current_info = {"title": title, "process": proc_name}
            
            if current_info != self.last_active_window:
                self.last_active_window = current_info
                logger.info(f"Active Window Changed: {title} ({proc_name})")
                
                from utils.helpers import create_message
                payload = create_message("active_window", {
                    "title": title,
                    "process_name": proc_name
                })
                self.ws_client.send_message(payload)
                
            time.sleep(1)  # Poll every second for changes

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Active window monitor stopped")
