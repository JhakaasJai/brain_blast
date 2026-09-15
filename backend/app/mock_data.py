"""
# MOCK: In-memory data layer — replaces PostgreSQL for the prototype.
#
# All data is seeded at startup from plain Python dicts.
# Every REST endpoint reads/writes these structures.
# Swap this module for a real SQLAlchemy session factory to move to production.
#
# Accounts
# --------
#   Patients
#     patient1@ner.in   / pass: patient1pass  (Assam/Assamese, Easy)
#     patient2@ner.in   / pass: patient2pass  (Meghalaya/Khasi, Medium)
#     patient3@ner.in   / pass: patient3pass  (Manipur/Meitei, Hard)
#   Caregivers
#     caregiver1@ner.in / pass: cg1pass  (linked to patient1 + patient3)
#     caregiver2@ner.in / pass: cg2pass  (linked to patient2)
#   Health Worker
#     hw1@ner.in        / pass: hw1pass   (sees patient1 + patient2 + patient3)
#   Admin
#     admin@ner.in      / pass: adminpass
"""

import uuid
from datetime import datetime, timedelta, timezone
from copy import deepcopy

from app.core.auth import get_password_hash

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)

def _days_ago(n: int) -> datetime:
    return _now() - timedelta(days=n)

def _uid() -> str:
    return str(uuid.uuid4())

# ──────────────────────────────────────────────────────────────────────────────
# Caregiver Education Library
# ──────────────────────────────────────────────────────────────────────────────

EDUCATION_ARTICLES: list[dict] = [
    {
        "id": "edu-communication",
        "title": "Communicating with patience and clarity",
        "category": "communication",
        "summary": "Simple ways to reduce pressure and support a person with memory changes.",
        "body": "Use short sentences, ask one question at a time, and allow extra time for a reply. Offer two simple choices instead of correcting every detail. Speak calmly and respectfully, and focus on what the person is trying to communicate.",
        "language": "en",
        "source_note": "General educational prototype content; discuss individual care with a qualified clinician.",
        "updated_at": _days_ago(7).isoformat(),
        "read_time_minutes": 2,
    },
    {
        "id": "edu-routines",
        "title": "Making daily routines easier",
        "category": "daily living",
        "summary": "Use familiar cues and small steps to support everyday activities.",
        "body": "Keep important items in consistent places. Break activities into one step at a time and use visible reminders. Praise effort and allow the person to do the parts they can safely manage.",
        "language": "en",
        "source_note": "General educational prototype content; discuss individual care with a qualified clinician.",
        "updated_at": _days_ago(5).isoformat(),
        "read_time_minutes": 2,
    },
    {
        "id": "edu-safety",
        "title": "A calm approach to home safety",
        "category": "safety",
        "summary": "A practical review of common hazards without taking away independence.",
        "body": "Keep walkways clear, improve lighting, and place frequently used items within easy reach. Review medicine storage and emergency contacts with the care team. Make changes respectfully and include the person in decisions whenever possible.",
        "language": "en",
        "source_note": "General educational prototype content; discuss individual care with a qualified clinician.",
        "updated_at": _days_ago(3).isoformat(),
        "read_time_minutes": 3,
    },
]

EDUCATION_PROGRESS: list[dict] = []

# ──────────────────────────────────────────────────────────────────────────────
# Users
# ──────────────────────────────────────────────────────────────────────────────

