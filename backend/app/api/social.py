"""
R2 — Social Connection Mode
Async message thread between a patient and their care team.
No real-time websockets in prototype — polling-based.
PRODUCTION: swap SOCIAL_MESSAGES for a DB table + FCM/SMS per send.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.schemas import SocialMessageIn, SocialMessageOut
from app.mock_data import (
    SOCIAL_MESSAGES,
    USERS_BY_ID,
    get_patients_for_user,
    add_notification,
    CAREGIVER_LINKS,
)

router = APIRouter(tags=["social"])


@router.get("/patients/{patient_id}/messages",
            response_model=list[SocialMessageOut])
def list_messages(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
):
    allowed = get_patients_for_user(current_user)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    msgs = [m for m in SOCIAL_MESSAGES if m["patient_id"] == patient_id]
    # Return chronological order
    return sorted(msgs, key=lambda m: m["sent_at"])


@router.post("/patients/{patient_id}/messages",
             response_model=SocialMessageOut, status_code=201)
def send_message(
    patient_id: str,
    body: SocialMessageIn,
    current_user: dict = Depends(get_current_user),
):
    # Sender must be themselves
    if current_user["id"] != body.sender_id:
        raise HTTPException(status_code=403, detail="sender_id must match authenticated user")
    allowed = get_patients_for_user(current_user)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")

    sender = USERS_BY_ID.get(current_user["id"], {})
    msg = {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "sender_id": current_user["id"],
        "sender_name": sender.get("name", "Unknown"),
        "sender_role": current_user["role"],
        "message_text": body.message_text,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    SOCIAL_MESSAGES.append(msg)

    # Simulate notification to the other party
    # If patient sent, notify all linked caregivers; if caregiver sent, notify patient
    if current_user["role"] == "patient":
        linked = [lk["caregiver_id"] for lk in CAREGIVER_LINKS
                  if lk["patient_id"] == patient_id and lk["status"] == "active"]
        for cg_id in linked:
            add_notification(
                target_user_id=cg_id,
                patient_id=patient_id,
                message=f"[SOCIAL] New message from {sender.get('name','patient')}: {body.message_text[:60]}",
                channel="in_app",
            )
    else:
        add_notification(
            target_user_id=patient_id,
            patient_id=patient_id,
            message=f"[SOCIAL] Message from {sender.get('name','your caregiver')}: {body.message_text[:60]}",
            channel="in_app",
        )

    return msg
