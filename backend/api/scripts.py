from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db
from backend.services.gemini import gemini_service
from backend.services.elevenlabs import speech_service

router = APIRouter(prefix="/scripts", tags=["Scripts"])

@router.get("/generate/{visitor_id}")
async def generate_and_stream(visitor_id: int, db: AsyncSession = Depends(get_db)):
    """Fetches visitor data, generates an empathetic script, and returns audio."""
    # Logic from main.py orchestrator goes here to keep main.py clean
    # ... (Fetch visitor, generate Gemini script, call ElevenLabs)
    script = await gemini_service.generate_whisper(...) 
    audio_stream = await speech_service.stream_whisper(script)
    return StreamingResponse(audio_stream, media_type="audio/mpeg")