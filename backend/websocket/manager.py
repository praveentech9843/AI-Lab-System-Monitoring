"""
WebSocket Connection Manager Module.
Manages active WebSocket client connections and JSON message broadcasting.
"""
from typing import Any, Dict, List
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages active WebSocket connections and handles broadcasting JSON payloads to connected clients.
    """

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accepts an incoming WebSocket connection and registers it to active connections.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Safely removes a disconnected WebSocket from active connections.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        """
        Sends a JSON message payload to a single specific WebSocket connection.
        """
        await websocket.send_json(message)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcasts a JSON message payload to all active WebSocket connections safely.
        """
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


# Global instantiated manager object for application-wide broadcasting
manager = ConnectionManager()
