"""
Game session sync + difficulty endpoint.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone

from app.api.dependencies import get_current_user
from app.core.db import get_db
from app.core.crud import get_patients_for_user
from app.models import GameSession, DifficultyLog, PatientProfile
from app.api.schemas import (
    SyncGameSessionsRequest, SyncGameSessionsResponse,
    DifficultyResponse,
)
from app.services.difficulty import compute_next_difficulty

router = APIRouter(tags=["games"])

@router.post("/sync/game-sessions", response_model=SyncGameSessionsResponse)
def sync_game_sessions(
    body: SyncGameSessionsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    synced = 0
    skipped = 0
    allowed = get_patients_for_user(current_user, db)
    
    # Load existing client UUIDs to prevent dupes in this batch
    patient_ids = [s.patient_id for s in body.sessions]
    existing = db.query(GameSession.client_uuid).filter(GameSession.patient_id.in_(patient_ids)).all()
    existing_uuids = {str(row.client_uuid) for row in existing}
    
    for session in body.sessions:
        if session.patient_id not in allowed:
            skipped += 1
            continue
        if str(session.client_uuid) in existing_uuids:
            skipped += 1
            continue
            
        record = GameSession(
            id=uuid.uuid4(),
            patient_id=session.patient_id,
            client_uuid=session.client_uuid,
            game_type=session.game_type,
            difficulty=session.difficulty,
            score=session.score,
            accuracy_pct=session.accuracy,
            time_spent_seconds=session.time_spent_seconds,
            hints_used=session.hints_used,
            completed_at=datetime.fromisoformat(session.completed_at)
        )
        db.add(record)
        existing_uuids.add(str(session.client_uuid))
        
        _maybe_update_difficulty(session.patient_id, session.game_type, db)
        synced += 1
        
    db.commit()
    return SyncGameSessionsResponse(synced=synced, skipped=skipped)


@router.get("/difficulty/next", response_model=DifficultyResponse)
def get_next_difficulty(
    patient_id: str,
    game_type: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed = get_patients_for_user(current_user, db)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    if game_type not in ("memory", "attention", "routine", "recognition"):
        raise HTTPException(status_code=400, detail="Unknown game_type")
        
    result = compute_next_difficulty(patient_id, game_type, db)
    
    # We parse the JSON inputs string back out to match the Pydantic schema return expectation
    import json
    if isinstance(result.get("inputs"), str):
        result["inputs"] = json.loads(result["inputs"])
        
    return result


def _maybe_update_difficulty(patient_id: str, game_type: str, db: Session):
    """Recalculate and persist difficulty after a new session syncs."""
    result = compute_next_difficulty(patient_id, game_type, db)
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == patient_id).first()
    
    if profile and result["current_tier"] != result["next_tier"]:
        log = DifficultyLog(
            id=uuid.uuid4(),
            patient_id=patient_id,
            game_type=game_type,
            previous_tier=result["current_tier"],
            new_tier=result["next_tier"],
            decision_source=result["decision_source"],
            inputs_json=result["inputs"],
            decided_at=datetime.now(timezone.utc)
        )
        db.add(log)
        
        # update profile
        if game_type == "memory": profile.difficulty_memory = result["next_tier"]
        elif game_type == "attention": profile.difficulty_attention = result["next_tier"]
        elif game_type == "routine": profile.difficulty_routine = result["next_tier"]
        elif game_type == "recognition": profile.difficulty_recognition = result["next_tier"]
        
        # flush the session object without fully committing so the caller can batch commit
        db.flush()
