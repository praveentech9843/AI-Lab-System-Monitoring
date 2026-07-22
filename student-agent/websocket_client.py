import asyncio
import json
import sys
import websockets
import config

class AgentWebSocketClient:
    def __init__(self, server_url=config.SERVER_URL):
        self.server_url = server_url
        self.connected = False
        self.running = False
        self.ws = None

    async def start(self):
        self.running = True
        await self._connect_loop()

    async def _connect_loop(self):
        while self.running:
            print("Connecting...")
            sys.stdout.flush()
            try:
                async with websockets.connect(self.server_url) as websocket:
                    self.ws = websocket
                    self.connected = True
                    print("Connected")
                    sys.stdout.flush()
                    
                    # Send registration message
                    print(f"Registering {config.SYSTEM_ID}")
                    sys.stdout.flush()
                    
                    register_payload = {
                        "type": "register",
                        "system_id": config.SYSTEM_ID,
                        "system_name": config.SYSTEM_NAME
                    }
                    await websocket.send(json.dumps(register_payload))
                    
                    # Loop to keep the connection open and receive any server responses
                    async for message in websocket:
                        pass
                        
            except (websockets.exceptions.ConnectionClosed, Exception) as e:
                self.connected = False
                self.ws = None
                if self.running:
                    # Auto reconnect after 5 seconds on connection loss/failure
                    await asyncio.sleep(5)

    async def send_message(self, data):
        """Send message over WebSocket if connected."""
        if self.ws and self.connected:
            try:
                await self.ws.send(json.dumps(data))
                return True
            except Exception:
                pass
        return False

    async def stop(self):
        self.running = False
        self.connected = False
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
