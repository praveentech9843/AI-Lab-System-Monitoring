import asyncio
import json
import sys
import websockets
from config import SERVER_URL, SYSTEM_ID
from utils.helpers import build_message

class WebSocketClient:
    def __init__(self):
        self.websocket = None
        self.connected = False

    async def connect(self):
        while True:
            try:
                print(f"Connecting to {SERVER_URL}...")
                sys.stdout.flush()

                self.websocket = await websockets.connect(SERVER_URL)
                self.connected = True
                
                print("Connected to server")
                sys.stdout.flush()

                await self.register()
                
                # Start heartbeat loop in the background
                from modules.heartbeat import heartbeat_loop
                heartbeat_task = asyncio.create_task(heartbeat_loop(self))
                
                # Start screen stream loop in the background
                from modules.screen_stream import screen_stream_loop
                screen_task = asyncio.create_task(screen_stream_loop(self))
                
                try:
                    await self.receive_messages()
                finally:
                    heartbeat_task.cancel()
                    screen_task.cancel()
                    await asyncio.gather(heartbeat_task, screen_task, return_exceptions=True)

            except Exception as e:
                print(f"Connection Lost: {e}")
                sys.stdout.flush()

                self.connected = False
                
                print("Reconnecting in 5 seconds...")
                sys.stdout.flush()
                
                await asyncio.sleep(5)

    async def register(self):
        # Construct registration payload using the build_message helper
        message = build_message(type="register", data={})
        await self.send(message)
        
        print("Register Message Sent")
        sys.stdout.flush()

    async def send(self, message):
        if self.connected and self.websocket:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception:
                pass

    async def receive_messages(self):
        async for message in self.websocket:
            print("Received:", message)
            sys.stdout.flush()
