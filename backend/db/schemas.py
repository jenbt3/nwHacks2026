from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class VisitorBase(BaseModel):
    name: str
    relationship_type: str # Updated name
    memory_anchor: Optional[str] = None

class VisitorCreate(VisitorBase):
    encoding: bytes  

class VisitorResponse(VisitorBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class VisitorSyncResponse(VisitorResponse):
    encoding: bytes

class VisitLog(BaseModel):
    visitor_id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)