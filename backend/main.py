# --- FULL main.py ---
import json
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from backend.core.websocket import manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace with your Raspberry Pi's actual IP
PI_MOTOR_URL = "http://192.168.137.38:8000/motor"

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get("type") == "CAMERA_CONTROL":
                # Forwarding joystick data to the Pi
                await run_in_threadpool(
                    requests.post, 
                    PI_MOTOR_URL, 
                    json=data, 
                    timeout=0.1
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root(): return {"status": "online"}