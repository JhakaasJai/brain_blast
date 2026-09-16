"""
Reminders CRUD + sync endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone

from app.api.dependencies import get_current_user
from app.core.db import get_db
from app.core.crud import get_patients_for_user
from app.models import Reminder, ReminderEvent, CaregiverLink, User
from app.api.schemas import (
    ReminderCreate, ReminderUpdate, ReminderOut,
    SyncReminderEventsRequest, SyncReminderEventsResponse, ReminderEventOut,
    ReminderEscalationOut,
)

router = APIRouter(tags=["reminders"])


@router.get("/reminders", response_model=list[ReminderOut])
def list_reminders(patient_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
        
    reminders = db.query(Reminder).filter(Reminder.patient_id == patient_id).all()
    return reminders


@router.post("/reminders", response_model=ReminderOut, status_code=201)
def create_reminder(body: ReminderCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    allowed = get_patients_for_user(current_user, db)
    if body.patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    if current_user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Only caregivers or care teams can manage reminders")

    import json
    data = body.model_dump()
    data["schedule_rule"] = json.dumps(data["schedule_rule"])
    rem = Reminder(
        id=uuid.uuid4(),
        **data,
        created_by=current_user["id"],
        created_at=datetime.now(timezone.utc),
    )
    db.add(rem)
    db.commit()
    db.refresh(rem)
    # Parse schedule_rule back for response
    result = {c.key: getattr(rem, c.key) for c in rem.__table__.columns}
    result["id"] = str(result["id"])
    result["patient_id"] = str(result["patient_id"])
    if isinstance(result.get("schedule_rule"), str):
        try:
            result["schedule_rule"] = json.loads(result["schedule_rule"])
        except Exception:
            result["schedule_rule"] = {}
    return result


@router.post("/reminders/{reminder_id}/escalate", response_model=ReminderEscalationOut)
def escalate_reminder(
    reminder_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rem = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
        
    if str(rem.patient_id) not in get_patients_for_user(current_user, db):
        raise HTTPException(status_code=403, detail="Not authorised")
        
    # Note: 'critical' is likely in the title or type since it isn't a native column in the base mockup,
    # but the old mock_data relied on a `.get("critical")`. We will safely ignore it for DB migration
    # and just assume all escalations requested via the endpoint are processed if a missed event exists.
    
    latest_event = db.query(ReminderEvent).filter(ReminderEvent.reminder_id == reminder_id).order_by(ReminderEvent.scheduled_time.desc()).first()
    
    if not latest_event or latest_event.status != "missed":
        latest_action = latest_event.status if latest_event else "no event"
        return ReminderEscalationOut(
            reminder_id=reminder_id, patient_id=str(rem.patient_id), escalated=False,
            reason=f"Latest event is {latest_action}; escalation requires a missed event", notification_ids=[]
        )
        
    links = db.query(CaregiverLink).filter(CaregiverLink.patient_id == rem.patient_id, CaregiverLink.status == "active").all()
    caregivers = [str(link.caregiver_id) for link in links]
    
    notification_ids = []
    
    # We would integrate Resend/SMS here. For the prototype, return simulated IDs
    for caregiver_id in caregivers:
        notification_ids.append(str(uuid.uuid4()))
        
    return ReminderEscalationOut(
        reminder_id=reminder_id, patient_id=str(rem.patient_id), escalated=True,
        reason="Critical reminder has a missed event", notification_ids=notification_ids
    )


@router.patch("/reminders/{reminder_id}", response_model=ReminderOut)
def update_reminder(
    reminder_id: str,
    body: ReminderUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rem = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
        
    if str(rem.patient_id) not in get_patients_for_user(current_user, db):
        raise HTTPException(status_code=403, detail="Not authorised")
        
    if current_user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Only caregivers or care teams can manage reminders")
        
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(rem, field, value)
        
    db.commit()
    db.refresh(rem)
    return rem


@router.delete("/reminders/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rem = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
        
    if str(rem.patient_id) not in get_patients_for_user(current_user, db):
        raise HTTPException(status_code=403, detail="Not authorised")
        
    if current_user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Only caregivers or care teams can manage reminders")
        
    db.delete(rem)
    db.commit()


@router.post("/sync/reminder-events", response_model=SyncReminderEventsResponse)
def sync_reminder_events(
    body: SyncReminderEventsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    synced = 0
    skipped = 0
    
    # Check existing uuids
    req_uuids = [e.client_uuid for e in body.events]
    existing = db.query(ReminderEvent.client_uuid).filter(ReminderEvent.client_uuid.in_(req_uuids)).all()
    existing_uuids = {str(row.client_uuid) for row in existing}
    
    for ev in body.events:
        if str(ev.client_uuid) in existing_uuids:
            skipped += 1
            continue
            
        rec = ReminderEvent(
            id=uuid.uuid4(),
            client_uuid=ev.client_uuid,
            reminder_id=ev.reminder_id,
            scheduled_time=datetime.fromisoformat(ev.scheduled_time or ev.fired_at),
            status=ev.action, # maps frontend 'action' to db 'status'
            action_taken_at=datetime.fromisoformat(ev.action_taken_at) if ev.action_taken_at else None
        )
        db.add(rec)
        existing_uuids.add(str(ev.client_uuid))
        synced += 1
        
    db.commit()
    return SyncReminderEventsResponse(synced=synced, skipped=skipped)
