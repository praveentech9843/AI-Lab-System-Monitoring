"""
WebSocket REST/Streaming Router Module.
Exposes WebSocket endpoints for real-time live desktop streaming and event notifications.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from websocket.manager import manager

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket) -> None:
    """
    Live WebSocket endpoint for desktop stream frames and real-time broadcasting.
    Accepts connection, registers to ConnectionManager, converts messages to structured JSON, and broadcasts.
    Always safely disconnects inside a finally block.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = {
                "event": "LIVE_MESSAGE",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "message": data
                }
            }
            await manager.broadcast(payload)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