USERS: list[dict] = [
    {
        "id": "user-patient-1",
        "role": "patient",
        "name": "Rina Borah",
        "phone": "+919876540001",
        "preferred_language": "as",        # Assamese
        "state_region": "Assam",
        "password_hash": get_password_hash("patient1pass"),
        "created_at": _days_ago(45).isoformat(),
    },
    {
        "id": "user-patient-2",
        "role": "patient",
        "name": "Banshan Lyngdoh",
        "phone": "+919876540002",
        "preferred_language": "kha",       # Khasi
        "state_region": "Meghalaya",
        "password_hash": get_password_hash("patient2pass"),
        "created_at": _days_ago(38).isoformat(),
    },
    {
        "id": "user-patient-3",
        "role": "patient",
        "name": "Thoibi Haobijam",
        "phone": "+919876540003",
        "preferred_language": "mni",       # Meitei/Manipuri
        "state_region": "Manipur",
        "password_hash": get_password_hash("patient3pass"),
        "created_at": _days_ago(30).isoformat(),
    },
    {
        "id": "user-caregiver-1",
        "role": "caregiver",
        "name": "Dipak Borah",
        "phone": "+919876540011",
        "preferred_language": "en",
        "state_region": "Assam",
        "password_hash": get_password_hash("cg1pass"),
        "created_at": _days_ago(44).isoformat(),
    },
    {
        "id": "user-caregiver-2",
        "role": "caregiver",
        "name": "Mebanlin Lyngdoh",
        "phone": "+919876540012",
        "preferred_language": "en",
        "state_region": "Meghalaya",
        "password_hash": get_password_hash("cg2pass"),
        "created_at": _days_ago(37).isoformat(),
    },
    {
        "id": "user-hw-1",
        "role": "health_worker",
        "name": "Priya Sharma",
        "phone": "+919876540021",
        "preferred_language": "hi",
        "state_region": "Assam",
        "password_hash": get_password_hash("hw1pass"),
        "created_at": _days_ago(50).isoformat(),
    },
    {
        "id": "user-admin-1",
        "role": "admin",
        "name": "Admin User",
        "phone": "+919876540099",
        "preferred_language": "en",
        "state_region": "All",
        "password_hash": get_password_hash("adminpass"),
        "created_at": _days_ago(60).isoformat(),
    },
]

# fast lookup
USERS_BY_ID: dict[str, dict] = {u["id"]: u for u in USERS}
USERS_BY_PHONE: dict[str, dict] = {u["phone"]: u for u in USERS}
USERS_BY_EMAIL_KEY: dict[str, dict] = {}

# We use "email" as login key (the build-agent-prompt uses email-style accounts)
_EMAIL_MAP = {
    "patient1@ner.in": "user-patient-1",
    "patient2@ner.in": "user-patient-2",
    "patient3@ner.in": "user-patient-3",
    "caregiver1@ner.in": "user-caregiver-1",
    "caregiver2@ner.in": "user-caregiver-2",
    "hw1@ner.in": "user-hw-1",
    "admin@ner.in": "user-admin-1",
}
for email, uid in _EMAIL_MAP.items():
    USERS_BY_EMAIL_KEY[email] = USERS_BY_ID[uid]


def get_user_by_email(email: str) -> dict | None:
    return USERS_BY_EMAIL_KEY.get(email)


def get_user_by_id(uid: str) -> dict | None:
    return USERS_BY_ID.get(uid)


# ──────────────────────────────────────────────────────────────────────────────
# Patient Profiles
# ──────────────────────────────────────────────────────────────────────────────

PATIENT_PROFILES: dict[str, dict] = {
    "user-patient-1": {
        "user_id": "user-patient-1",
        "dob_or_age": 72,
        "dementia_stage_note": "Mild — occasional word-finding difficulty. Follows routines well.",
        "theme_preference": "assam_village",
        "onboarding_complete": True,
        "guardian_consent_at": _days_ago(44).isoformat(),
        "preferred_name": "Rina",
        "likes": ["tea", "Bihu songs", "family photos"],
        "dislikes": [],
        "routine_notes": "Morning tea at 07:30; rest after lunch.",
        "mobility_notes": "Walks independently; avoid slippery floors.",
        "vision_notes": "Uses reading glasses.",
        "hearing_notes": " prefers slow, clear speech.",
        "current_difficulty": {
            "memory": "easy",
            "attention": "easy",
            "routine": "medium",
            "recognition": "easy",
        },
    },
    "user-patient-2": {
        "user_id": "user-patient-2",
        "dob_or_age": 68,
        "dementia_stage_note": "Moderate — needs prompting for daily tasks. Responds well to visual cues.",
        "theme_preference": "meghalaya_highlands",
        "onboarding_complete": True,
        "guardian_consent_at": _days_ago(37).isoformat(),
        "current_difficulty": {
            "memory": "medium",
            "attention": "medium",
            "routine": "easy",
            "recognition": "medium",
        },
    },
    "user-patient-3": {
        "user_id": "user-patient-3",
        "dob_or_age": 65,
        "dementia_stage_note": "Mild — early detection. High engagement with cultural visuals.",
        "theme_preference": "manipur_festival",
        "onboarding_complete": True,
        "guardian_consent_at": _days_ago(29).isoformat(),
        "current_difficulty": {
            "memory": "hard",
            "attention": "medium",
            "routine": "medium",
            "recognition": "hard",
        },
    },
}

