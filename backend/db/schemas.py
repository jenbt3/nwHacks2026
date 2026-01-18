from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VisitorBase(BaseModel):
    name: str
    relationship: str
    memory_anchor: Optional[str] = None

class VisitorCreate(VisitorBase):
    encoding: bytes  # This will be sent as a base64 string and decoded

class VisitorResponse(VisitorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class VisitLog(BaseModel):
    visitor_id: int
    timestamp: datetime