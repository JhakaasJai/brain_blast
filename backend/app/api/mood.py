"""
R4 — Sleep and Mood Check-ins
Patients record daily mood (1-5) and sleep quality/hours.
Caregivers and health workers see the check-in history.
PRODUCTION: enforce one check-in per patient per day at the DB level.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.schemas import MoodCheckinIn, MoodCheckinOut
from app.mock_data import MOOD_CHECKINS, get_patients_for_user

router = APIRouter(tags=["mood"])


@router.get("/patients/{patient_id}/mood-checkins",
            response_model=list[MoodCheckinOut])
def list_mood_checkins(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
):
    allowed = get_patients_for_user(current_user)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    return sorted(
        [c for c in MOOD_CHECKINS if c["patient_id"] == patient_id],
        key=lambda c: c["recorded_at"],
    )


@router.post("/patients/{patient_id}/mood-checkins",
             response_model=MoodCheckinOut, status_code=201)
def create_mood_checkin(
    patient_id: str,
    body: MoodCheckinIn,
    current_user: dict = Depends(get_current_user),
):
    # Patients can only record their own check-ins
    if current_user["role"] == "patient" and current_user["id"] != patient_id:
        raise HTTPException(status_code=403, detail="Can only record your own check-in")
    allowed = get_patients_for_user(current_user)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    if not (1 <= body.mood_score <= 5):
        raise HTTPException(status_code=422, detail="mood_score must be 1–5")
    if body.sleep_quality and body.sleep_quality not in ("poor", "fair", "good"):
        raise HTTPException(status_code=422, detail="sleep_quality must be poor, fair, or good")
    entry = {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "mood_score": body.mood_score,
        "sleep_hours": body.sleep_hours,
        "sleep_quality": body.sleep_quality,
        "notes": body.notes,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    MOOD_CHECKINS.append(entry)
    return entry
