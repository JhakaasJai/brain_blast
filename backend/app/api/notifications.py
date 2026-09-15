"""
Notifications log endpoint — shows simulated push/SMS alerts in-app.
"""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.mock_data import NOTIFICATIONS_LOG, get_patients_for_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/")
def list_notifications(current_user: dict = Depends(get_current_user)):
    """Return in-app notifications for the current user (caregiver/hw/admin)."""
    uid = current_user["id"]
    role = current_user["role"]
    if role == "admin":
        return NOTIFICATIONS_LOG
    # caregivers/hw see notifications targeted at them
    return [n for n in NOTIFICATIONS_LOG if n.get("target_user_id") == uid]


@router.patch("/{notification_id}/read")
def mark_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    for n in NOTIFICATIONS_LOG:
        if n["id"] == notification_id:
            n["read"] = True
            return {"ok": True}
    return {"ok": False, "detail": "not found"}
