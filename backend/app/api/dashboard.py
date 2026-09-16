from datetime import datetime, timezone, timedelta
import csv
import io
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.db import get_db
from app.api.dependencies import get_current_user
from app.core.crud import get_patients_for_user, add_audit_entry
from app.models import (
    GameSession, Reminder, ReminderEvent, Alert, PatientProfile, User, Medication
)
from app.api.schemas import DashboardSummary, TrendResponse, TrendPoint, AlertOut, CareSummaryOut, SummaryExportOut

router = APIRouter(tags=["dashboard"])

def _assert_access(current_user: dict, patient_id: str, db: Session):
    if patient_id not in get_patients_for_user(current_user, db):
        raise HTTPException(status_code=403, detail="Not authorised")


@router.get("/dashboard/{patient_id}/summary", response_model=DashboardSummary)
def dashboard_summary(patient_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _assert_access(current_user, patient_id, db)
    add_audit_entry(db, current_user["id"], patient_id, "read_dashboard_summary")

    patient_sessions = db.query(GameSession).filter(GameSession.patient_id == patient_id).order_by(GameSession.completed_at.desc()).all()
    now = datetime.now(timezone.utc)
    cutoff_7d = now - timedelta(days=7)

    sessions_7d = [s for s in patient_sessions if s.completed_at > cutoff_7d]
    avg_acc_7d = sum(s.accuracy_pct for s in sessions_7d) / len(sessions_7d) if sessions_7d else 0.0

    session_dates = sorted(set(s.completed_at.date() for s in patient_sessions), reverse=True)
    streak = 0
    check_date = now.date()
    for d in session_dates:
        if d == check_date or d == check_date - timedelta(days=1):
            streak += 1
            check_date = d - timedelta(days=1)
        else:
            break

    reminders = db.query(Reminder).filter(Reminder.patient_id == patient_id).all()
    rem_ids = [r.id for r in reminders]
    events = db.query(ReminderEvent).filter(ReminderEvent.reminder_id.in_(rem_ids)).all()
    
    done_count = sum(1 for e in events if e.status == "completed")
    adherence = (done_count / len(events) * 100) if events else 100.0

    last_session_at = patient_sessions[0].completed_at if patient_sessions else None
    inactivity_h = 0.0
    if last_session_at:
        inactivity_h = (now - last_session_at).total_seconds() / 3600

    profile = db.query(PatientProfile).filter(PatientProfile.user_id == patient_id).first()
    user = db.query(User).filter(User.id == patient_id).first()

    diffs = {}
    if profile:
        diffs = {
            "memory": profile.difficulty_memory,
            "attention": profile.difficulty_attention,
            "routine": profile.difficulty_routine,
            "recognition": profile.difficulty_recognition
        }

    return DashboardSummary(
        patient_id=patient_id,
        patient_name=user.name if user else "Unknown",
        total_sessions=len(patient_sessions),
        sessions_last_7_days=len(sessions_7d),
        streak_days=streak,
        avg_accuracy_last_7_days=round(avg_acc_7d, 1),
        reminder_adherence_pct=round(adherence, 1),
        last_session_at=str(last_session_at) if last_session_at else None,
        inactivity_hours=round(inactivity_h, 1),
        current_difficulty=diffs,
    )


@router.get("/dashboard/{patient_id}/care-summary", response_model=CareSummaryOut)
def care_summary(patient_id: str, period_days: int = 30, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _assert_access(current_user, patient_id, db)
    period_days = max(1, min(period_days, 365))
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=period_days)
    
    sessions = db.query(GameSession).filter(GameSession.patient_id == patient_id, GameSession.completed_at >= cutoff).all()
    
    reminders = db.query(Reminder).filter(Reminder.patient_id == patient_id).all()
    rem_ids = [r.id for r in reminders]
    events = db.query(ReminderEvent).filter(ReminderEvent.reminder_id.in_(rem_ids), ReminderEvent.scheduled_time >= cutoff).all()
    
    medications = db.query(Medication).filter(Medication.patient_id == patient_id).all()
    user = db.query(User).filter(User.id == patient_id).first()
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == patient_id).first()
    
    diffs = {}
    if profile:
        diffs = {
            "memory": profile.difficulty_memory,
            "attention": profile.difficulty_attention,
            "routine": profile.difficulty_routine,
            "recognition": profile.difficulty_recognition
        }
        
    summary = CareSummaryOut(
        patient_id=patient_id,
        patient_name=user.name if user else "Unknown",
        generated_at=now.isoformat(),
        period_days=period_days,
        activity={"sessions": len(sessions), "average_accuracy": round(sum(s.accuracy_pct for s in sessions) / len(sessions), 1) if sessions else 0.0},
        reminders={"total_events": len(events), "done": sum(e.status == "completed" for e in events), "snoozed": 0, "missed": sum(e.status == "missed" for e in events)},
        current_difficulty=diffs,
        medications=[m.__dict__ for m in medications],
        disclaimer="This is an activity and care-support summary, not a diagnostic report or medical advice.",
    )
    add_audit_entry(db, current_user["id"], patient_id, "export_care_summary")
    return summary


@router.get("/dashboard/{patient_id}/care-summary.csv", response_model=SummaryExportOut)
def export_care_summary_csv(patient_id: str, period_days: int = 30, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    summary = care_summary(patient_id, period_days, current_user, db)
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
    db: Session = Depends(get_db)
):
    _assert_access(current_user, patient_id, db)
    add_audit_entry(db, current_user["id"], patient_id, f"read_trends_{game_type}")

    cutoff = datetime.now(timezone.utc) - timedelta(days=range)
    sessions = db.query(GameSession).filter(
        GameSession.patient_id == patient_id,
        GameSession.game_type == game_type,
        GameSession.completed_at > cutoff
    ).order_by(GameSession.completed_at).all()

    points = [
        TrendPoint(
            date=str(s.completed_at)[:10],
            score=s.score,
            accuracy=s.accuracy_pct,
            difficulty=s.difficulty,
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
    db: Session = Depends(get_db)
):
    allowed = get_patients_for_user(current_user, db)
    query = db.query(Alert).filter(Alert.patient_id.in_(allowed))
    
    if patient_id:
        query = query.filter(Alert.patient_id == patient_id)
        
    if status == "open":
        query = query.filter(Alert.resolved == False)
    elif status == "resolved":
        query = query.filter(Alert.resolved == True)
        
    alerts = query.all()
    enriched = []
    
    for alert in alerts:
        item = {
            "id": str(alert.id),
            "patient_id": str(alert.patient_id),
            "type": alert.type,
            "triggered_at": str(alert.triggered_at),
            "channel": alert.channel,
            "delivered": alert.delivered,
            "resolved": alert.resolved,
            "simulation_label": alert.simulation_label,
            "explanation": alert.explanation,
            "observed_threshold": alert.observed_threshold,
            "next_step": alert.next_step
        }
        
        if not item.get("explanation"):
            if alert.type == "inactivity":
                item["explanation"] = "No completed game session was recorded during the configured inactivity window."
                item["observed_threshold"] = "48 hours without a completed game session"
                item["next_step"] = "Check in with the patient; this is not a diagnosis or emergency determination."
            elif alert.type == "missed_reminder":
                item["explanation"] = "A reminder event was marked missed."
                item["observed_threshold"] = "One missed reminder event"
                item["next_step"] = "Check the routine and contact the patient if support is needed."
                
        enriched.append(item)
        
    return enriched
