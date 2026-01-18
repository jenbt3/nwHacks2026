from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys (Loaded from .env)
    GEMINI_API_KEY: str
    ELEVENLABS_API_KEY: str
    
    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/bridge.db"
    
    # AI Personas
    VOICE_ID: str = "JBFqnCBsd6RMkjVDRZzb" # Warm/Empathic persona
    
    class Config:
        env_file = ".env"

settings = Settings()