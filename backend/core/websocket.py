import json
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Using a list is fine for small scale, but consider a set() 
        # for faster removals if you expect 100+ concurrent caregivers.
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, message: dict):
        """Sends an alert to all active connections and cleans up dead ones."""
        message_json = json.dumps(message)
        
        # We iterate over a copy [:] so we can safely remove items during the loop
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message_json)
            except Exception:
                # If sending fails, the connection is dead; remove it.
                self.disconnect(connection)

# Shared instance for the entire app
manager = ConnectionManager()