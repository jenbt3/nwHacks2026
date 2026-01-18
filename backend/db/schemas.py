from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
import base64

class VisitorBase(BaseModel):
    name: str
    relation: str # Matches the updated models.py
    memory_anchor: Optional[str] = None

class VisitorCreate(VisitorBase):
    # Incoming data from frontend/seed script is a Base64 string
    encoding: str 

    @field_validator('encoding')
    @classmethod
    def decode_encoding(cls, v: str) -> bytes:
        """Converts Base64 string to raw bytes for LargeBinary storage."""
        try:
            # If it's a data URI (from main.js), strip the prefix
            if "," in v:
                v = v.split(",")[1]
            return base64.b64decode(v)
        except Exception:
            raise ValueError("Invalid base64 encoding for face vector.")

class VisitorResponse(VisitorBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class VisitorSyncResponse(VisitorResponse):
    # Outgoing data for the Pi must be converted back to a string
    encoding: str

    @classmethod
    def model_validate(cls, obj):
        """Custom validation to ensure bytes are converted to Base64 for the Pi."""
        data = super().model_validate(obj)
        if isinstance(obj.encoding, bytes):
            data.encoding = base64.b64encode(obj.encoding).decode('utf-8')
        return data

class VisitLog(BaseModel):
    visitor_id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)