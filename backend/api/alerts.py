from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
from backend.core.websocket import manager
from backend.core.constants import OFF_HOURS_START, OFF_HOURS_END

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def is_off_hours():
    """Helper to check if the current time falls within wandering risk hours."""
    now = datetime.now().hour
    # Handles wrap-around (e.g., 10 PM to 6 AM)
    if OFF_HOURS_START > OFF_HOURS_END:
        return now >= OFF_HOURS_START or now < OFF_HOURS_END
    return OFF_HOURS_START <= now < OFF_HOURS_END

@router.post("/wandering")
async def report_wandering():
    """Triggered by Pi when patient is near the exit."""
    
    # Only treat as HIGH priority if it's during off-hours
    is_critical = is_off_hours()
    
    alert_payload = {
        "type": "WANDERING_DETECTED",
        "timestamp": datetime.now().isoformat(),
        "priority": "HIGH" if is_critical else "INFO",
        "message": "Patient near exit" if is_critical else "Movement near door"
    }

    # Broadcast to all connected caregivers
    await manager.broadcast_alert(alert_payload)
    
    return {"status": "Alert processed", "critical": is_critical}