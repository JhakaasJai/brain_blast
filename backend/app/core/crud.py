from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import User, CaregiverLink, HWPatientMap, AuditLog

def get_patients_for_user(current_user: dict, db: Session) -> list[str]:
    """Return list of patient IDs a caregiver/hw/admin is allowed to see."""
    role = current_user["role"]
    uid = current_user["id"]
    
    if role == "patient":
        return [uid]
    
    if role == "caregiver":
        links = db.query(CaregiverLink).filter(
            CaregiverLink.caregiver_id == uid,
            CaregiverLink.status == "active"
        ).all()
        return [str(lk.patient_id) for lk in links]
        
    if role == "health_worker":
        result = db.query(HWPatientMap).filter(HWPatientMap.hw_id == uid).all()
        return [str(row.patient_id) for row in result]
        
    if role == "admin":
        patients = db.query(User).filter(User.role == "patient").all()
        return [str(u.id) for u in patients]
        
    return []

def add_audit_entry(db: Session, actor_id: str, patient_id: str, action: str):
    entry = AuditLog(
        actor_id=actor_id,
        patient_id=patient_id,
        action=action
    )
    db.add(entry)
    db.commit()
