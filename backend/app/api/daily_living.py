"""
R3 — Daily Living Assistance
Simple per-patient daily task checklist. Patients tick tasks done;
caregivers can view progress.
PRODUCTION: persist per-day in DB; reset via scheduled nightly job.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.schemas import DailyTaskOut, DailyTaskToggle
from app.mock_data import DAILY_TASKS, get_patients_for_user

router = APIRouter(tags=["daily-living"])


@router.get("/patients/{patient_id}/daily-tasks",
            response_model=list[DailyTaskOut])
def get_daily_tasks(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
):
    allowed = get_patients_for_user(current_user)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    # Auto-create tasks for new patients not seeded
    if patient_id not in DAILY_TASKS:
        from app.mock_data import _default_tasks
        DAILY_TASKS[patient_id] = _default_tasks(patient_id)
    return DAILY_TASKS[patient_id]


@router.patch("/patients/{patient_id}/daily-tasks/{task_id}",
              response_model=DailyTaskOut)
def toggle_task(
    patient_id: str,
    task_id: str,
    body: DailyTaskToggle,
    current_user: dict = Depends(get_current_user),
):
    # Patients can only tick their own tasks; care team can mark on behalf
    if current_user["role"] == "patient" and current_user["id"] != patient_id:
        raise HTTPException(status_code=403, detail="Can only update your own tasks")
    allowed = get_patients_for_user(current_user)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    tasks = DAILY_TASKS.get(patient_id, [])
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = body.done
            task["done_at"] = datetime.now(timezone.utc).isoformat() if body.done else None
            return task
    raise HTTPException(status_code=404, detail="Task not found")
