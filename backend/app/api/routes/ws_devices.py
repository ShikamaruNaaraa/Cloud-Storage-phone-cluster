from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()  # singleton in this module

@router.websocket("/ws/devices/{device_id}")
async def device_ws(websocket: WebSocket, device_id: int):
    await manager.connect(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # You can handle ACK messages etc here too if you want
            # print("WS from device:", device_id, data)
    except WebSocketDisconnect:
        manager.disconnect(device_id)
