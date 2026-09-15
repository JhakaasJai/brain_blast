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

TIER_ORDER = ["easy", "medium", "hard"]


def compute_next_difficulty(patient_id: str, game_type: str) -> dict:
    from app.mock_data import GAME_SESSIONS, PATIENT_PROFILES

    profile = PATIENT_PROFILES.get(patient_id)
    current_tier = (profile or {}).get("current_difficulty", {}).get(game_type, "easy")

    # Filter sessions for this patient + game type, sorted newest first
    sessions = sorted(
        [s for s in GAME_SESSIONS if s["patient_id"] == patient_id and s["game_type"] == game_type],
        key=lambda s: s["completed_at"],
        reverse=True,
    )

    if len(sessions) < 3:
        return {
            "patient_id": patient_id,
            "game_type": game_type,
            "current_tier": current_tier,
            "next_tier": current_tier,
            "decision_source": "rule",
            "reason": f"Fewer than 3 sessions ({len(sessions)}) — holding tier",
            "inputs": {"session_count": len(sessions), "last_3_accuracy": []},
        }

    last_3 = sessions[:3]
    avg_accuracy = sum(s["accuracy"] for s in last_3) / 3
    last_3_acc = [s["accuracy"] for s in last_3]

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
        "inputs": {
            "session_count": len(sessions),
            "last_3_accuracy": last_3_acc,
            "avg_accuracy": round(avg_accuracy, 1),
        },
    }
