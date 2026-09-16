"""R5 physical activity logs; prototype has no wearable integration."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.db import get_db
from app.core.crud import get_patients_for_user
from app.models import ActivityLog
from app.api.schemas import ActivityLogIn, ActivityLogOut

router=APIRouter(tags=['activity'])

@router.get('/patients/{patient_id}/activities',response_model=list[ActivityLogOut])
def list_activities(patient_id:str,current_user:dict=Depends(get_current_user),db:Session=Depends(get_db)):
    if patient_id not in get_patients_for_user(current_user,db): raise HTTPException(403,'Not authorised')
    logs = db.query(ActivityLog).filter(ActivityLog.patient_id==patient_id).order_by(ActivityLog.logged_at.asc()).all()
    return logs

@router.post('/patients/{patient_id}/activities',response_model=ActivityLogOut,status_code=201)
def create_activity(patient_id:str,body:ActivityLogIn,current_user:dict=Depends(get_current_user),db:Session=Depends(get_db)):
    if current_user['role']=='patient' and current_user['id']!=patient_id: raise HTTPException(403,'Can only record your own activity')
    if patient_id not in get_patients_for_user(current_user,db): raise HTTPException(403,'Not authorised')
    if body.duration_minutes<=0: raise HTTPException(422,'duration_minutes must be positive')
    if body.intensity and body.intensity not in ('light','moderate','vigorous'): raise HTTPException(422,'Invalid intensity')
    
    x = ActivityLog(
        id=uuid.uuid4(),
        patient_id=patient_id,
        activity_type=body.activity_type,
        duration_minutes=body.duration_minutes,
        intensity=body.intensity,
        notes=body.notes,
        recorded_at=datetime.now(timezone.utc)
    )
    db.add(x)
    db.commit()
    db.refresh(x)
    return x
