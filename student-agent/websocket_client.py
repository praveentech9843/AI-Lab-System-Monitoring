import asyncio
import json
import logging
import threading
import time
import websockets
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("WebSocketClient")

class AgentWebSocketClient:
    def __init__(self, server_url=config.SERVER_URL):
        self.server_url = server_url
        self.loop = None
        self.thread = None
        self.queue = None
        self.connected = False
        self.running = False

    def start(self):
        self.running = True
        self.loop = asyncio.new_event_loop()
        self.queue = asyncio.Queue()
        self.thread = threading.Thread(target=self._run_loop, args=(self.loop,))
        self.thread.daemon = True
        self.thread.start()
        logger.info("WebSocket Client thread started")

    def _run_loop(self, loop):
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._main_task())
        except asyncio.CancelledError:
            logger.info("Main loop tasks cancelled")
        finally:
            loop.close()
            logger.info("Event loop closed")

    async def _main_task(self):
        while self.running:
            try:
                logger.info(f"Connecting to WebSocket server at {self.server_url}...")
                async with websockets.connect(self.server_url) as websocket:
                    self.connected = True
                    logger.info("WebSocket connection established")
                    
                    # Send registration message
                    from utils.helpers import create_message
                    register_payload = create_message("register", {})
                    await websocket.send(json.dumps(register_payload))
                    logger.info(f"Registered with student ID: {config.STUDENT_ID}")
                    
                    # Run send and receive loops concurrently
                    await asyncio.gather(
                        self._send_loop(websocket),
                        self._receive_loop(websocket)
                    )
            except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, Exception) as e:
                self.connected = False
                if self.running:
                    logger.warning(f"Connection lost or failed: {e}. Reconnecting in 5 seconds...")
                    # Wait 5 seconds before reconnecting
                    await asyncio.sleep(5)

    async def _send_loop(self, websocket):
        while self.connected and self.running:
            data = await self.queue.get()
            try:
                await websocket.send(json.dumps(data))
                self.queue.task_done()
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                # Re-queue the message to try again later
                self.queue.put_nowait(data)
                raise e

    async def _receive_loop(self, websocket):
        try:
            async for message in websocket:
                logger.info(f"Received message from server: {message}")
                try:
                    data = json.loads(message)
                    self.handle_command(data)
                except json.JSONDecodeError:
                    logger.error("Failed to decode message as JSON")
        except Exception as e:
            logger.error(f"Error in receive loop: {e}")
            raise e

    def send_message(self, data):
        """Thread-safe method to enqueue messages for sending."""
        if not self.running:
            logger.warning("WebSocket client is not running, message discarded")
            return False
            
        try:
            self.loop.call_soon_threadsafe(self.queue.put_nowait, data)
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue message: {e}")
            return False

    def handle_command(self, command_data):
        # Future server command handler placeholder
        pass

    def stop(self):
        self.running = False
        self.connected = False
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self._cancel_all_tasks)
        if self.thread:
            self.thread.join(timeout=3)
        logger.info("WebSocket client stopped")

    def _cancel_all_tasks(self):
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
        self.loop.stop()

