import logging
from elevenlabs.client import AsyncElevenLabs
from backend.core.config import settings

# Setup logging for production-grade error tracking
logger = logging.getLogger("speech_service")

class SpeechService:
    def __init__(self):
        # Use centralized settings from config.py
        self.client = AsyncElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        self.voice_id = settings.VOICE_ID
        self.model_id = "eleven_flash_v2_5"

    async def stream_whisper(self, text: str):
        """
        Converts text to speech and returns an async byte stream.
        Optimized for <100ms time-to-first-byte.
        """
        try:
            audio_stream = await self.client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                # Force specific format to reduce Pi-side decoding overhead
                output_format="mp3_44100_128",
                # 1 = Max speed, 4 = Max quality. 1 is required for the 2.0s target.
                optimize_streaming_latency=1 
            )
            return audio_stream
            
        except Exception as e:
            logger.error(f"ElevenLabs API Failure: {e}")
            return None

# Single instance for the app
speech_service = SpeechService()