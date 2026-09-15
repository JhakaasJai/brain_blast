"""
R3 — Daily Living Assistance
Simple per-patient daily task checklist. Patients tick tasks done;
caregivers can view progress.
PRODUCTION: persist per-day in DB; reset via scheduled nightly job.
"""
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.api.dependencies import get_current_user
from app.api.schemas import DailyTaskOut, DailyTaskToggle
from app.core.crud import get_patients_for_user
from app.models import DailyTask

router = APIRouter(tags=["daily-living"])


def _default_tasks(patient_id: str, db: Session):
    tasks = [
        {"id": str(uuid.uuid4()), "patient_id": patient_id, "label": "Take morning medication", "icon": "pill", "category": "health"},
        {"id": str(uuid.uuid4()), "patient_id": patient_id, "label": "Drink a glass of water", "icon": "water", "category": "health"},
        {"id": str(uuid.uuid4()), "patient_id": patient_id, "label": "Brush teeth", "icon": "hygiene", "category": "hygiene"},
    ]
    db_tasks = []
    for t in tasks:
        db_task = DailyTask(
            id=uuid.UUID(t["id"]),
            patient_id=t["patient_id"],
            label=t["label"],
            icon=t["icon"],
            category=t["category"],
            done=False
        )
        db.add(db_task)
        db_tasks.append(db_task)
    db.commit()
    for t in db_tasks: db.refresh(t)
    return db_tasks


@router.get("/patients/{patient_id}/daily-tasks",
            response_model=list[DailyTaskOut])
def get_daily_tasks(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
        
    tasks = db.query(DailyTask).filter(DailyTask.patient_id == patient_id).all()
    if not tasks:
        tasks = _default_tasks(patient_id, db)
        
    return tasks


@router.patch("/patients/{patient_id}/daily-tasks/{task_id}",
              response_model=DailyTaskOut)
def toggle_task(
    patient_id: str,
    task_id: str,
    body: DailyTaskToggle,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Patients can only tick their own tasks; care team can mark on behalf
    if current_user["role"] == "patient" and current_user["id"] != patient_id:
        raise HTTPException(status_code=403, detail="Can only update your own tasks")
        
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
        
    task = db.query(DailyTask).filter(DailyTask.id == task_id, DailyTask.patient_id == patient_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.done = body.done
    task.done_at = datetime.now(timezone.utc) if body.done else None
    
    db.commit()
    db.refresh(task)
    
    return task
