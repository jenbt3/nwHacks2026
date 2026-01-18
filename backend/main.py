import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.core.websocket import manager 
from backend.api import people, alerts, scripts
from backend.db.database import engine, Base

# Setup basic logging to monitor the bridge's health
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bridge_main")

app = FastAPI(title="Cognitive Bridge API", version="1.0.0")

# 1. Security: Enable CORS so your Dashboard can talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows connections from any origin for the hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Initialization: Auto-create database tables on startup
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # This creates visitors and visits tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized and tables verified.")

# 3. Routes: Include all core service modules
app.include_router(people.router)
app.include_router(alerts.router)
app.include_router(scripts.router) # Essential for AI scripts and audio

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time bridge for wandering alerts and detection logs."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text() 
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Caregiver dashboard disconnected.")

@app.get("/")
async def root():
    return {
        "status": "online",
        "project": "Cognitive Bridge",
        "version": "1.0.0",
        "message": "System Ready for NW Hacks 2026"
    }
@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()
    logger.info("Database connections closed. Goodbye.")