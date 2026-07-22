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
                await self.receive_messages()

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
