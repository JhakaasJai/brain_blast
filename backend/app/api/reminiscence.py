"""
R1 — Reminiscence Therapy
Caregivers seed text prompts for a patient; patients write memory notes in response.
No media upload in prototype — all content is plain text.
Swap REMINISCENCE_PROMPTS / REMINISCENCE_NOTES for a real DB table in production.
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.api.dependencies import get_current_user
from app.api.schemas import (
    ReminiscencePromptOut,
    ReminiscenceNoteIn,
    ReminiscenceNoteOut,
)
from app.core.crud import get_patients_for_user
from app.models import ReminiscencePrompt, ReminiscenceNote

router = APIRouter(tags=["reminiscence"])

# ── Prompts ────────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/reminiscence/prompts", response_model=list[ReminiscencePromptOut])
def list_prompts(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    return db.query(ReminiscencePrompt).filter(ReminiscencePrompt.patient_id == patient_id).all()


@router.post("/patients/{patient_id}/reminiscence/prompts", response_model=ReminiscencePromptOut, status_code=201)
def create_prompt(
    patient_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Only care team may add prompts")
        
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
        
    prompt = ReminiscencePrompt(
        id=uuid.uuid4(),
        patient_id=patient_id,
        theme=body.get("theme", "family"),
        title=body.get("title", ""),
        prompt_text=body.get("prompt_text", ""),
        created_by=current_user["id"],
        created_at=datetime.now(timezone.utc)
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


# ── Notes ──────────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/reminiscence/notes", response_model=list[ReminiscenceNoteOut])
def list_notes(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    return db.query(ReminiscenceNote).filter(ReminiscenceNote.patient_id == patient_id).all()


@router.post("/patients/{patient_id}/reminiscence/notes", response_model=ReminiscenceNoteOut, status_code=201)
def create_note(
    patient_id: str,
    body: ReminiscenceNoteIn,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] == "patient" and current_user["id"] != patient_id:
        raise HTTPException(status_code=403, detail="Can only record your own notes")
        
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
        
    note = ReminiscenceNote(
        id=uuid.uuid4(),
        prompt_id=body.prompt_id,
        patient_id=patient_id,
        note_text=body.note_text,
        recorded_at=datetime.now(timezone.utc)
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
