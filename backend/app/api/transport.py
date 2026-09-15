"""R17 — Appointment transport / location notes.

Caregivers (and health_worker/admin) can create structured transport notes for
a patient's upcoming appointment: travel mode, pickup point, driver contact,
destination, estimated travel time, and return instructions.

Patients can read their own transport notes (read-only).
Transport notes may optionally reference an appointment_prep record by id.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.schemas import TransportNoteCreate, TransportNoteOut, TransportNoteUpdate
from app.mock_data import TRANSPORT_NOTES, add_audit_entry, get_patients_for_user

router = APIRouter(tags=["appointment-transport"])

_CARE_TEAM_ROLES = ("caregiver", "health_worker", "admin")
_VALID_MODES = {"walk", "auto", "taxi", "bus", "family_vehicle", "ambulance", "other"}


def _require_patient_access(patient_id: str, user: dict) -> None:
    if user["role"] == "patient":
        if user["id"] != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return
    if user["role"] not in _CARE_TEAM_ROLES:
        raise HTTPException(status_code=403, detail="Care-team access required")
    if patient_id not in get_patients_for_user(user):
        raise HTTPException(status_code=403, detail="Patient is outside your care scope")


def _require_care_team(user: dict) -> None:
    if user["role"] not in _CARE_TEAM_ROLES:
        raise HTTPException(status_code=403, detail="Care-team role required to edit transport notes")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/transport-notes", response_model=list[TransportNoteOut])
def list_transport_notes(patient_id: str, current_user: dict = Depends(get_current_user)):
    """List all transport notes for a patient, sorted by appointment date descending."""
    _require_patient_access(patient_id, current_user)
    add_audit_entry(current_user["id"], patient_id, "read_transport_notes")
    rows = [r for r in TRANSPORT_NOTES if r["patient_id"] == patient_id]
    return sorted(rows, key=lambda r: r["appointment_at"], reverse=True)


@router.get("/patients/{patient_id}/transport-notes/{note_id}", response_model=TransportNoteOut)
def get_transport_note(patient_id: str, note_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch a single transport note by id."""
    _require_patient_access(patient_id, current_user)
    row = next((r for r in TRANSPORT_NOTES if r["id"] == note_id and r["patient_id"] == patient_id), None)
    if row is None:
        raise HTTPException(status_code=404, detail="Transport note not found")
    add_audit_entry(current_user["id"], patient_id, "read_transport_note")
    return row


@router.post("/patients/{patient_id}/transport-notes", response_model=TransportNoteOut, status_code=201)
def create_transport_note(
    patient_id: str,
    body: TransportNoteCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a transport note for an upcoming appointment (care-team only)."""
    _require_care_team(current_user)
    _require_patient_access(patient_id, current_user)
    if body.patient_id != patient_id:
        raise HTTPException(status_code=422, detail="patient_id in body must match path parameter")
    if not body.pickup_point.strip():
        raise HTTPException(status_code=422, detail="pickup_point is required")
    if not body.destination.strip():
        raise HTTPException(status_code=422, detail="destination is required")
    if not body.pickup_time.strip():
        raise HTTPException(status_code=422, detail="pickup_time is required")
    if body.mode not in _VALID_MODES:
        raise HTTPException(
            status_code=422,
            detail=f"mode must be one of: {', '.join(sorted(_VALID_MODES))}",
        )

    row = {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "appointment_ref": body.appointment_ref,
        "appointment_at": body.appointment_at,
        "mode": body.mode,
        "pickup_point": body.pickup_point.strip(),
        "pickup_time": body.pickup_time.strip(),
        "driver_or_contact_name": body.driver_or_contact_name,
        "driver_or_contact_phone": body.driver_or_contact_phone,
        "destination": body.destination.strip(),
        "estimated_travel_minutes": body.estimated_travel_minutes,
        "return_notes": body.return_notes,
        "extra_notes": body.extra_notes,
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    TRANSPORT_NOTES.append(row)
    add_audit_entry(current_user["id"], patient_id, "created_transport_note")
    return row


@router.patch("/patients/{patient_id}/transport-notes/{note_id}", response_model=TransportNoteOut)
def update_transport_note(
    patient_id: str,
    note_id: str,
    body: TransportNoteUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update fields on a transport note (care-team only)."""
    _require_care_team(current_user)
    _require_patient_access(patient_id, current_user)
    row = next((r for r in TRANSPORT_NOTES if r["id"] == note_id and r["patient_id"] == patient_id), None)
    if row is None:
        raise HTTPException(status_code=404, detail="Transport note not found")
    updates = body.model_dump(exclude_none=True)
    if "mode" in updates and updates["mode"] not in _VALID_MODES:
        raise HTTPException(
            status_code=422,
            detail=f"mode must be one of: {', '.join(sorted(_VALID_MODES))}",
        )
    for field, value in updates.items():
        row[field] = value
    add_audit_entry(current_user["id"], patient_id, "updated_transport_note")
    return row


@router.delete("/patients/{patient_id}/transport-notes/{note_id}", status_code=204)
def delete_transport_note(
    patient_id: str,
    note_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a transport note (care-team only)."""
    _require_care_team(current_user)
    _require_patient_access(patient_id, current_user)
    row = next((r for r in TRANSPORT_NOTES if r["id"] == note_id and r["patient_id"] == patient_id), None)
    if row is None:
        raise HTTPException(status_code=404, detail="Transport note not found")
    TRANSPORT_NOTES.remove(row)
    add_audit_entry(current_user["id"], patient_id, "deleted_transport_note")
    return None


__all__ = ["router"]
