# --- FULL main.py ---
import logging
import json
import requests
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

from backend.core.websocket import manager 
from backend.api import people, alerts, scripts
from backend.db.database import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bridge_main")

# CONFIG: The IP of your Raspberry Pi
PI_NODE_URL = "http://192.168.x.x:8000/motor" 

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Cognitive Bridge API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(people.router)
app.include_router(alerts.router)
app.include_router(scripts.router)

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            if message == "ping": continue
            
            try:
                data = json.loads(message)
                if data.get("type") == "CAMERA_CONTROL":
                    # FORWARD TO PI: Non-blocking threadpool call
                    await run_in_threadpool(
                        requests.post, 
                        PI_NODE_URL, 
                        json=data, 
                        timeout=0.1
                    )
            except: pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)