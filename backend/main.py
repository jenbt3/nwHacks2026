from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import cv2


from .db.database import engine, Base, get_db
from .db.models import Visitor, Visit
from .services.gemini import gemini_service
from .services.elevenlabs import speech_service
from .core.websocket import manager # Correct import
from .api import people, alerts, scripts # Import routers
from .camera.pi_backend import generate_frames 

app = FastAPI(title="Cognitive Bridge API")

# Include Modular Routers
app.include_router(people.router)
app.include_router(alerts.router)
app.include_router(scripts.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/detect/{visitor_id}")
async def handle_detection(visitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
    visitor = result.scalars().first()
    
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    # Fetch last visit before logging new one
    last_visit_result = await db.execute(
        select(Visit.timestamp)
        .where(Visit.visitor_id == visitor_id)
        .order_by(Visit.timestamp.desc())
        .limit(1)
    )
    last_visit_timestamp = last_visit_result.scalars().first()

    # Log new visit
    new_visit = Visit(visitor_id=visitor.id)
    db.add(new_visit)
    await db.commit()

    # FIX: Pass the timestamp to Gemini
    script = await gemini_service.generate_whisper(
        name=visitor.name,
        relationship=visitor.relationship,
        anchor=visitor.memory_anchor,
        last_visit=last_visit_timestamp # Mapped correctly now
    )

    audio_stream = await speech_service.stream_whisper(script)
    return StreamingResponse(audio_stream, media_type="audio/mpeg")


@app.get("/video")
async def video():
    """Video streaming endpoint"""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )