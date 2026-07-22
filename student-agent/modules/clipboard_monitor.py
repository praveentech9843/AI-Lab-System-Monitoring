import asyncio
import sys
import config
from message_builder import build_message

if sys.platform == "win32":
    try:
        import win32clipboard
        win32_available = True
    except ImportError:
        win32_available = False
else:
    win32_available = False

class ClipboardMonitor:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.task = None
        self.last_sequence_number = 0

    def start(self):
        """Starts the clipboard monitoring logic if enabled."""
        if config.CLIPBOARD_ENABLED and win32_available:
            self.running = True
            try:
                win32clipboard.OpenClipboard()
                self.last_sequence_number = win32clipboard.GetClipboardSequenceNumber()
                win32clipboard.CloseClipboard()
            except Exception:
                self.last_sequence_number = 0
            self.task = asyncio.create_task(self.scan_loop())

    async def scan_loop(self):
        """Asynchronously polls the clipboard sequence number for changes."""
        while self.running:
            if self.client.connected:
                try:
                    win32clipboard.OpenClipboard()
                    current_seq = win32clipboard.GetClipboardSequenceNumber()
                    win32clipboard.CloseClipboard()
                    
                    if current_seq != self.last_sequence_number:
                        self.last_sequence_number = current_seq
                        
                        # Dispatch notification only (does NOT read or transmit text/contents)
                        message = build_message(
                            msg_type="clipboard",
                            data={"event": "changed"}
                        )
                        await self.client.send(message)
                except Exception:
                    try:
                        win32clipboard.CloseClipboard()
                    except Exception:
                        pass
            await asyncio.sleep(1.0)

    def stop(self):
        """Stops the clipboard monitor loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