# Emergency contacts (prototype data; production must encrypt and consent-gate this data)
EMERGENCY_CONTACTS: list[dict] = [
    {"id": "contact-p1-1", "patient_id": "user-patient-1", "name": "Dipak Borah", "phone": "+919****0011", "relationship": "Son", "is_primary": True},
    {"id": "contact-p1-2", "patient_id": "user-patient-1", "name": "Local Health Worker", "phone": "+919****0021", "relationship": "Health worker", "is_primary": False},
    {"id": "contact-p2-1", "patient_id": "user-patient-2", "name": "Mebanlin Lyngdoh", "phone": "+919****0012", "relationship": "Daughter", "is_primary": True},
]

# Medication records contain instructions but never automated dose advice.
MEDICATIONS: list[dict] = [
    {"id": "med-p1-1", "patient_id": "user-patient-1", "name": "Blood pressure tablet", "dose": "1 tablet", "form": "tablet", "instructions": "Take with water as directed by your clinician.", "prescribing_clinician": "Gauhati Medical College", "start_date": None, "end_date": None, "refill_date": None, "active": True, "missed_dose_guidance": "Do not take an extra dose. Follow your clinician or pharmacist instructions."},
]

# Safety check-ins intentionally store only the latest check-in per patient.
# No continuous GPS or location history is collected in this prototype.
SAFETY_CHECK_INS: dict[str, dict] = {}

# ──────────────────────────────────────────────────────────────────────────────
# Reminiscence Therapy
# Prompts seeded by caregivers; notes written by patients.
# All content is text-based (no media upload in prototype).
# ──────────────────────────────────────────────────────────────────────────────

REMINISCENCE_PROMPTS: list[dict] = [
    {
        "id": "rprompt-1",
        "patient_id": "user-patient-1",
        "theme": "family",
        "title": "Your family home",
        "prompt_text": "Can you describe the home you grew up in? What did it look like, smell like, or sound like?",
        "created_by": "user-caregiver-1",
        "created_at": _days_ago(10).isoformat(),
    },
    {
        "id": "rprompt-2",
        "patient_id": "user-patient-1",
        "theme": "festivals",
        "title": "Bihu celebrations",
        "prompt_text": "What is your favourite memory of Bihu? Who were you with and what did you do?",
        "created_by": "user-caregiver-1",
        "created_at": _days_ago(8).isoformat(),
    },
    {
        "id": "rprompt-3",
        "patient_id": "user-patient-1",
        "theme": "food",
        "title": "A favourite meal",
        "prompt_text": "What is a meal that always made you feel at home? Who cooked it?",
        "created_by": "user-caregiver-1",
        "created_at": _days_ago(5).isoformat(),
    },
    {
        "id": "rprompt-4",
        "patient_id": "user-patient-2",
        "theme": "seasons",
        "title": "The monsoon hills",
        "prompt_text": "What do you remember about the rainy season in the hills? What sounds and sights come to mind?",
        "created_by": "user-caregiver-2",
        "created_at": _days_ago(7).isoformat(),
    },
    {
        "id": "rprompt-5",
        "patient_id": "user-patient-3",
        "theme": "festivals",
        "title": "Yaoshang memories",
        "prompt_text": "Tell me about a Yaoshang festival you remember well. What games did you play?",
        "created_by": "user-caregiver-1",
        "created_at": _days_ago(6).isoformat(),
    },
]

