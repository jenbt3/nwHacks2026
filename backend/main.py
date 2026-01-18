import logging
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.core.websocket import manager 
from backend.api import people, alerts, scripts
from backend.db.database import engine, Base
# Import the motor_bridge instance
from backend.motor_controller_integration.motor_controller import motor_bridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bridge_main")

app = FastAPI(title="Cognitive Bridge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized and tables verified.")

@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()
    logger.info("Database connections closed. Goodbye.")

app.include_router(people.router)
app.include_router(alerts.router)
app.include_router(scripts.router)

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time bridge for alerts, logs, and camera motor control."""
    await manager.connect(websocket)
    try:
        while True:
            # We now listen for JSON data (joystick movements)
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            
            if data.get("type") == "CAMERA_CONTROL":
                angle = data.get("direction", 0)
                force = data.get("distance", 0)
                
                # Relay to the motor bridge (Hardware Serial)
                motor_bridge.process_joystick(angle, force)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Caregiver dashboard disconnected.")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")

@app.get("/")
async def root():
    return {"status": "online", "project": "Cognitive Bridge"}