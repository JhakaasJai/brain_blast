"""
Dashboard aggregation endpoints.
"""
from datetime import datetime, timezone, timedelta
import csv
import io
import json
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.schemas import DashboardSummary, TrendResponse, TrendPoint, AlertOut, CareSummaryOut, SummaryExportOut
from app.mock_data import (
    GAME_SESSIONS, REMINDER_EVENTS, REMINDERS, ALERTS,
    USERS_BY_ID, get_patients_for_user, add_audit_entry,
)

router = APIRouter(tags=["dashboard"])


def _assert_access(current_user: dict, patient_id: str):
    if patient_id not in get_patients_for_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorised")


@router.get("/dashboard/{patient_id}/summary", response_model=DashboardSummary)
def dashboard_summary(patient_id: str, current_user: dict = Depends(get_current_user)):
    _assert_access(current_user, patient_id)
    add_audit_entry(current_user["id"], patient_id, "read_dashboard_summary")

    patient_sessions = [s for s in GAME_SESSIONS if s["patient_id"] == patient_id]
    now = datetime.now(timezone.utc)
    cutoff_7d = now - timedelta(days=7)

    sessions_7d = [
        s for s in patient_sessions
        if datetime.fromisoformat(s["completed_at"]) > cutoff_7d
    ]
    avg_acc_7d = (
        sum(s["accuracy"] for s in sessions_7d) / len(sessions_7d)
        if sessions_7d else 0.0
    )

    # streak: count consecutive days with at least one session
    session_dates = sorted(set(
        datetime.fromisoformat(s["completed_at"]).date()
        for s in patient_sessions
    ), reverse=True)
    streak = 0
    check_date = now.date()
    for d in session_dates:
        if d == check_date or d == check_date - timedelta(days=1):
            streak += 1
            check_date = d
        else:
            break

    # reminder adherence
    patient_rem_ids = {r["id"] for r in REMINDERS if r["patient_id"] == patient_id}
    patient_events = [e for e in REMINDER_EVENTS if e["reminder_id"] in patient_rem_ids]
    done_count = sum(1 for e in patient_events if e["action"] == "done")
    adherence = (done_count / len(patient_events) * 100) if patient_events else 100.0

    last_session_at = (
        max(s["completed_at"] for s in patient_sessions)
        if patient_sessions else None
    )
    inactivity_h = 0.0
    if last_session_at:
        last_dt = datetime.fromisoformat(last_session_at)
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        inactivity_h = (now - last_dt).total_seconds() / 3600

    from app.mock_data import PATIENT_PROFILES
    profile = PATIENT_PROFILES.get(patient_id, {})
    user = USERS_BY_ID.get(patient_id, {})

    return DashboardSummary(
        patient_id=patient_id,
        patient_name=user.get("name", "Unknown"),
        total_sessions=len(patient_sessions),
        sessions_last_7_days=len(sessions_7d),
        streak_days=streak,
        avg_accuracy_last_7_days=round(avg_acc_7d, 1),
        reminder_adherence_pct=round(adherence, 1),
        last_session_at=last_session_at,
        inactivity_hours=round(inactivity_h, 1),
        current_difficulty=profile.get("current_difficulty", {}),
    )


@router.get("/dashboard/{patient_id}/care-summary", response_model=CareSummaryOut)
def care_summary(patient_id: str, period_days: int = 30, current_user: dict = Depends(get_current_user)):
    _assert_access(current_user, patient_id)
    period_days = max(1, min(period_days, 365))
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=period_days)
    sessions = [s for s in GAME_SESSIONS if s["patient_id"] == patient_id and datetime.fromisoformat(s["completed_at"]) >= cutoff]
    rem_ids = {r["id"] for r in REMINDERS if r["patient_id"] == patient_id}
    events = [e for e in REMINDER_EVENTS if e["reminder_id"] in rem_ids and datetime.fromisoformat(e["fired_at"]) >= cutoff]
    medications = [m for m in __import__("app.mock_data", fromlist=["MEDICATIONS"]).MEDICATIONS if m["patient_id"] == patient_id]
    user = USERS_BY_ID.get(patient_id, {})
    profile = __import__("app.mock_data", fromlist=["PATIENT_PROFILES"]).PATIENT_PROFILES.get(patient_id, {})
    summary = CareSummaryOut(
        patient_id=patient_id,
        patient_name=user.get("name", "Unknown"),
        generated_at=now.isoformat(),
        period_days=period_days,
        activity={"sessions": len(sessions), "average_accuracy": round(sum(s["accuracy"] for s in sessions) / len(sessions), 1) if sessions else 0.0},
        reminders={"total_events": len(events), "done": sum(e["action"] == "done" for e in events), "snoozed": sum(e["action"] == "snoozed" for e in events), "missed": sum(e["action"] == "missed" for e in events)},
        current_difficulty=profile.get("current_difficulty", {}),
        medications=medications,
        disclaimer="This is an activity and care-support summary, not a diagnostic report or medical advice.",
    )
    add_audit_entry(current_user["id"], patient_id, "export_care_summary")
    return summary


