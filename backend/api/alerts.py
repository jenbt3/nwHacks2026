from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
from backend.core.websocket import manager
from backend.core.constants import OFF_HOURS_START, OFF_HOURS_END
from pydantic import BaseModel

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# Schema for incoming detection data from the Pi
class DetectionPayload(BaseModel):
    name: str
    relationship_type: str # Matches our updated models.py

def is_off_hours():
    """Helper to check if the current time falls within wandering risk hours."""
    now = datetime.now().hour
    if OFF_HOURS_START > OFF_HOURS_END:
        return now >= OFF_HOURS_START or now < OFF_HOURS_END
    return OFF_HOURS_START <= now < OFF_HOURS_END

@router.post("/wandering")
async def report_wandering():
    """Triggered by Pi when patient is near the exit (Ultrasound/PIR)."""
    is_critical = is_off_hours()
    
    alert_payload = {
        "type": "WANDERING_DETECTED",
        "timestamp": datetime.now().isoformat(),
        "priority": "HIGH" if is_critical else "INFO",
        "message": "URGENT: Patient near exit" if is_critical else "Movement near door"
    }

    await manager.broadcast_alert(alert_payload)
    return {"status": "Wandering alert processed", "critical": is_critical}

@router.post("/detection")
async def report_detection(payload: DetectionPayload):
    """Triggered by Pi when a face is recognized."""
    
    detection_payload = {
        "type": "DETECTION",
        "name": payload.name,
        "relationship_type": payload.relationship_type,
        "timestamp": datetime.now().isoformat()
    }

    # This updates the 'Visitor Memory Log' on the dashboard
    await manager.broadcast_alert(detection_payload)
    
    return {"status": "Detection logged", "visitor": payload.name}