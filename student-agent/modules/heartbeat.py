import time
import threading
import logging
import psutil
import config

logger = logging.getLogger("Heartbeat")

class HeartbeatMonitor:
    def __init__(self, ws_client):
        self.ws_client = ws_client
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Heartbeat sender started")

    def _run(self):
        while self.running:
            try:
                cpu_usage = psutil.cpu_percent(interval=None)
                memory_info = psutil.virtual_memory()
                
                from utils.helpers import create_message
                payload = create_message("heartbeat", {
                    "status": "online",
                    "cpu_percent": cpu_usage,
                    "memory_percent": memory_info.percent
                })
                self.ws_client.send_message(payload)
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")

            time.sleep(config.HEARTBEAT_INTERVAL)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Heartbeat sender stopped")
