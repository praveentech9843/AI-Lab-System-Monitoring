import time
import logging
import signal
import sys
from websocket_client import AgentWebSocketClient
import config

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
        
        logger.info("Student Agent started, waiting...")

    def stop(self):
        if not self.running:
            return
        logger.info("Stopping Student Agent...")
        self.running = False
        
        # Stop WebSocket client
        self.ws_client.stop()
        logger.info("Student Agent stopped successfully.")

def main():
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

