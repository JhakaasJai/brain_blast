"""
R2 — Social Connection Mode
Async message thread between a patient and their care team.
No real-time websockets in prototype — polling-based.
PRODUCTION: swap SOCIAL_MESSAGES for a DB table + FCM/SMS per send.
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.api.dependencies import get_current_user
from app.api.schemas import SocialMessageIn, SocialMessageOut
from app.models import SocialMessage, User, CaregiverLink, Notification
from app.core.crud import get_patients_for_user

router = APIRouter(tags=["social"])

def _add_notification(db: Session, target_user_id: str, message: str, channel: str = "in_app"):
    n = Notification(
        id=uuid.uuid4(),
        user_id=target_user_id,
        target_user_id=target_user_id,
        message=message,
        channel=channel,
        read=False,
        created_at=datetime.now(timezone.utc)
    )
    db.add(n)

@router.get("/patients/{patient_id}/messages", response_model=list[SocialMessageOut])
def list_messages(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
        
    messages = db.query(SocialMessage).filter(SocialMessage.patient_id == patient_id).order_by(SocialMessage.sent_at.asc()).all()
    
    # We need to map sender_name and sender_role for the response model
    result = []
    for m in messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        result.append({
            "id": str(m.id),
            "patient_id": str(m.patient_id),
            "sender_id": str(m.sender_id),
            "sender_name": sender.name if sender else "Unknown",
            "sender_role": sender.role if sender else "Unknown",
            "message_text": m.message_text,
            "sent_at": m.sent_at.isoformat() if hasattr(m.sent_at, 'isoformat') else m.sent_at,
        })
        
    return result

@router.post("/patients/{patient_id}/messages", response_model=SocialMessageOut, status_code=201)
def send_message(
    patient_id: str,
    body: SocialMessageIn,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["id"] != body.sender_id:
        raise HTTPException(status_code=403, detail="sender_id must match authenticated user")
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")

    sender = db.query(User).filter(User.id == current_user["id"]).first()
    
    msg = SocialMessage(
        id=uuid.uuid4(),
        patient_id=patient_id,
        sender_id=current_user["id"],
        message_text=body.message_text,
        sent_at=datetime.now(timezone.utc)
    )
    db.add(msg)

    # Simulate notification
    sender_name = sender.name if sender else ("your caregiver" if current_user["role"] != "patient" else "patient")
    if current_user["role"] == "patient":
        linked = db.query(CaregiverLink).filter(CaregiverLink.patient_id == patient_id, CaregiverLink.status == "active").all()
        for cg in linked:
            _add_notification(
                db=db,
                target_user_id=str(cg.caregiver_id),
                message=f"[SOCIAL] New message from {sender_name}: {body.message_text[:60]}",
                channel="in_app",
            )
    else:
        _add_notification(
            db=db,
            target_user_id=patient_id,
            message=f"[SOCIAL] Message from {sender_name}: {body.message_text[:60]}",
            channel="in_app",
        )

    db.commit()
    db.refresh(msg)
    
    return {
        "id": str(msg.id),
        "patient_id": str(msg.patient_id),
        "sender_id": str(msg.sender_id),
        "sender_name": sender.name if sender else "Unknown",
        "sender_role": current_user["role"],
        "message_text": msg.message_text,
        "sent_at": msg.sent_at.isoformat() if hasattr(msg.sent_at, 'isoformat') else msg.sent_at,
    }
