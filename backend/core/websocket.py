# --- FULL websocket.py ---
import json
import logging
from fastapi import WebSocket

logger = logging.getLogger("websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, message: dict):
        message_json = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message_json)
            except:
                self.disconnect(connection)

manager = ConnectionManager()