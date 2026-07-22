import asyncio
import json
import sys
import websockets
import config
from message_builder import build_message

class WebSocketClient:
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.running = False
        self.lock = asyncio.Lock()

    async def connect(self):
        """Main connection loop that manages connection and reconnection."""
        self.running = True
        while self.running:
            try:
                print(f"Connecting to {config.SERVER_URL}...")
                sys.stdout.flush()
                
                self.websocket = await websockets.connect(config.SERVER_URL)
                self.connected = True
                
                print("Connected to server")
                sys.stdout.flush()
                
                await self.register()
                await self.receive()
            except Exception as e:
                print(f"Connection Lost: {e}")
                sys.stdout.flush()
                self.connected = False
                self.websocket = None
                
                if self.running:
                    print("Reconnecting in 5 seconds...")
                    sys.stdout.flush()
                    await asyncio.sleep(5)

    async def register(self):
        """Sends the initial registration payload to the server."""
        message = build_message(msg_type="register")
        await self.send(message)
        
        print("Register Message Sent")
        sys.stdout.flush()

    async def send(self, message: dict):
        """Thread-safe and async-safe send wrapper."""
        if self.connected and self.websocket:
            async with self.lock:
                try:
                    await self.websocket.send(json.dumps(message))
                except Exception:
                    pass

    async def receive(self):
        """Asynchronously listens for incoming server messages."""
        async for message in self.websocket:
            try:
                payload = json.loads(message)
                if payload.get("event") == "COMMAND_TRIGGERED":
                    cmd_data = payload.get("data", {}) or {}
                    # SYSTEM_01 -> PC-01, SYSTEM_02 -> PC-02 etc.
                    cfg_comp_id = config.SYSTEM_ID.replace("SYSTEM_", "PC-")
                    tgt_comp_id = cmd_data.get("computer_id")
                    
                    if tgt_comp_id == cfg_comp_id or tgt_comp_id == config.SYSTEM_ID:
                        command = cmd_data.get("command", "").lower()
                        print(f"Received admin action command: {command}")
                        sys.stdout.flush()
                        self.execute_command(command)
            except Exception as e:
                print(f"Error handling incoming message: {e}")
                sys.stdout.flush()

    def execute_command(self, command: str):
        if command == "lock":
            print("EXECUTE: Lock workstation.")
            sys.stdout.flush()
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.user32.LockWorkStation()
        elif command == "logout":
            print("EXECUTE: Force logout.")
            sys.stdout.flush()
            sys.exit(0)

    async def reconnect(self):
        """Forces a reconnect by closing the active websocket."""
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass

    async def stop(self):
        """Stops the client loop and closes the connection cleanly."""
        self.running = False
        self.connected = False
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass
            self.websocket = None

