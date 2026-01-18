import logging
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

from backend.core.websocket import manager 
from backend.api import people, alerts, scripts
from backend.db.database import engine, Base
from backend.motor_controller_integration.motor_controller import motor_bridge

# Setup centralized logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bridge_main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events (SQLAlchemy 2.0+ pattern)."""
    # Startup: Initialize DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized and tables verified.")
    
    yield
    
    # Shutdown: Clean up connections
    await engine.dispose()
    logger.info("Database connections closed. Goodbye.")

app = FastAPI(
    title="Cognitive Bridge API", 
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(people.router)
app.include_router(alerts.router)
app.include_router(scripts.router)

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time bridge for alerts and non-blocking motor control."""
    await manager.connect(websocket)
    try:
        while True:
            # Handle incoming JSON from main.js joystick
            message = await websocket.receive_text()
            
            # Simple keep-alive check
            if message == "ping":
                await websocket.send_text("pong")
                continue

            try:
                data = json.loads(message)
                
                if data.get("type") == "CAMERA_CONTROL":
                    angle = data.get("direction", 0)
                    force = data.get("distance", 0)
                    
                    # Offload blocking serial I/O to a threadpool to keep WS loop fast
                    await run_in_threadpool(motor_bridge.process_joystick, angle, force)

            except json.JSONDecodeError:
                pass # Ignore malformed keep-alives
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Caregiver dashboard disconnected.")
    except Exception as e:
        logger.error(f"WebSocket Loop Error: {e}")

@app.get("/")
async def root():
    return {"status": "online", "project": "Cognitive Bridge"}