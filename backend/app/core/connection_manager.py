from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active: Dict[int, WebSocket] = {}

    async def connect(self, device_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active[device_id] = websocket

    def disconnect(self, device_id: int):
        self.active.pop(device_id, None)

    async def send_json_to_device(self, device_id: int, payload: dict) -> bool:
        ws = self.active.get(device_id)
        if not ws:
            return False
        await ws.send_json(payload)
        return True

# ✅ THIS is what your import expects
manager = ConnectionManager()
