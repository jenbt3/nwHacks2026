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

    # 2. Fetch the most recent past visit for temporal context
    visit_query = await db.execute(
        select(Visit)
        .where(Visit.visitor_id == visitor_id)
        .order_by(desc(Visit.timestamp))
        .limit(1)
    )
    last_visit = visit_query.scalars().first()

    try:
        # 3. Generate the empathetic script using Gemini
        # Updated to use 'relation' as per models.py
        script = await gemini_service.generate_whisper(
            name=visitor.name,
            relation=visitor.relation, 
            anchor=visitor.memory_anchor,
            last_visit=last_visit.timestamp if last_visit else None
        )

        # 4. Log THIS visit for future cooldown/context logic
        new_visit = Visit(visitor_id=visitor_id)
        db.add(new_visit)
        await db.commit()

        # 5. Stream the audio from ElevenLabs
        audio_stream = await speech_service.stream_whisper(script)
        
        if not audio_stream:
            raise HTTPException(status_code=500, detail="ElevenLabs failed to generate audio stream")

        return StreamingResponse(audio_stream, media_type="audio/mpeg")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Script generation error: {str(e)}")