"""R13 health-worker route and visit planning."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.schemas import VisitPlanIn, VisitPlanOut, VisitPlanUpdate
from app.mock_data import VISIT_PLANS, get_patients_for_user, get_user_by_id

router = APIRouter(tags=["health-worker visits"])
ALLOWED_ROLES = ("health_worker", "admin")
STATUSES = ("planned", "completed", "cancelled")


def require_route_access(user: dict) -> None:
    if user["role"] not in ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Health-worker route access required")


@router.get("/health-worker/visits", response_model=list[VisitPlanOut])
def list_visits(patient_id: str | None = None, current_user: dict = Depends(get_current_user)):
    require_route_access(current_user)
    allowed = set(get_patients_for_user(current_user))
    if patient_id and patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Patient is outside your care scope")
    rows = [row for row in VISIT_PLANS if row["patient_id"] in allowed]
    if patient_id:
        rows = [row for row in rows if row["patient_id"] == patient_id]
    return sorted(rows, key=lambda row: row["scheduled_at"])


@router.post("/health-worker/visits", response_model=VisitPlanOut, status_code=201)
def create_visit(body: VisitPlanIn, current_user: dict = Depends(get_current_user)):
    require_route_access(current_user)
    if body.patient_id not in get_patients_for_user(current_user):
        raise HTTPException(status_code=403, detail="Patient is outside your care scope")
    if not body.purpose.strip() or not body.location.strip():
        raise HTTPException(status_code=422, detail="purpose and location are required")
    if not body.scheduled_at.strip():
        raise HTTPException(status_code=422, detail="scheduled_at is required")
    patient = get_user_by_id(body.patient_id)
    row = {
        "id": str(uuid.uuid4()),
        "patient_id": body.patient_id,
        "patient_name": patient["name"] if patient else body.patient_id,
        "scheduled_at": body.scheduled_at,
        "purpose": body.purpose.strip(),
        "location": body.location.strip(),
        "notes": body.notes,
        "status": "planned",
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    VISIT_PLANS.append(row)
    return row


@router.patch("/health-worker/visits/{visit_id}", response_model=VisitPlanOut)
def update_visit(visit_id: str, body: VisitPlanUpdate, current_user: dict = Depends(get_current_user)):
    require_route_access(current_user)
    row = next((item for item in VISIT_PLANS if item["id"] == visit_id), None)
    if not row or row["patient_id"] not in get_patients_for_user(current_user):
        raise HTTPException(status_code=404, detail="Visit not found")
    if body.status not in STATUSES:
        raise HTTPException(status_code=422, detail="status must be planned, completed, or cancelled")
    row["status"] = body.status
    if body.notes is not None:
        row["notes"] = body.notes
    return row


@router.delete("/health-worker/visits/{visit_id}", status_code=204)
def delete_visit(visit_id: str, current_user: dict = Depends(get_current_user)):
    require_route_access(current_user)
    row = next((item for item in VISIT_PLANS if item["id"] == visit_id), None)
    if not row or row["patient_id"] not in get_patients_for_user(current_user):
        raise HTTPException(status_code=404, detail="Visit not found")
    VISIT_PLANS.remove(row)
    return None


__all__ = ["router"]
