import asyncio
import psutil
import config
from message_builder import build_message

class ProcessMonitor:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.task = None

    def start(self):
        """Starts the process scan loop as a background task."""
        self.running = True
        self.task = asyncio.create_task(self.scan_loop())

    async def scan_loop(self):
        """Asynchronously gathers running processes list and dispatches it."""
        while self.running:
            if self.client.connected:
                try:
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'exe']):
                        try:
                            processes.append({
                                "name": proc.info['name'] or "",
                                "pid": proc.info['pid'],
                                "path": proc.info['exe'] or ""
                            })
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass
                    
                    message = build_message(
                        msg_type="processes",
                        data={"processes": processes}
                    )
                    await self.client.send(message)
                except Exception:
                    pass
            await asyncio.sleep(config.PROCESS_SCAN_INTERVAL)

    def stop(self):
        """Stops the process scan loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
