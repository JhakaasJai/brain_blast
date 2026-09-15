"""R12 caregiver wellbeing check-ins."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.db import get_db
from app.models import CaregiverWellbeing
from app.api.schemas import CaregiverWellbeingIn, CaregiverWellbeingOut

router = APIRouter(tags=["caregiver wellbeing"])

def require_care_team_user(user: dict) -> None:
    if user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Care-team access required")

def validate_scores(body: CaregiverWellbeingIn) -> None:
    if not 1 <= body.energy_score <= 5:
        raise HTTPException(status_code=422, detail="energy_score must be 1–5")
    if not 1 <= body.stress_score <= 5:
        raise HTTPException(status_code=422, detail="stress_score must be 1–5")

@router.get("/caregiver-wellbeing", response_model=list[CaregiverWellbeingOut])
def list_wellbeing(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    require_care_team_user(current_user)
    return db.query(CaregiverWellbeing).filter(CaregiverWellbeing.user_id == current_user["id"]).order_by(CaregiverWellbeing.recorded_at.asc()).all()

@router.post("/caregiver-wellbeing", response_model=CaregiverWellbeingOut, status_code=201)
def create_wellbeing(
    body: CaregiverWellbeingIn,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_care_team_user(current_user)
    validate_scores(body)
    
    row = CaregiverWellbeing(
        id=uuid.uuid4(),
        user_id=current_user["id"],
        energy_score=body.energy_score,
        stress_score=body.stress_score,
        support_needed=body.support_needed,
        notes=body.notes,
        recorded_at=datetime.now(timezone.utc)
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
