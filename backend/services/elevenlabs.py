import os
import asyncio
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import stream

# Load API Key
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = AsyncElevenLabs(api_key=ELEVENLABS_API_KEY)

# Use 'Flash v2.5' for ultra-low latency (~75ms model time)
DEFAULT_MODEL = "eleven_flash_v2_5"

# Choose a "Warm/Empathic" Voice ID (e.g., 'George' or a custom cloned voice)
# You can find these IDs in the ElevenLabs Voice Lab
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb" 

class SpeechService:
    def __init__(self):
        self.client = client

    async def stream_whisper(self, text: str):
        """
        Converts text to speech and streams it to the Pi's audio output.
        In a hackathon setup, the backend generates the stream and 
        the Pi's 'client.py' consumes the bytes for playback.
        """
        try:
            # Generate the audio stream
            audio_stream = await self.client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=DEFAULT_VOICE_ID,
                model_id=DEFAULT_MODEL,
                # Optimize for latency: 1 = max speed, 4 = max quality
                optimize_streaming_latency=1 
            )
            
            # This returns an async generator of audio bytes
            return audio_stream
        except Exception as e:
            print(f"ElevenLabs Streaming Error: {e}")
            return None

# Initialize singleton
speech_service = SpeechService()