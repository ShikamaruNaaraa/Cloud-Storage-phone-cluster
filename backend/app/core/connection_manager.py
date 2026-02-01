
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # Maps device_id -> WebSocket
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, device_id: int, websocket: WebSocket):
        self.active_connections[device_id] = websocket

    def disconnect(self, device_id: int):
        self.active_connections.pop(device_id, None)

    async def send_command(self, device_id: int, command_type: str, data: dict):
        if device_id in self.active_connections:
            ws = self.active_connections[device_id]
            await ws.send_json({
                "type": command_type,
                "payload": data
            })
            return True
        return False

manager = ConnectionManager()