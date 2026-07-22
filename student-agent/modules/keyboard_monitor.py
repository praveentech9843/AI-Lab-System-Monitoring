import time
import threading
import logging
import config

logger = logging.getLogger("KeyboardMonitor")

try:
    import keyboard
    keyboard_available = True
except ImportError:
    keyboard_available = False
    logger.warning("keyboard not installed. Keyboard monitor will not function.")

class KeyboardMonitor:
    def __init__(self, ws_client):
        self.ws_client = ws_client
        self.running = False
        self.key_count = 0
        self.lock = threading.Lock()
        self.hook = None

    def start(self):
        if config.KEYBOARD_MONITOR_ENABLED and keyboard_available:
            self.running = True
            try:
                self.hook = keyboard.on_press(self._on_press)
                # Start a reporting thread for keystroke statistics
                self.report_thread = threading.Thread(target=self._report_loop)
                self.report_thread.daemon = True
                self.report_thread.start()
                logger.info("Keyboard monitor started")
            except Exception as e:
                logger.error(f"Failed to start keyboard monitor: {e}")

    def _on_press(self, event):
        if not self.running:
            return
        with self.lock:
            self.key_count += 1

    def _report_loop(self):
        while self.running:
            time.sleep(10)  # Report keystroke metrics every 10 seconds
            with self.lock:
                current_count = self.key_count
                self.key_count = 0
            
            if current_count > 0:
                logger.info(f"Keystrokes in last period: {current_count}")
                from utils.helpers import create_message
                payload = create_message("keyboard", {
                    "keystroke_count": current_count
                })
                self.ws_client.send_message(payload)

    def stop(self):
        self.running = False
        if self.hook:
            try:
                keyboard.unhook(self.hook)
            except Exception as e:
                logger.error(f"Failed to unhook keyboard: {e}")
        logger.info("Keyboard monitor stopped")

