"""R16 — Appointment preparation.

Caregivers (and health_worker/admin) can create and manage structured
preparation notes for a patient's upcoming appointment: doctor name,
clinic, questions to ask, items to bring, and transport instructions.

Patients can read their own preparation notes (read-only, simplified view).
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.api.dependencies import get_current_user
from app.core.crud import get_patients_for_user, add_audit_entry
from app.models import AppointmentPrep
from app.api.schemas import AppointmentPrepCreate, AppointmentPrepOut, AppointmentPrepUpdate

router = APIRouter(tags=["appointment-preparation"])

_CARE_TEAM_ROLES = ("caregiver", "health_worker", "admin")
_DISCLAIMER = (
    "This preparation note is an organisational aid only and does not "
    "constitute medical advice. Discuss all clinical decisions with the patient's doctor."
)

def _require_patient_access(patient_id: str, user: dict, db: Session) -> None:
    """Raise 403 if user cannot see this patient's prep notes."""
    if user["role"] == "patient":
        if user["id"] != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return
    if user["role"] not in _CARE_TEAM_ROLES:
        raise HTTPException(status_code=403, detail="Care-team access required")
    allowed = get_patients_for_user(user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Patient is outside your care scope")

def _require_care_team(user: dict) -> None:
    if user["role"] not in _CARE_TEAM_ROLES:
        raise HTTPException(status_code=403, detail="Care-team role required to edit appointment prep")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/appointment-prep", response_model=list[AppointmentPrepOut])
def list_appointment_preps(patient_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_patient_access(patient_id, current_user, db)
    add_audit_entry(db, current_user["id"], patient_id, "read_appointment_preps")
    rows = db.query(AppointmentPrep).filter(AppointmentPrep.patient_id == patient_id).order_by(AppointmentPrep.appointment_at.desc()).all()
    return rows


@router.get("/patients/{patient_id}/appointment-prep/next", response_model=AppointmentPrepOut | None)
def get_next_appointment_prep(patient_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_patient_access(patient_id, current_user, db)
    add_audit_entry(db, current_user["id"], patient_id, "read_next_appointment_prep")
    now_iso = datetime.now(timezone.utc).isoformat()
    upcoming = db.query(AppointmentPrep).filter(
        AppointmentPrep.patient_id == patient_id, 
        AppointmentPrep.appointment_at >= now_iso
    ).order_by(AppointmentPrep.appointment_at.asc()).first()
    return upcoming


@router.post("/patients/{patient_id}/appointment-prep", response_model=AppointmentPrepOut, status_code=201)
def create_appointment_prep(
    patient_id: str,
    body: AppointmentPrepCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_care_team(current_user)
    _require_patient_access(patient_id, current_user, db)
    if body.patient_id != patient_id:
        raise HTTPException(status_code=422, detail="patient_id in body must match path parameter")
    if not body.doctor_name.strip():
        raise HTTPException(status_code=422, detail="doctor_name is required")
    if not body.clinic_or_hospital.strip():
        raise HTTPException(status_code=422, detail="clinic_or_hospital is required")
    if not body.appointment_at.strip():
        raise HTTPException(status_code=422, detail="appointment_at is required")

    row = AppointmentPrep(
        id=uuid.uuid4(),
        patient_id=patient_id,
        appointment_at=body.appointment_at,
        doctor_name=body.doctor_name.strip(),
        clinic_or_hospital=body.clinic_or_hospital.strip(),
        questions_to_ask=body.questions_to_ask,
        items_to_bring=body.items_to_bring,
        transport_notes=body.transport_notes,
        extra_notes=body.extra_notes,
        created_by=current_user["id"],
        created_at=datetime.now(timezone.utc),
        disclaimer=_DISCLAIMER,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    add_audit_entry(db, current_user["id"], patient_id, "created_appointment_prep")
    return row


@router.patch("/patients/{patient_id}/appointment-prep/{prep_id}", response_model=AppointmentPrepOut)
def update_appointment_prep(
    patient_id: str,
    prep_id: str,
    body: AppointmentPrepUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_care_team(current_user)
    _require_patient_access(patient_id, current_user, db)
    row = db.query(AppointmentPrep).filter(AppointmentPrep.id == prep_id, AppointmentPrep.patient_id == patient_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Appointment prep note not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    add_audit_entry(db, current_user["id"], patient_id, "updated_appointment_prep")
    return row


@router.delete("/patients/{patient_id}/appointment-prep/{prep_id}", status_code=204)
def delete_appointment_prep(
    patient_id: str,
    prep_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_care_team(current_user)
    _require_patient_access(patient_id, current_user, db)
    row = db.query(AppointmentPrep).filter(AppointmentPrep.id == prep_id, AppointmentPrep.patient_id == patient_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Appointment prep note not found")
    db.delete(row)
    db.commit()
    add_audit_entry(db, current_user["id"], patient_id, "deleted_appointment_prep")
    return None

__all__ = ["router"]
