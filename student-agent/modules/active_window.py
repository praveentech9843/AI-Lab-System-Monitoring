import asyncio
import sys
import config
from message_builder import build_message

if sys.platform == "win32":
    try:
        import win32gui
        import win32process
        import psutil
        win32_available = True
    except ImportError:
        win32_available = False
else:
    win32_available = False

class ActiveWindow:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.task = None
        self.last_window_info = None

    def start(self):
        """Starts the active window detection scan loop as a background task."""
        if win32_available:
            self.running = True
            self.task = asyncio.create_task(self.scan_loop())

    async def scan_loop(self):
        """Asynchronously monitors for foreground active window changes."""
        while self.running:
            if self.client.connected:
                try:
                    hwnd = win32gui.GetForegroundWindow()
                    title = win32gui.GetWindowText(hwnd)
                    
                    if hwnd and title:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        proc = psutil.Process(pid)
                        executable = proc.name()
                        
                        current_info = {
                            "title": title,
                            "executable": executable,
                            "pid": pid
                        }
                        
                        if current_info != self.last_window_info:
                            self.last_window_info = current_info
                            message = build_message(msg_type="window", data=current_info)
                            await self.client.send(message)
                except Exception:
                    pass
            await asyncio.sleep(config.WINDOW_SCAN_INTERVAL)

    def stop(self):
        """Stops the active window scan loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
