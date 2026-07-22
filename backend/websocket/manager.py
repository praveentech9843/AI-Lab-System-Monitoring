"""
Optimized WebSocket Connection Manager Module.
- Parallel async broadcasts using asyncio.gather()
- Connection state validation before send
- Dead connection pruning on write failure
"""
import asyncio
from typing import Any, Dict, List
from fastapi import WebSocket
from starlette.websockets import WebSocketState


class ConnectionManager:
    """
    Manages active WebSocket connections and broadcasts JSON payloads concurrently.
    """

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        if websocket.client_state != WebSocketState.CONNECTED:
            self.disconnect(websocket)
            return
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcasts to all connected clients concurrently using asyncio.gather().
        Dead connections are pruned after the batch completes.
        """
        if not self.active_connections:
            return

        # Filter to only connected sockets before gather
        live = [c for c in self.active_connections if c.client_state == WebSocketState.CONNECTED]
        dead = [c for c in self.active_connections if c.client_state != WebSocketState.CONNECTED]
        for c in dead:
            self.disconnect(c)

        if not live:
            return

        async def _send(conn: WebSocket):
            try:
                await conn.send_json(message)
            except Exception:
                self.disconnect(conn)

        await asyncio.gather(*[_send(c) for c in live], return_exceptions=True)


# Global manager instance
manager = ConnectionManager()
