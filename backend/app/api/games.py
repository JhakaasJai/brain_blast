"""
Game session sync + difficulty endpoint.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.schemas import (
    SyncGameSessionsRequest, SyncGameSessionsResponse,
    DifficultyResponse,
)
from app.mock_data import (
    GAME_SESSIONS, DIFFICULTY_LOG, PATIENT_PROFILES,
    get_patients_for_user,
)
from app.services.difficulty import compute_next_difficulty

router = APIRouter(tags=["games"])


@router.post("/sync/game-sessions", response_model=SyncGameSessionsResponse)
def sync_game_sessions(
    body: SyncGameSessionsRequest,
    current_user: dict = Depends(get_current_user),
):
    synced = 0
    skipped = 0
    existing_uuids = {s["client_uuid"] for s in GAME_SESSIONS}
    for session in body.sessions:
        allowed = get_patients_for_user(current_user)
        if session.patient_id not in allowed:
            skipped += 1
            continue
        if session.client_uuid in existing_uuids:
            skipped += 1
            continue
        record = {"id": str(uuid.uuid4()), **session.model_dump(), "sync_status": "synced"}
        GAME_SESSIONS.append(record)
        existing_uuids.add(session.client_uuid)
        # After each new session, evaluate difficulty
        _maybe_update_difficulty(session.patient_id, session.game_type)
        synced += 1
    return SyncGameSessionsResponse(synced=synced, skipped=skipped)


@router.get("/difficulty/next", response_model=DifficultyResponse)
def get_next_difficulty(
    patient_id: str,
    game_type: str,
    current_user: dict = Depends(get_current_user),
):
    allowed = get_patients_for_user(current_user)
    if patient_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorised")
    if game_type not in ("memory", "attention", "routine", "recognition"):
        raise HTTPException(status_code=400, detail="Unknown game_type")
    return compute_next_difficulty(patient_id, game_type)


def _maybe_update_difficulty(patient_id: str, game_type: str):
    """Recalculate and persist difficulty after a new session syncs."""
    result = compute_next_difficulty(patient_id, game_type)
    profile = PATIENT_PROFILES.get(patient_id)
    if profile and result["current_tier"] != result["next_tier"]:
        DIFFICULTY_LOG.append({
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "game_type": game_type,
            "previous_tier": result["current_tier"],
            "new_tier": result["next_tier"],
            "decision_source": result["decision_source"],
            "inputs_json": result["inputs"],
            "decided_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        })
        profile["current_difficulty"][game_type] = result["next_tier"]
