"""R5 physical activity logs; prototype has no wearable integration."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user
from app.api.schemas import ActivityLogIn, ActivityLogOut
from app.mock_data import ACTIVITY_LOGS, get_patients_for_user
router=APIRouter(tags=['activity'])
@router.get('/patients/{patient_id}/activities',response_model=list[ActivityLogOut])
def list_activities(patient_id:str,current_user:dict=Depends(get_current_user)):
    if patient_id not in get_patients_for_user(current_user): raise HTTPException(403,'Not authorised')
    return sorted([x for x in ACTIVITY_LOGS if x['patient_id']==patient_id],key=lambda x:x['logged_at'])
@router.post('/patients/{patient_id}/activities',response_model=ActivityLogOut,status_code=201)
def create_activity(patient_id:str,body:ActivityLogIn,current_user:dict=Depends(get_current_user)):
    if current_user['role']=='patient' and current_user['id']!=patient_id: raise HTTPException(403,'Can only record your own activity')
    if patient_id not in get_patients_for_user(current_user): raise HTTPException(403,'Not authorised')
    if body.duration_minutes<=0: raise HTTPException(422,'duration_minutes must be positive')
    if body.intensity and body.intensity not in ('light','moderate','vigorous'): raise HTTPException(422,'Invalid intensity')
    x={'id':str(uuid.uuid4()),'patient_id':patient_id,**body.model_dump(),'logged_at':datetime.now(timezone.utc).isoformat()}
    ACTIVITY_LOGS.append(x); return x