@router.get("/dashboard/{patient_id}/care-summary.csv", response_model=SummaryExportOut)
def export_care_summary_csv(patient_id: str, period_days: int = 30, current_user: dict = Depends(get_current_user)):
    summary = care_summary(patient_id, period_days, current_user)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["section", "field", "value"])
    writer.writerow(["activity", "sessions", summary.activity["sessions"]])
    writer.writerow(["activity", "average_accuracy", summary.activity["average_accuracy"]])
    for key, value in summary.reminders.items(): writer.writerow(["reminders", key, value])
    for game, tier in summary.current_difficulty.items(): writer.writerow(["difficulty", game, tier])
    writer.writerow(["notice", "disclaimer", summary.disclaimer])
    return SummaryExportOut(filename=f"{patient_id}-care-summary.csv", content_type="text/csv", content=buffer.getvalue(), disclaimer=summary.disclaimer)


@router.get("/dashboard/{patient_id}/trends", response_model=TrendResponse)
def dashboard_trends(
    patient_id: str,
    game_type: str = "memory",
    range: int = 30,
    current_user: dict = Depends(get_current_user),
):
    _assert_access(current_user, patient_id)
    add_audit_entry(current_user["id"], patient_id, f"read_trends_{game_type}")

    cutoff = datetime.now(timezone.utc) - timedelta(days=range)
    sessions = [
        s for s in GAME_SESSIONS
        if s["patient_id"] == patient_id
        and s["game_type"] == game_type
        and datetime.fromisoformat(s["completed_at"]) > cutoff
    ]
    sessions.sort(key=lambda s: s["completed_at"])

    points = [
        TrendPoint(
            date=s["completed_at"][:10],
            score=s["score"],
            accuracy=s["accuracy"],
            difficulty=s["difficulty"],
        )
        for s in sessions
    ]

    summary_text = f"No {game_type} sessions recorded in the last {range} days."
    if len(points) > 0:
        avg_acc = sum(p.accuracy for p in points) / len(points)
        trend_direction = "stable"
        if len(points) >= 3:
            first_half = points[:len(points)//2]
            second_half = points[len(points)//2:]
            avg_first = sum(p.accuracy for p in first_half) / len(first_half)
            avg_second = sum(p.accuracy for p in second_half) / len(second_half)
            if avg_second > avg_first + 5:
                trend_direction = "improving"
            elif avg_second < avg_first - 5:
                trend_direction = "declining"
        
        summary_text = (
            f"Over the last {range} days, accuracy in {game_type} games has been {trend_direction}, "
            f"averaging {avg_acc:.1f}%. "
            "This indicates general engagement level and is not a clinical diagnosis."
        )

    return TrendResponse(
        patient_id=patient_id, 
        game_type=game_type, 
        range_days=range, 
        points=points,
        plain_language_summary=summary_text
    )


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(
    patient_id: str | None = None,
    status: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    allowed = get_patients_for_user(current_user)
    results = [a for a in ALERTS if a["patient_id"] in allowed]
    if patient_id:
        results = [a for a in results if a["patient_id"] == patient_id]
    if status == "open":
        results = [a for a in results if not a["resolved"]]
    elif status == "resolved":
        results = [a for a in results if a["resolved"]]
    enriched = []
    for alert in results:
        item = dict(alert)
        if alert["type"] == "inactivity":
            item["explanation"] = "No completed game session was recorded during the configured inactivity window."
            item["observed_threshold"] = "48 hours without a completed game session"
            item["next_step"] = "Check in with the patient; this is not a diagnosis or emergency determination."
        elif alert["type"] == "missed_reminder":
            item["explanation"] = "A reminder event was marked missed."
            item["observed_threshold"] = "One missed reminder event"
            item["next_step"] = "Check the routine and contact the patient if support is needed."
        enriched.append(item)
    return enriched
