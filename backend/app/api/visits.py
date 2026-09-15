"""R13 health-worker route and visit planning."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.api.dependencies import get_current_user
from app.core.crud import get_patients_for_user
from app.models import VisitPlan, User
from app.api.schemas import VisitPlanIn, VisitPlanOut, VisitPlanUpdate

router = APIRouter(tags=["health-worker visits"])
ALLOWED_ROLES = ("health_worker", "admin")
STATUSES = ("planned", "completed", "cancelled")


def require_route_access(user: dict) -> None:
    if user["role"] not in ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Health-worker route access required")


@router.get("/health-worker/visits", response_model=list[VisitPlanOut])
def list_visits(patient_id: str | None = None, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    require_route_access(current_user)
    allowed = set(get_patients_for_user(current_user, db))
    if patient_id and patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Patient is outside your care scope")
        
    query = db.query(VisitPlan).filter(VisitPlan.patient_id.in_(allowed))
    if patient_id:
        query = query.filter(VisitPlan.patient_id == patient_id)
        
    rows = query.order_by(VisitPlan.scheduled_at.asc()).all()
    return rows


@router.post("/health-worker/visits", response_model=VisitPlanOut, status_code=201)
def create_visit(body: VisitPlanIn, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    require_route_access(current_user)
    if body.patient_id not in get_patients_for_user(current_user, db):
        raise HTTPException(status_code=403, detail="Patient is outside your care scope")
    if not body.purpose.strip() or not body.location.strip():
        raise HTTPException(status_code=422, detail="purpose and location are required")
    if not body.scheduled_at.strip():
        raise HTTPException(status_code=422, detail="scheduled_at is required")
        
    patient = db.query(User).filter(User.id == body.patient_id).first()
    
    row = VisitPlan(
        id=uuid.uuid4(),
        patient_id=body.patient_id,
        patient_name=patient.name if patient else body.patient_id,
        scheduled_at=body.scheduled_at,
        purpose=body.purpose.strip(),
        location=body.location.strip(),
        notes=body.notes,
        status="planned",
        created_by=current_user["id"],
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/health-worker/visits/{visit_id}", response_model=VisitPlanOut)
def update_visit(visit_id: str, body: VisitPlanUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    require_route_access(current_user)
    row = db.query(VisitPlan).filter(VisitPlan.id == visit_id).first()
    
    if not row or str(row.patient_id) not in get_patients_for_user(current_user, db):
        raise HTTPException(status_code=404, detail="Visit not found")
    if body.status not in STATUSES:
        raise HTTPException(status_code=422, detail="status must be planned, completed, or cancelled")
        
    row.status = body.status
    if body.notes is not None:
        row.notes = body.notes
        
    db.commit()
    db.refresh(row)
    return row


@router.delete("/health-worker/visits/{visit_id}", status_code=204)
def delete_visit(visit_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    require_route_access(current_user)
    row = db.query(VisitPlan).filter(VisitPlan.id == visit_id).first()
    
    if not row or str(row.patient_id) not in get_patients_for_user(current_user, db):
        raise HTTPException(status_code=404, detail="Visit not found")
        
    db.delete(row)
    db.commit()
    return None

__all__ = ["router"]
