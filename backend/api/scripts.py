from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.db.database import get_db
from backend.db.models import Visitor, Visit
from backend.services.gemini import gemini_service
from backend.services.elevenlabs import speech_service

router = APIRouter(prefix="/scripts", tags=["Scripts"])

@router.get("/generate/{visitor_id}")
async def generate_and_stream(visitor_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Fetch Visitor details
    result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
    visitor = result.scalars().first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    # 2. Fetch the most recent past visit for context
    visit_query = await db.execute(
        select(Visit)
        .where(Visit.visitor_id == visitor_id)
        .order_by(desc(Visit.timestamp))
        .limit(1)
    )
    last_visit = visit_query.scalars().first()

    # 3. Generate the empathetic script using Gemini
    script = await gemini_service.generate_whisper(
        name=visitor.name,
        relationship=visitor.relationship,
        anchor=visitor.memory_anchor,
        last_visit=last_visit.timestamp if last_visit else None
    )

    # 4. Log THIS visit so the cooldown logic works next time
    new_visit = Visit(visitor_id=visitor_id)
    db.add(new_visit)
    await db.commit()

    # 5. Stream the audio from ElevenLabs
    audio_stream = await speech_service.stream_whisper(script)
    if not audio_stream:
        raise HTTPException(status_code=500, detail="Audio generation failed")

    return StreamingResponse(audio_stream, media_type="audio/mpeg")