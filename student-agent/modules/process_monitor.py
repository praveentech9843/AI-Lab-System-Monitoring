import time
import threading
import logging
import psutil
import config

logger = logging.getLogger("ProcessMonitor")

class ProcessMonitor:
    def __init__(self, ws_client):
        self.ws_client = ws_client
        self.running = False
        self.thread = None

    def start(self):
        if config.PROCESS_MONITOR_ENABLED:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Process monitor started")

    def _get_running_processes(self):
        processes = set()
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name:
                    processes.add(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return sorted(list(processes))

    def _run(self):
        while self.running:
            try:
                processes = self._get_running_processes()
                logger.info(f"Monitoring {len(processes)} active processes")
                
                from utils.helpers import create_message
                payload = create_message("process", {
                    "processes": processes
                })
                self.ws_client.send_message(payload)
            except Exception as e:
                logger.error(f"Error gathering process list: {e}")

            time.sleep(config.PROCESS_MONITOR_INTERVAL)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Process monitor stopped")
