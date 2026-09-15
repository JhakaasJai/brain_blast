"""
v1 Rule-based difficulty engine.
Logic (from workflow spec Section 4.2):
  - Look at the last 3 completed sessions for (patient_id, game_type)
  - If all 3 exist and avg accuracy > 80% → raise tier
  - If all 3 exist and avg accuracy < 50% → lower tier
  - Otherwise → hold current tier

Returns a DifficultyResponse-compatible dict.

# NOTE: Phase 6 (v2 ML) is deferred for this prototype.
# The endpoint contract is identical; swapping in ML is a one-function change here.
"""

from sqlalchemy.orm import Session
import json
from app.models import GameSession, PatientProfile

TIER_ORDER = ["easy", "medium", "hard"]

def compute_next_difficulty(patient_id: str, game_type: str, db: Session) -> dict:
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == patient_id).first()
    
    current_tier = "easy"
    if profile:
        diffs = {
            "memory": profile.difficulty_memory,
            "attention": profile.difficulty_attention,
            "routine": profile.difficulty_routine,
            "recognition": profile.difficulty_recognition
        }
        current_tier = diffs.get(game_type, "easy")

    sessions = db.query(GameSession).filter(
        GameSession.patient_id == patient_id,
        GameSession.game_type == game_type
    ).order_by(GameSession.completed_at.desc()).all()

    if len(sessions) < 3:
        return {
            "patient_id": patient_id,
            "game_type": game_type,
            "current_tier": current_tier,
            "next_tier": current_tier,
            "decision_source": "rule",
            "reason": f"Fewer than 3 sessions ({len(sessions)}) — holding tier",
            "inputs": json.dumps({"session_count": len(sessions), "last_3_accuracy": []}),
        }

    last_3 = sessions[:3]
    avg_accuracy = sum(s.accuracy_pct for s in last_3) / 3
    last_3_acc = [s.accuracy_pct for s in last_3]

    current_idx = TIER_ORDER.index(current_tier)

    if avg_accuracy > 80 and current_idx < len(TIER_ORDER) - 1:
        next_tier = TIER_ORDER[current_idx + 1]
        reason = f"Last 3 avg accuracy {avg_accuracy:.1f}% > 80% — raising tier"
    elif avg_accuracy < 50 and current_idx > 0:
        next_tier = TIER_ORDER[current_idx - 1]
        reason = f"Last 3 avg accuracy {avg_accuracy:.1f}% < 50% — lowering tier"
    else:
        next_tier = current_tier
        reason = f"Last 3 avg accuracy {avg_accuracy:.1f}% — holding tier"

    return {
        "patient_id": patient_id,
        "game_type": game_type,
        "current_tier": current_tier,
        "next_tier": next_tier,
        "decision_source": "rule",
        "reason": reason,
        "inputs": json.dumps({
            "session_count": len(sessions),
            "last_3_accuracy": last_3_acc,
            "avg_accuracy": round(avg_accuracy, 1),
        }),
    }
