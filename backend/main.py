from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# Change relative (.) to absolute (backend.)
from backend.core.websocket import manager 
from backend.api import people, alerts

app = FastAPI()

# Include routers
app.include_router(people.router)
app.include_router(alerts.router)

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() 
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "nwHacks 2026 Bridge API is Online"}