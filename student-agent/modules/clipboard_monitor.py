import time
import threading
import logging
import sys
import config

logger = logging.getLogger("ClipboardMonitor")

win32_clipboard_available = False
if sys.platform == "win32":
    try:
        import win32clipboard
        win32_clipboard_available = True
    except ImportError:
        logger.warning("pywin32 not installed. Clipboard monitoring will not work.")

class ClipboardMonitor:
    def __init__(self, ws_client):
        self.ws_client = ws_client
        self.running = False
        self.thread = None
        self.last_clipboard_content = ""

    def start(self):
        if config.CLIPBOARD_MONITOR_ENABLED and win32_clipboard_available:
            self.running = True
            self.last_clipboard_content = self._get_clipboard_text()
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Clipboard monitor started")

    def _get_clipboard_text(self):
        try:
            win32clipboard.OpenClipboard()
            data = ""
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                val = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                if isinstance(val, bytes):
                    data = val.decode('utf-8', errors='ignore')
                else:
                    data = str(val)
            win32clipboard.CloseClipboard()
            return data
        except Exception:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            return ""

    def _run(self):
        while self.running:
            try:
                content = self._get_clipboard_text()
                if content and content != self.last_clipboard_content:
                    self.last_clipboard_content = content
                    logger.info("Clipboard content changed")
                    
                    from utils.helpers import create_message
                    payload = create_message("clipboard", {
                        "content": content
                    })
                    self.ws_client.send_message(payload)
            except Exception as e:
                logger.error(f"Error reading clipboard: {e}")

            time.sleep(2)  # Poll clipboard every 2 seconds

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Clipboard monitor stopped")

