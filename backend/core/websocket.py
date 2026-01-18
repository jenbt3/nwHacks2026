import json
import logging
from fastapi import WebSocket

# Setup basic logging for debugging connection drops
logger = logging.getLogger("websocket")

class ConnectionManager:
    def __init__(self):
        # Using a set for O(1) removals and to prevent duplicate connections
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, message: dict):
        """Sends an alert to all active connections and cleans up dead ones."""
        message_json = json.dumps(message)
        
        # Iterate over a copy to allow safe removal during iteration
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.warning(f"WebSocket send failed: {e}. Removing connection.")
                self.disconnect(connection)

# Shared instance for the entire app
manager = ConnectionManager()