REMINISCENCE_NOTES: list[dict] = [
    {
        "id": "rnote-1",
        "prompt_id": "rprompt-1",
        "patient_id": "user-patient-1",
        "note_text": "Our house had a red tin roof and a big tulsi plant at the front door. My mother always cooked in the back kitchen.",
        "recorded_at": _days_ago(9).isoformat(),
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Social Connection messages
# Async message thread between patient and care team (no real-time; prototype).
# PRODUCTION: replace with DB table + FCM/SMS push per send.
# ──────────────────────────────────────────────────────────────────────────────

SOCIAL_MESSAGES: list[dict] = [
    {
        "id": "smsg-1",
        "patient_id": "user-patient-1",
        "sender_id": "user-caregiver-1",
        "sender_name": "Dipak Borah",
        "sender_role": "caregiver",
        "message_text": "How are you feeling today, Ma? Did you have your morning tea?",
        "sent_at": _days_ago(1).isoformat(),
    },
    {
        "id": "smsg-2",
        "patient_id": "user-patient-1",
        "sender_id": "user-patient-1",
        "sender_name": "Rina Borah",
        "sender_role": "patient",
        "message_text": "Yes, I had tea. The garden looks nice today.",
        "sent_at": _days_ago(0).isoformat(),
    },
    {
        "id": "smsg-3",
        "patient_id": "user-patient-2",
        "sender_id": "user-caregiver-2",
        "sender_name": "Mebanlin Lyngdoh",
        "sender_role": "caregiver",
        "message_text": "Good morning! Don't forget your morning exercises.",
        "sent_at": _days_ago(1).isoformat(),
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Daily Living Assistance
# Simple daily checklist per patient. Prototype resets on server restart.
# PRODUCTION: persist per-day in DB; reset nightly via scheduled job.
# ──────────────────────────────────────────────────────────────────────────────

def _default_tasks(patient_id: str) -> list[dict]:
    return [
        {"id": f"dt-{patient_id}-1", "patient_id": patient_id, "label": "Morning wash and get dressed", "category": "morning", "done": False, "done_at": None},
        {"id": f"dt-{patient_id}-2", "patient_id": patient_id, "label": "Have breakfast", "category": "meals", "done": False, "done_at": None},
        {"id": f"dt-{patient_id}-3", "patient_id": patient_id, "label": "Take morning medication", "category": "morning", "done": False, "done_at": None},
        {"id": f"dt-{patient_id}-4", "patient_id": patient_id, "label": "Drink a glass of water", "category": "hygiene", "done": False, "done_at": None},
        {"id": f"dt-{patient_id}-5", "patient_id": patient_id, "label": "Short walk or stretching", "category": "exercise", "done": False, "done_at": None},
        {"id": f"dt-{patient_id}-6", "patient_id": patient_id, "label": "Have lunch", "category": "meals", "done": False, "done_at": None},
        {"id": f"dt-{patient_id}-7", "patient_id": patient_id, "label": "Rest after lunch", "category": "evening", "done": False, "done_at": None},
        {"id": f"dt-{patient_id}-8", "patient_id": patient_id, "label": "Have dinner", "category": "meals", "done": False, "done_at": None},
        {"id": f"dt-{patient_id}-9", "patient_id": patient_id, "label": "Take evening medication", "category": "evening", "done": False, "done_at": None},
        {"id": f"dt-{patient_id}-10", "patient_id": patient_id, "label": "Wash hands and brush teeth", "category": "hygiene", "done": False, "done_at": None},
    ]

# keyed by patient_id
DAILY_TASKS: dict[str, list[dict]] = {
    "user-patient-1": _default_tasks("user-patient-1"),
    "user-patient-2": _default_tasks("user-patient-2"),
    "user-patient-3": _default_tasks("user-patient-3"),
}

# ──────────────────────────────────────────────────────────────────────────────
# Sleep and Mood Check-ins
# One check-in per day per patient (prototype stores all; production: 1/day limit enforced in DB).
# ──────────────────────────────────────────────────────────────────────────────

MOOD_CHECKINS: list[dict] = [
    {"id": "mood-p1-1", "patient_id": "user-patient-1", "mood_score": 4, "sleep_hours": 7.0, "sleep_quality": "good", "notes": "Felt rested.", "recorded_at": _days_ago(2).isoformat()},
    {"id": "mood-p1-2", "patient_id": "user-patient-1", "mood_score": 3, "sleep_hours": 5.5, "sleep_quality": "fair", "notes": "Woke up once.", "recorded_at": _days_ago(1).isoformat()},
    {"id": "mood-p2-1", "patient_id": "user-patient-2", "mood_score": 2, "sleep_hours": 6.0, "sleep_quality": "poor", "notes": None, "recorded_at": _days_ago(1).isoformat()},
]

# Physical activity logs; prototype text-based, no wearable integration.
ACTIVITY_LOGS: list[dict] = [
    {"id": "activity-p1-1", "patient_id": "user-patient-1", "activity_type": "walk", "duration_minutes": 15, "intensity": "light", "notes": "Walked in the garden.", "logged_at": _days_ago(1).isoformat()},
    {"id": "activity-p1-2", "patient_id": "user-patient-1", "activity_type": "stretch", "duration_minutes": 10, "intensity": "light", "notes": None, "logged_at": _days_ago(2).isoformat()},
    {"id": "activity-p2-1", "patient_id": "user-patient-2", "activity_type": "walk", "duration_minutes": 20, "intensity": "moderate", "notes": None, "logged_at": _days_ago(1).isoformat()},
]

# ──────────────────────────────────────────────────────────────────────────────
# Caregiver Links
# ──────────────────────────────────────────────────────────────────────────────

CAREGIVER_LINKS: list[dict] = [
    {"id": "link-1", "caregiver_id": "user-caregiver-1", "patient_id": "user-patient-1",
     "relationship": "Son", "status": "active"},
    {"id": "link-2", "caregiver_id": "user-caregiver-1", "patient_id": "user-patient-3",
     "relationship": "Neighbour", "status": "active"},
    {"id": "link-3", "caregiver_id": "user-caregiver-2", "patient_id": "user-patient-2",
     "relationship": "Daughter", "status": "active"},
]

# Health worker cluster (all 3 patients)
HW_PATIENT_MAP: dict[str, list[str]] = {
    "user-hw-1": ["user-patient-1", "user-patient-2", "user-patient-3"],
}


def get_patients_for_user(user: dict) -> list[str]:
    """Return list of patient IDs a caregiver/hw/admin is allowed to see."""
    role = user["role"]
    uid = user["id"]
    if role == "patient":
        return [uid]
    if role == "caregiver":
        return [lk["patient_id"] for lk in CAREGIVER_LINKS
                if lk["caregiver_id"] == uid and lk["status"] == "active"]
    if role == "health_worker":
        return HW_PATIENT_MAP.get(uid, [])
    if role == "admin":
        return [u["id"] for u in USERS if u["role"] == "patient"]
    return []

# ──────────────────────────────────────────────────────────────────────────────
# Game Sessions (~18 per patient over 30 days, 4 game types)
# ──────────────────────────────────────────────────────────────────────────────

_GAME_TYPES = ["memory", "attention", "routine", "recognition"]
_DIFFICULTIES = ["easy", "medium", "hard"]

def _make_sessions(patient_id: str, diff_profile: dict, count: int = 18) -> list[dict]:
    sessions = []
    import math, random
    random.seed(hash(patient_id) % (2**31))

    for i in range(count):
        day_offset = int((i / count) * 30)
        game_type = _GAME_TYPES[i % 4]
        diff = diff_profile.get(game_type, "easy")
        # generate realistic scores: slight upward trend with noise
        base_accuracy = 55 + (i / count) * 30 + random.uniform(-12, 12)
        accuracy = max(10, min(100, base_accuracy))
        score = int(accuracy * 10)
        reaction_ms = int(3000 - (accuracy / 100) * 1500 + random.uniform(-200, 200))
        errors = max(0, int((100 - accuracy) / 20))

        sessions.append({
            "id": _uid(),
            "patient_id": patient_id,
            "game_type": game_type,
            "difficulty": diff,
            "score": score,
            "accuracy": round(accuracy, 1),
            "reaction_time_avg_ms": reaction_ms,
            "errors": errors,
            "started_at": _days_ago(30 - day_offset).isoformat(),
            "completed_at": (_days_ago(30 - day_offset) + timedelta(minutes=15)).isoformat(),
            "client_uuid": _uid(),
            "sync_status": "synced",
        })
    return sessions

GAME_SESSIONS: list[dict] = (
    _make_sessions("user-patient-1", PATIENT_PROFILES["user-patient-1"]["current_difficulty"])
    + _make_sessions("user-patient-2", PATIENT_PROFILES["user-patient-2"]["current_difficulty"])
    + _make_sessions("user-patient-3", PATIENT_PROFILES["user-patient-3"]["current_difficulty"])
)

# ──────────────────────────────────────────────────────────────────────────────
# Difficulty Log
# ──────────────────────────────────────────────────────────────────────────────

DIFFICULTY_LOG: list[dict] = [
    # Patient 1 — memory tier went easy → medium (accuracy climbed)
    {
        "id": _uid(), "patient_id": "user-patient-1", "game_type": "memory",
        "previous_tier": "easy", "new_tier": "medium",
        "decision_source": "rule",
        "inputs_json": {"last_3_accuracy": [82.1, 85.3, 81.7], "rule": "accuracy>80 on last 3"},
        "decided_at": _days_ago(15).isoformat(),
    },
    # Patient 1 — routine already medium from onboarding; dropped to easy then recovered
    {
        "id": _uid(), "patient_id": "user-patient-1", "game_type": "routine",
        "previous_tier": "medium", "new_tier": "easy",
        "decision_source": "rule",
        "inputs_json": {"last_3_accuracy": [44.0, 48.5, 41.2], "rule": "accuracy<50 on last 3"},
        "decided_at": _days_ago(22).isoformat(),
    },
    {
        "id": _uid(), "patient_id": "user-patient-1", "game_type": "routine",
        "previous_tier": "easy", "new_tier": "medium",
        "decision_source": "rule",
        "inputs_json": {"last_3_accuracy": [81.0, 83.5, 88.0], "rule": "accuracy>80 on last 3"},
        "decided_at": _days_ago(8).isoformat(),
    },
    # Patient 2 — attention raised
    {
        "id": _uid(), "patient_id": "user-patient-2", "game_type": "attention",
        "previous_tier": "easy", "new_tier": "medium",
        "decision_source": "rule",
        "inputs_json": {"last_3_accuracy": [83.4, 87.1, 90.0], "rule": "accuracy>80 on last 3"},
        "decided_at": _days_ago(12).isoformat(),
    },
    # Patient 3 — memory raised to hard
    {
        "id": _uid(), "patient_id": "user-patient-3", "game_type": "memory",
        "previous_tier": "medium", "new_tier": "hard",
        "decision_source": "rule",
        "inputs_json": {"last_3_accuracy": [91.2, 88.5, 93.1], "rule": "accuracy>80 on last 3"},
        "decided_at": _days_ago(10).isoformat(),
    },
    {
        "id": _uid(), "patient_id": "user-patient-3", "game_type": "recognition",
        "previous_tier": "medium", "new_tier": "hard",
        "decision_source": "rule",
        "inputs_json": {"last_3_accuracy": [88.0, 92.3, 89.7], "rule": "accuracy>80 on last 3"},
        "decided_at": _days_ago(5).isoformat(),
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Reminders
# ──────────────────────────────────────────────────────────────────────────────

REMINDERS: list[dict] = [
    # Patient 1 reminders
    {"id": "rem-p1-1", "patient_id": "user-patient-1", "category": "medicine",
     "message": "Take your morning blood pressure tablet with water.",
     "schedule_rule": {"type": "daily", "time": "08:00"}, "active": True},
    {"id": "rem-p1-2", "patient_id": "user-patient-1", "category": "hydration",
     "message": "Drink a full glass of water now.",
     "schedule_rule": {"type": "interval_hours", "every": 3}, "active": True},
    {"id": "rem-p1-3", "patient_id": "user-patient-1", "category": "activity",
     "message": "Time for your morning walk outside.",
     "schedule_rule": {"type": "daily", "time": "07:00"}, "active": True},
    {"id": "rem-p1-4", "patient_id": "user-patient-1", "category": "appointment",
     "message": "Doctor visit at Gauhati Medical College — 11am.",
     "schedule_rule": {"type": "once", "at": _days_ago(-3).isoformat()}, "active": True},
    {"id": "rem-p1-5", "patient_id": "user-patient-1", "category": "medicine",
     "message": "Take your evening vitamin D tablet.",
     "schedule_rule": {"type": "daily", "time": "19:00"}, "active": True},

    # Patient 2 reminders
    {"id": "rem-p2-1", "patient_id": "user-patient-2", "category": "medicine",
     "message": "Take your Alzheimer's medication with food.",
     "schedule_rule": {"type": "daily", "time": "09:00"}, "active": True},
    {"id": "rem-p2-2", "patient_id": "user-patient-2", "category": "hydration",
     "message": "Drink water — stay hydrated in the hills!",
     "schedule_rule": {"type": "interval_hours", "every": 4}, "active": True},
    {"id": "rem-p2-3", "patient_id": "user-patient-2", "category": "activity",
     "message": "Do your 10-minute stretching exercise.",
     "schedule_rule": {"type": "daily", "time": "10:30"}, "active": True},
    {"id": "rem-p2-4", "patient_id": "user-patient-2", "category": "appointment",
     "message": "Community health check at Nongkynmaw PHC.",
     "schedule_rule": {"type": "once", "at": _days_ago(-7).isoformat()}, "active": True},
    {"id": "rem-p2-5", "patient_id": "user-patient-2", "category": "medicine",
     "message": "Evening dose — calcium tablet.",
     "schedule_rule": {"type": "daily", "time": "20:00"}, "active": True},
    {"id": "rem-p2-6", "patient_id": "user-patient-2", "category": "activity",
     "message": "Play a memory game for 15 minutes.",
     "schedule_rule": {"type": "daily", "time": "15:00"}, "active": True},

    # Patient 3 reminders
    {"id": "rem-p3-1", "patient_id": "user-patient-3", "category": "medicine",
     "message": "Morning medication — take with warm water.",
     "schedule_rule": {"type": "daily", "time": "07:30"}, "active": True},
    {"id": "rem-p3-2", "patient_id": "user-patient-3", "category": "hydration",
     "message": "Drink a glass of water.",
     "schedule_rule": {"type": "interval_hours", "every": 3}, "active": True},
    {"id": "rem-p3-3", "patient_id": "user-patient-3", "category": "activity",
     "message": "Attend Sankirtana practice at the community hall.",
     "schedule_rule": {"type": "weekly", "day": "saturday", "time": "17:00"}, "active": True},
    {"id": "rem-p3-4", "patient_id": "user-patient-3", "category": "appointment",
     "message": "Neurology review at RIMS Imphal — 2pm.",
     "schedule_rule": {"type": "once", "at": _days_ago(-5).isoformat()}, "active": True},
    {"id": "rem-p3-5", "patient_id": "user-patient-3", "category": "medicine",
     "message": "Evening medication.",
     "schedule_rule": {"type": "daily", "time": "19:30"}, "active": True},
]

REMINDERS_BY_ID: dict[str, dict] = {r["id"]: r for r in REMINDERS}

# ──────────────────────────────────────────────────────────────────────────────
# Reminder Events (mix of done/snoozed/missed — adherence not 100%)
# ──────────────────────────────────────────────────────────────────────────────

def _rem_event(rem_id: str, patient_id: str, action: str, days_ago_val: int) -> dict:
    return {
        "id": _uid(), "reminder_id": rem_id, "patient_id": patient_id,
        "fired_at": _days_ago(days_ago_val).isoformat(),
        "action": action,   # done / snoozed / missed
        "client_uuid": _uid(), "sync_status": "synced",
    }

REMINDER_EVENTS: list[dict] = [
    # Patient 1
    _rem_event("rem-p1-1", "user-patient-1", "done",    1),
    _rem_event("rem-p1-1", "user-patient-1", "done",    2),
    _rem_event("rem-p1-1", "user-patient-1", "missed",  3),   # ← missed
    _rem_event("rem-p1-1", "user-patient-1", "done",    4),
    _rem_event("rem-p1-2", "user-patient-1", "snoozed", 1),
    _rem_event("rem-p1-2", "user-patient-1", "done",    2),
    _rem_event("rem-p1-3", "user-patient-1", "done",    1),
    _rem_event("rem-p1-3", "user-patient-1", "missed",  2),
    _rem_event("rem-p1-5", "user-patient-1", "done",    1),
    _rem_event("rem-p1-5", "user-patient-1", "snoozed", 2),
    # Patient 2
    _rem_event("rem-p2-1", "user-patient-2", "done",    1),
    _rem_event("rem-p2-1", "user-patient-2", "missed",  2),   # ← missed
    _rem_event("rem-p2-1", "user-patient-2", "done",    3),
    _rem_event("rem-p2-2", "user-patient-2", "done",    1),
    _rem_event("rem-p2-3", "user-patient-2", "snoozed", 1),
    _rem_event("rem-p2-3", "user-patient-2", "done",    2),
    _rem_event("rem-p2-5", "user-patient-2", "done",    1),
    _rem_event("rem-p2-6", "user-patient-2", "missed",  1),
    # Patient 3
    _rem_event("rem-p3-1", "user-patient-3", "done",    1),
    _rem_event("rem-p3-1", "user-patient-3", "done",    2),
    _rem_event("rem-p3-2", "user-patient-3", "snoozed", 1),
    _rem_event("rem-p3-3", "user-patient-3", "done",    6),   # last saturday
    _rem_event("rem-p3-5", "user-patient-3", "done",    1),
    _rem_event("rem-p3-5", "user-patient-3", "missed",  2),
]

# ──────────────────────────────────────────────────────────────────────────────
# Alerts
# ──────────────────────────────────────────────────────────────────────────────

ALERTS: list[dict] = [
    {
        "id": "alert-1",
        "patient_id": "user-patient-2",
        "type": "inactivity",
        "triggered_at": _days_ago(3).isoformat(),
        "channel": "push",
        "delivered": True,
        "resolved": False,
        # MOCK: in-app notification shown; no real FCM call made
        "simulation_label": "[SMS SIMULATION] Banshan Lyngdoh has not played a game in 48+ hours. SMS sent to caregiver +919876540012.",
    },
    {
        "id": "alert-2",
        "patient_id": "user-patient-1",
        "type": "missed_reminder",
        "triggered_at": _days_ago(3).isoformat(),
        "channel": "sms",
        "delivered": True,
        "resolved": True,
        # MOCK: SMS simulated only — no Twilio/MSG91 call made
        "simulation_label": "[SMS SIMULATION] Rina Borah missed morning blood pressure tablet reminder. SMS sent to caregiver +919876540011.",
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Caregiver notes and handover entries.
CAREGIVER_NOTES: list[dict] = []

# Audit Log
# ──────────────────────────────────────────────────────────────────────────────

AUDIT_LOG: list[dict] = []


def add_audit_entry(actor_id: str, patient_id: str, action: str) -> None:
    AUDIT_LOG.append({
        "id": _uid(),
        "actor_id": actor_id,
        "patient_id": patient_id,
        "action": action,
        "accessed_at": _now().isoformat(),
    })


# ──────────────────────────────────────────────────────────────────────────────
# Notifications log (simulated push + SMS, shown in-app)
# ──────────────────────────────────────────────────────────────────────────────

NOTIFICATIONS_LOG: list[dict] = [
    {
        "id": _uid(),
        "target_user_id": "user-caregiver-1",
        "patient_id": "user-patient-1",
        "message": "[SMS SIMULATION] Rina Borah missed morning blood pressure tablet reminder.",
        "channel": "sms",
        "created_at": _days_ago(3).isoformat(),
        "read": False,
    },
    {
        "id": _uid(),
        "target_user_id": "user-caregiver-2",
        "patient_id": "user-patient-2",
        "message": "[SMS SIMULATION] Banshan Lyngdoh has not played a game in 48+ hours — inactivity alert.",
        "channel": "sms",
        "created_at": _days_ago(3).isoformat(),
        "read": False,
    },
]


def add_notification(target_user_id: str, patient_id: str, message: str, channel: str = "push") -> dict:
    """
    # MOCK: Simulates push/SMS delivery.
    # In production, this would call FCM for push and Twilio/MSG91 for SMS.
    # For now it just appends to NOTIFICATIONS_LOG and logs to console.
    """
    import sys
    entry = {
        "id": _uid(),
        "target_user_id": target_user_id,
        "patient_id": patient_id,
        "message": message,
        "channel": channel,
        "created_at": _now().isoformat(),
        "read": False,
    }
    NOTIFICATIONS_LOG.append(entry)
    print(f"[SMS SIMULATION] notification queued: {message}", file=sys.stderr)
    return entry
