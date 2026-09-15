from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.api.dependencies import get_current_user, require_caregiver_or_hw
from app.core.db import get_db
from app.core.crud import get_patients_for_user, add_audit_entry
from app.models import (
    PatientProfile, Medication, SafetyCheckIn, EmergencyContact, 
    CaregiverNote, AuditLog, CaregiverLink, User
)

from app.api.schemas import (
    PatientProfileOut, PatientProfileUpdate,
    MedicationCreate, MedicationOut,
    SafetyCheckInCreate, SafetyCheckInOut,
    EmergencyContactCreate, EmergencyContactOut,
    CaregiverLinkCreate, CaregiverLinkOut, CaregiverLinkPatch, AuditEntryOut,
    CaregiverNoteCreate, CaregiverNoteOut,
)
from app.api.regional import REGIONAL_THEMES
from datetime import datetime, timezone

router = APIRouter(tags=["patients"])


def _assert_can_read_patient(current_user: dict, patient_id: str, db: Session):
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorised to access this patient's data")


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/profile", response_model=PatientProfileOut)
def get_patient_profile(patient_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _assert_can_read_patient(current_user, patient_id, db)
    add_audit_entry(db, current_user["id"], patient_id, "read_profile")
    
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == patient_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
        
    return profile


@router.put("/patients/{patient_id}/profile", response_model=PatientProfileOut)
def update_patient_profile(
    patient_id: str,
    body: PatientProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _assert_can_read_patient(current_user, patient_id, db)
    if current_user["role"] == "caregiver" and current_user["id"] != patient_id:
        raise HTTPException(status_code=403, detail="Caregivers cannot edit patient profiles")
        
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == patient_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
        
    if body.theme_preference and body.theme_preference not in {theme["id"] for theme in REGIONAL_THEMES}:
        raise HTTPException(status_code=422, detail="Unknown regional theme")
        
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
        
    db.commit()
    db.refresh(profile)
    add_audit_entry(db, current_user["id"], patient_id, "update_profile")
    return profile


# ── Medication records ────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/medications", response_model=list[MedicationOut])
def list_medications(patient_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _assert_can_read_patient(current_user, patient_id, db)
    meds = db.query(Medication).filter(Medication.patient_id == patient_id).all()
    return meds


@router.post("/patients/{patient_id}/medications", response_model=MedicationOut, status_code=201)
def create_medication(patient_id: str, body: MedicationCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if patient_id != body.patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    _assert_can_read_patient(current_user, patient_id, db)
    if current_user["role"] == "patient":
        raise HTTPException(status_code=403, detail="A caregiver or health worker must add medications")
        
    medication = Medication(
        id=uuid.uuid4(),
        **body.model_dump(),
        missed_dose_guidance="Do not take an extra dose. Follow your clinician or pharmacist instructions."
    )
    db.add(medication)
    db.commit()
    db.refresh(medication)
    
    add_audit_entry(db, current_user["id"], patient_id, "create_medication")
    return medication


# ── Safety check-ins ──────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/safety-check-in", response_model=SafetyCheckInOut | None)
def get_safety_check_in(patient_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _assert_can_read_patient(current_user, patient_id, db)
    check_in = db.query(SafetyCheckIn).filter(SafetyCheckIn.patient_id == patient_id).order_by(SafetyCheckIn.checked_in_at.desc()).first()
    return check_in


@router.post("/patients/{patient_id}/safety-check-in", response_model=SafetyCheckInOut)
def create_safety_check_in(patient_id: str, body: SafetyCheckInCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if patient_id != body.patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    _assert_can_read_patient(current_user, patient_id, db)
    
    if body.share_location and current_user["role"] == "patient":
        profile = db.query(PatientProfile).filter(PatientProfile.user_id == patient_id).first()
        if not profile or not profile.location_sharing_consent:
            raise HTTPException(status_code=409, detail="Location sharing consent is required")
            
    check_in = SafetyCheckIn(
        id=uuid.uuid4(),
        **body.model_dump(),
        checked_in_at=datetime.now(timezone.utc),
        consent_required=True
    )
    if not body.share_location:
        check_in.approximate_area = None
        
    db.add(check_in)
    db.commit()
    db.refresh(check_in)
    
    add_audit_entry(db, current_user["id"], patient_id, "create_safety_check_in")
    return check_in


# ── Emergency contacts ───────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/emergency-contacts", response_model=list[EmergencyContactOut])
def list_emergency_contacts(patient_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _assert_can_read_patient(current_user, patient_id, db)
    contacts = db.query(EmergencyContact).filter(EmergencyContact.patient_id == patient_id).all()
    return contacts


@router.post("/patients/{patient_id}/emergency-contacts", response_model=EmergencyContactOut, status_code=201)
def create_emergency_contact(patient_id: str, body: EmergencyContactCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if patient_id != body.patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    _assert_can_read_patient(current_user, patient_id, db)
    if current_user["role"] == "patient":
        raise HTTPException(status_code=403, detail="A caregiver or health worker must add contacts")
        
    if body.is_primary:
        db.query(EmergencyContact).filter(EmergencyContact.patient_id == patient_id).update({"is_primary": False})
        
    contact = EmergencyContact(id=uuid.uuid4(), **body.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    add_audit_entry(db, current_user["id"], patient_id, "create_emergency_contact")
    return contact


@router.get("/patients/{patient_id}/emergency-call/{contact_id}")
def emergency_call_preview(patient_id: str, contact_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _assert_can_read_patient(current_user, patient_id, db)
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id, EmergencyContact.patient_id == patient_id).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Emergency contact not found")
        
    add_audit_entry(db, current_user["id"], patient_id, "emergency_call_preview")
    return {"action": "call", "phone": contact.phone, "contact_name": contact.name, "warning": "User confirmation required before calling"}


# ── Caregiver notes ───────────────────────────────────────────────────────────

@router.get("/caregiver-notes", response_model=list[CaregiverNoteOut])
def list_caregiver_notes(patient_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _assert_can_read_patient(current_user, patient_id, db)
    notes = db.query(CaregiverNote).filter(CaregiverNote.patient_id == patient_id).order_by(CaregiverNote.created_at.desc()).limit(100).all()
    return notes


@router.post("/caregiver-notes", response_model=CaregiverNoteOut, status_code=201)
def create_caregiver_note(body: CaregiverNoteCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _assert_can_read_patient(current_user, body.patient_id, db)
    if current_user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Only care-team members can add handover notes")
        
    note = CaregiverNote(
        id=uuid.uuid4(),
        **body.model_dump(),
        author_id=current_user["id"],
        created_at=datetime.now(timezone.utc)
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    
    add_audit_entry(db, current_user["id"], body.patient_id, "create_caregiver_note")
    return note


# ── Audit log ──────────────────────────────────────────────────────────────────

@router.get("/audit-log", response_model=list[AuditEntryOut])
def list_audit_log(
    patient_id: str | None = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed = set(get_patients_for_user(current_user, db))
    if patient_id and patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised to view this audit log")
        
    query = db.query(AuditLog).filter(AuditLog.patient_id.in_(allowed))
    if patient_id:
        query = query.filter(AuditLog.patient_id == patient_id)
        
    entries = query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return entries


# ── Caregiver Links ───────────────────────────────────────────────────────────

@router.get("/caregiver-links", response_model=list[CaregiverLinkOut])
def list_caregiver_links(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] == "patient":
        return db.query(CaregiverLink).filter(CaregiverLink.patient_id == current_user["id"]).all()
    if current_user["role"] == "caregiver":
        return db.query(CaregiverLink).filter(CaregiverLink.caregiver_id == current_user["id"]).all()
    if current_user["role"] in ("health_worker", "admin"):
        return db.query(CaregiverLink).all()
    return []


@router.post("/caregiver-links", response_model=CaregiverLinkOut, status_code=201)
def create_caregiver_link(
    body: CaregiverLinkCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ("caregiver", "admin"):
        raise HTTPException(status_code=403, detail="Only caregivers or admins can request a link")
        
    caregiver_id = body.caregiver_id or current_user["id"]
    caregiver = db.query(User).filter(User.id == caregiver_id).first()
    
    if not caregiver or caregiver.role != "caregiver":
        raise HTTPException(status_code=400, detail="Invalid caregiver account")
        
    if current_user["role"] == "caregiver" and str(caregiver_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cannot create a link for another caregiver")
        
    patient = db.query(User).filter(User.id == body.patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    link = CaregiverLink(
        id=uuid.uuid4(),
        caregiver_id=caregiver_id,
        patient_id=body.patient_id,
        relationship=body.relationship,
        status="active"
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    
    add_audit_entry(db, current_user["id"], body.patient_id, "grant_caregiver_access")
    return link


@router.patch("/caregiver-links/{link_id}", response_model=CaregiverLinkOut)
def patch_caregiver_link(
    link_id: str,
    body: CaregiverLinkPatch,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    link = db.query(CaregiverLink).filter(CaregiverLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
        
    allowed = (
        current_user["role"] == "admin"
        or current_user["id"] == str(link.caregiver_id)
        or current_user["id"] == str(link.patient_id)
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="Not authorised to change this consent grant")
        
    link.status = body.status
    db.commit()
    db.refresh(link)
    
    action = "revoke_caregiver_access" if body.status == "revoked" else "restore_caregiver_access"
    add_audit_entry(db, current_user["id"], str(link.patient_id), action)
    
    return link
