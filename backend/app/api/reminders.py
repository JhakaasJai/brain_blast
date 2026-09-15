"""
Reminders CRUD + sync endpoints.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.schemas import (
    ReminderCreate, ReminderUpdate, ReminderOut,
    SyncReminderEventsRequest, SyncReminderEventsResponse, ReminderEventOut,
    ReminderEscalationOut,
)
from app.mock_data import (
    REMINDERS, REMINDERS_BY_ID, REMINDER_EVENTS, CAREGIVER_LINKS,
    get_patients_for_user,
)

router = APIRouter(tags=["reminders"])


@router.get("/reminders", response_model=list[ReminderOut])
def list_reminders(patient_id: str, current_user: dict = Depends(get_current_user)):
    allowed = get_patients_for_user(current_user)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    return [r for r in REMINDERS if r["patient_id"] == patient_id]


@router.post("/reminders", response_model=ReminderOut, status_code=201)
def create_reminder(body: ReminderCreate, current_user: dict = Depends(get_current_user)):
    allowed = get_patients_for_user(current_user)
    if body.patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    if current_user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Only caregivers or care teams can manage reminders")
    rem = {"id": str(uuid.uuid4()), **body.model_dump()}
    REMINDERS.append(rem)
    REMINDERS_BY_ID[rem["id"]] = rem
    return rem


@router.post("/reminders/{reminder_id}/escalate", response_model=ReminderEscalationOut)
def escalate_reminder(
    reminder_id: str,
    current_user: dict = Depends(get_current_user),
):
    rem = REMINDERS_BY_ID.get(reminder_id)
    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if rem["patient_id"] not in get_patients_for_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorised")
    if not rem.get("critical", False):
        return ReminderEscalationOut(
            reminder_id=reminder_id, patient_id=rem["patient_id"], escalated=False,
            reason="Reminder is not marked critical", notification_ids=[]
        )
    recent = [event for event in REMINDER_EVENTS if event["reminder_id"] == reminder_id]
    latest = max(recent, key=lambda event: event["fired_at"], default=None)
    if not latest or latest["action"] != "missed":
        latest_action = latest["action"] if latest else "no event"
        return ReminderEscalationOut(
            reminder_id=reminder_id, patient_id=rem["patient_id"], escalated=False,
            reason=f"Latest event is {latest_action}; escalation requires a missed event", notification_ids=[]
        )
    caregivers = [link["caregiver_id"] for link in CAREGIVER_LINKS
                  if link["patient_id"] == rem["patient_id"] and link["status"] == "active"]
    from app.mock_data import add_notification
    notification_ids = []
    for caregiver_id in caregivers:
        notification = add_notification(
            caregiver_id, rem["patient_id"],
            f"[SMS SIMULATION] Critical reminder missed: {rem['message']}", channel="sms"
        )
        notification_ids.append(notification["id"])
    return ReminderEscalationOut(
        reminder_id=reminder_id, patient_id=rem["patient_id"], escalated=True,
        reason="Critical reminder has a missed event", notification_ids=notification_ids
    )


@router.patch("/reminders/{reminder_id}", response_model=ReminderOut)
def update_reminder(
    reminder_id: str,
    body: ReminderUpdate,
    current_user: dict = Depends(get_current_user),
):
    rem = REMINDERS_BY_ID.get(reminder_id)
    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if rem["patient_id"] not in get_patients_for_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorised")
    if current_user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Only caregivers or care teams can manage reminders")
    for field, value in body.model_dump(exclude_none=True).items():
        rem[field] = value
    return rem


@router.delete("/reminders/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: str,
    current_user: dict = Depends(get_current_user),
):
    rem = REMINDERS_BY_ID.get(reminder_id)
    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if rem["patient_id"] not in get_patients_for_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorised")
    if current_user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Only caregivers or care teams can manage reminders")
    REMINDERS.remove(rem)
    del REMINDERS_BY_ID[reminder_id]


@router.post("/sync/reminder-events", response_model=SyncReminderEventsResponse)
def sync_reminder_events(
    body: SyncReminderEventsRequest,
    current_user: dict = Depends(get_current_user),
):
    synced = 0
    skipped = 0
    existing_uuids = {e["client_uuid"] for e in REMINDER_EVENTS}
    for ev in body.events:
        if ev.client_uuid in existing_uuids:
            skipped += 1
            continue
        REMINDER_EVENTS.append({
            "id": str(uuid.uuid4()),
            **ev.model_dump(),
            "sync_status": "synced",
        })
        synced += 1
    return SyncReminderEventsResponse(synced=synced, skipped=skipped)
