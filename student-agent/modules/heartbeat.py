import asyncio
import config
from message_builder import build_message

class Heartbeat:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.task = None

    def start(self):
        """Starts the heartbeat loop as a background task."""
        self.running = True
        self.task = asyncio.create_task(self.run_loop())

    async def run_loop(self):
        """Periodically dispatches a heartbeat payload."""
        while self.running:
            if self.client.connected:
                try:
                    message = build_message(msg_type="heartbeat")
                    await self.client.send(message)
                except Exception:
                    pass
            await asyncio.sleep(config.HEARTBEAT_INTERVAL)

    def stop(self):
        """Stops the heartbeat loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
