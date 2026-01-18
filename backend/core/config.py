from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # API Keys (Loaded from .env)
    GEMINI_API_KEY: str = Field(..., min_length=10)
    ELEVENLABS_API_KEY: str = Field(..., min_length=10)
    
    # AI Personas
    VOICE_ID: str = "JBFqnCBsd6RMkjVDRZzb"
    
    # Pydantic V2 style config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()