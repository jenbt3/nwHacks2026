from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
# Assuming 'manager' is imported from your main WebSocket handler

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.post("/wandering")
async def report_wandering(background_tasks: BackgroundTasks):
    """Triggered by Pi when patient is near the exit during off-hours."""
    alert_payload = {
        "type": "WANDERING_DETECTED",
        "timestamp": datetime.now().isoformat(),
        "priority": "HIGH"
    }
    # Broadcast to all connected caregivers via WebSocket
    await manager.broadcast_alert(alert_payload)
    return {"status": "Alert sent"}