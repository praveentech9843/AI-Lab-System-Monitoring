import time
import logging
import signal
import sys
from websocket_client import AgentWebSocketClient
import config
from modules.screen_stream import ScreenStreamer
from modules.active_window import ActiveWindowMonitor
from modules.process_monitor import ProcessMonitor
from modules.keyboard_monitor import KeyboardMonitor
from modules.clipboard_monitor import ClipboardMonitor
from modules.heartbeat import HeartbeatMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Main")

class StudentAgent:
    def __init__(self):
        self.ws_client = AgentWebSocketClient()
        
        # Initialize modules
        self.heartbeat = HeartbeatMonitor(self.ws_client)
        self.screen_stream = ScreenStreamer(self.ws_client)
        self.active_window = ActiveWindowMonitor(self.ws_client)
        self.process_monitor = ProcessMonitor(self.ws_client)
        self.keyboard_monitor = KeyboardMonitor(self.ws_client)
        self.clipboard_monitor = ClipboardMonitor(self.ws_client)
        
        self.running = False

    def start(self):
        logger.info("Starting Student Agent...")
        self.running = True
        
        # Connect WebSocket
        self.ws_client.start()
        
        # Send Test Message (enqueued and sent upon connection)
        from utils.helpers import create_message
        test_payload = create_message("test_message", {"message": "Hello from Student Agent! Foundation check."})
        logger.info("Enqueuing test message...")
        self.ws_client.send_message(test_payload)
        
        # Start monitoring modules
        self.heartbeat.start()
        self.screen_stream.start()
        self.active_window.start()
        self.process_monitor.start()
        self.keyboard_monitor.start()
        self.clipboard_monitor.start()
        
        logger.info("Student Agent started, all modules active.")

    def stop(self):
        if not self.running:
            return
        logger.info("Stopping Student Agent...")
        self.running = False
        
        # Stop monitoring modules
        self.clipboard_monitor.stop()
        self.keyboard_monitor.stop()
        self.process_monitor.stop()
        self.active_window.stop()
        self.screen_stream.stop()
        self.heartbeat.stop()
        
        # Stop WebSocket client
        self.ws_client.stop()
        logger.info("Student Agent stopped successfully.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Student Screen Capture and Activity Agent")
    parser.add_argument("--install-startup", action="store_true", help="Register agent to start automatically on Windows logon")
    parser.add_argument("--uninstall-startup", action="store_true", help="Unregister agent from Windows startup")
    args = parser.parse_args()

    if args.install_startup:
        from utils.autostart import register_startup
        success = register_startup()
        sys.exit(0 if success else 1)
        
    if args.uninstall_startup:
        from utils.autostart import unregister_startup
        success = unregister_startup()
        sys.exit(0 if success else 1)

    agent = StudentAgent()
    
    # Handle graceful exit
    def signal_handler(sig, frame):
        logger.info("Interrupt signal received. Shutting down...")
        agent.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    agent.start()
    
    # Keep the main thread alive
    try:
        while agent.running:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()

if __name__ == "__main__":
    main()

