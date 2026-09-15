"""
Patient profile endpoints + caregiver-links.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, require_caregiver_or_hw
from app.api.schemas import (
    PatientProfileOut, PatientProfileUpdate,
    MedicationCreate, MedicationOut,
    SafetyCheckInCreate, SafetyCheckInOut,
    EmergencyContactCreate, EmergencyContactOut,
    CaregiverLinkCreate, CaregiverLinkOut, CaregiverLinkPatch, AuditEntryOut,
    CaregiverNoteCreate, CaregiverNoteOut,
)
from app.mock_data import (
    PATIENT_PROFILES, CAREGIVER_LINKS, AUDIT_LOG, CAREGIVER_NOTES, get_patients_for_user,
    add_audit_entry, USERS_BY_ID,
)
from app.api.regional import REGIONAL_THEMES

router = APIRouter(tags=["patients"])


def _assert_can_read_patient(current_user: dict, patient_id: str):
    allowed = get_patients_for_user(current_user)
    if patient_id not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorised to access this patient's data")


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/profile", response_model=PatientProfileOut)
def get_patient_profile(patient_id: str, current_user: dict = Depends(get_current_user)):
    _assert_can_read_patient(current_user, patient_id)
    add_audit_entry(current_user["id"], patient_id, "read_profile")
    profile = PATIENT_PROFILES.get(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile


@router.put("/patients/{patient_id}/profile", response_model=PatientProfileOut)
def update_patient_profile(
    patient_id: str,
    body: PatientProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    _assert_can_read_patient(current_user, patient_id)
    if current_user["role"] == "caregiver" and current_user["id"] != patient_id:
        raise HTTPException(status_code=403, detail="Caregivers cannot edit patient profiles")
    profile = PATIENT_PROFILES.get(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    if body.theme_preference and body.theme_preference not in {theme["id"] for theme in REGIONAL_THEMES}:
        raise HTTPException(status_code=422, detail="Unknown regional theme")
    for field, value in body.model_dump(exclude_none=True).items():
        profile[field] = value
    add_audit_entry(current_user["id"], patient_id, "update_profile")
    return profile


# ── Medication records ────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/medications", response_model=list[MedicationOut])
def list_medications(patient_id: str, current_user: dict = Depends(get_current_user)):
    _assert_can_read_patient(current_user, patient_id)
    from app.mock_data import MEDICATIONS
    return [med for med in MEDICATIONS if med["patient_id"] == patient_id]


@router.post("/patients/{patient_id}/medications", response_model=MedicationOut, status_code=201)
def create_medication(patient_id: str, body: MedicationCreate, current_user: dict = Depends(get_current_user)):
    if patient_id != body.patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    _assert_can_read_patient(current_user, patient_id)
    if current_user["role"] == "patient":
        raise HTTPException(status_code=403, detail="A caregiver or health worker must add medications")
    from app.mock_data import MEDICATIONS
    medication = {
        "id": str(uuid.uuid4()), **body.model_dump(),
        "missed_dose_guidance": "Do not take an extra dose. Follow your clinician or pharmacist instructions.",
    }
    MEDICATIONS.append(medication)
    add_audit_entry(current_user["id"], patient_id, "create_medication")
    return medication


# ── Safety check-ins ──────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/safety-check-in", response_model=SafetyCheckInOut | None)
def get_safety_check_in(patient_id: str, current_user: dict = Depends(get_current_user)):
    _assert_can_read_patient(current_user, patient_id)
    from app.mock_data import SAFETY_CHECK_INS
    return SAFETY_CHECK_INS.get(patient_id)


@router.post("/patients/{patient_id}/safety-check-in", response_model=SafetyCheckInOut)
def create_safety_check_in(patient_id: str, body: SafetyCheckInCreate, current_user: dict = Depends(get_current_user)):
    if patient_id != body.patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    _assert_can_read_patient(current_user, patient_id)
    if body.share_location and current_user["role"] == "patient" and not PATIENT_PROFILES[patient_id].get("location_sharing_consent", False):
        raise HTTPException(status_code=409, detail="Location sharing consent is required")
    from app.mock_data import SAFETY_CHECK_INS, _now
    entry = {"id": str(uuid.uuid4()), **body.model_dump(), "checked_in_at": _now().isoformat(), "consent_required": True}
    if not body.share_location:
        entry["approximate_area"] = None
    SAFETY_CHECK_INS[patient_id] = entry
    add_audit_entry(current_user["id"], patient_id, "create_safety_check_in")
    return entry


# ── Emergency contacts ───────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/emergency-contacts", response_model=list[EmergencyContactOut])
def list_emergency_contacts(patient_id: str, current_user: dict = Depends(get_current_user)):
    _assert_can_read_patient(current_user, patient_id)
    from app.mock_data import EMERGENCY_CONTACTS
    return [contact for contact in EMERGENCY_CONTACTS if contact["patient_id"] == patient_id]


@router.post("/patients/{patient_id}/emergency-contacts", response_model=EmergencyContactOut, status_code=201)
def create_emergency_contact(patient_id: str, body: EmergencyContactCreate, current_user: dict = Depends(get_current_user)):
    if patient_id != body.patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    _assert_can_read_patient(current_user, patient_id)
    if current_user["role"] == "patient":
        raise HTTPException(status_code=403, detail="A caregiver or health worker must add contacts")
    from app.mock_data import EMERGENCY_CONTACTS
    if body.is_primary:
        for contact in EMERGENCY_CONTACTS:
            if contact["patient_id"] == patient_id:
                contact["is_primary"] = False
    contact = {"id": str(uuid.uuid4()), **body.model_dump()}
    EMERGENCY_CONTACTS.append(contact)
    add_audit_entry(current_user["id"], patient_id, "create_emergency_contact")
    return contact


@router.get("/patients/{patient_id}/emergency-call/{contact_id}")
def emergency_call_preview(patient_id: str, contact_id: str, current_user: dict = Depends(get_current_user)):
    _assert_can_read_patient(current_user, patient_id)
    from app.mock_data import EMERGENCY_CONTACTS
    contact = next((c for c in EMERGENCY_CONTACTS if c["id"] == contact_id and c["patient_id"] == patient_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Emergency contact not found")
    add_audit_entry(current_user["id"], patient_id, "emergency_call_preview")
    return {"action": "call", "phone": contact["phone"], "contact_name": contact["name"], "warning": "User confirmation required before calling"}


# ── Caregiver notes ───────────────────────────────────────────────────────────

@router.get("/caregiver-notes", response_model=list[CaregiverNoteOut])
def list_caregiver_notes(patient_id: str, current_user: dict = Depends(get_current_user)):
    _assert_can_read_patient(current_user, patient_id)
    return [note for note in CAREGIVER_NOTES if note["patient_id"] == patient_id][-100:][::-1]


@router.post("/caregiver-notes", response_model=CaregiverNoteOut, status_code=201)
def create_caregiver_note(body: CaregiverNoteCreate, current_user: dict = Depends(get_current_user)):
    _assert_can_read_patient(current_user, body.patient_id)
    if current_user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Only care-team members can add handover notes")
    from app.mock_data import _now
    note = {"id": str(uuid.uuid4()), **body.model_dump(), "author_id": current_user["id"], "created_at": _now().isoformat()}
    CAREGIVER_NOTES.append(note)
    add_audit_entry(current_user["id"], body.patient_id, "create_caregiver_note")
    return note


# ── Audit log ──────────────────────────────────────────────────────────────────

@router.get("/audit-log", response_model=list[AuditEntryOut])
def list_audit_log(
    patient_id: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    allowed = set(get_patients_for_user(current_user))
    if patient_id and patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised to view this audit log")
    entries = [entry for entry in AUDIT_LOG if entry["patient_id"] in allowed]
    if patient_id:
        entries = [entry for entry in entries if entry["patient_id"] == patient_id]
    return entries[-100:][::-1]


# ── Caregiver Links ───────────────────────────────────────────────────────────

@router.get("/caregiver-links", response_model=list[CaregiverLinkOut])
def list_caregiver_links(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "patient":
        return [link for link in CAREGIVER_LINKS if link["patient_id"] == current_user["id"]]
    if current_user["role"] == "caregiver":
        return [link for link in CAREGIVER_LINKS if link["caregiver_id"] == current_user["id"]]
    if current_user["role"] in ("health_worker", "admin"):
        return list(CAREGIVER_LINKS)
    return []


@router.post("/caregiver-links", response_model=CaregiverLinkOut, status_code=201)
def create_caregiver_link(
    body: CaregiverLinkCreate,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in ("caregiver", "admin"):
        raise HTTPException(status_code=403, detail="Only caregivers or admins can request a link")
    caregiver_id = body.caregiver_id or current_user["id"]
    caregiver = USERS_BY_ID.get(caregiver_id)
    if not caregiver or caregiver.get("role") != "caregiver":
        raise HTTPException(status_code=400, detail="Invalid caregiver account")
    if current_user["role"] == "caregiver" and caregiver_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cannot create a link for another caregiver")
    if not any(user["id"] == body.patient_id and user["role"] == "patient" for user in USERS_BY_ID.values()):
        raise HTTPException(status_code=404, detail="Patient not found")
    link = {
        "id": str(uuid.uuid4()),
        "caregiver_id": caregiver_id,
        "patient_id": body.patient_id,
        "relationship": body.relationship,
        "status": "active",
    }
    CAREGIVER_LINKS.append(link)
    add_audit_entry(current_user["id"], body.patient_id, "grant_caregiver_access")
    return link


@router.patch("/caregiver-links/{link_id}", response_model=CaregiverLinkOut)
def patch_caregiver_link(
    link_id: str,
    body: CaregiverLinkPatch,
    current_user: dict = Depends(get_current_user),
):
    for link in CAREGIVER_LINKS:
        if link["id"] != link_id:
            continue
        allowed = (
            current_user["role"] == "admin"
            or current_user["id"] == link["caregiver_id"]
            or current_user["id"] == link["patient_id"]
        )
        if not allowed:
            raise HTTPException(status_code=403, detail="Not authorised to change this consent grant")
        link["status"] = body.status
        action = "revoke_caregiver_access" if body.status == "revoked" else "restore_caregiver_access"
        add_audit_entry(current_user["id"], link["patient_id"], action)
        return link
    raise HTTPException(status_code=404, detail="Link not found")
