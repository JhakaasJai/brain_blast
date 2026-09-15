"""
Notifications log endpoint — shows simulated push/SMS alerts in-app.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db

from app.api.dependencies import get_current_user
from app.models import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/")
def list_notifications(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return in-app notifications for the current user (caregiver/hw/admin)."""
    uid = current_user["id"]
    role = current_user["role"]
    if role == "admin":
        return db.query(Notification).order_by(Notification.created_at.desc()).all()
    # caregivers/hw see notifications targeted at them
    return db.query(Notification).filter(Notification.target_user_id == uid).order_by(Notification.created_at.desc()).all()


@router.patch("/{notification_id}/read")
def mark_read(notification_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.read = True
        db.commit()
        return {"ok": True}
    return {"ok": False, "detail": "not found"}
