"""
seed.py — bootstrap the DB with demo users AND rich demo data for the demo patient.
Safe to run multiple times: checks for existing rows before inserting.
"""
import uuid
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.db import engine, SessionLocal
from app.core.auth import get_password_hash
from app.models import (
    Base, User, PatientProfile, CaregiverLink, HWPatientMap,
    GameSession, Reminder, ReminderEvent,
    Medication, EmergencyContact,
    SafetyCheckIn, MoodCheckin, ActivityLog,
    ReminiscencePrompt, ReminiscenceNote,
    SocialMessage, DailyTask, Notification,
    AppointmentPrep, TransportNote,
    Alert,
)


def _now(delta_days: int = 0, delta_hours: int = 0) -> datetime:
    """Return a UTC datetime offset from today."""
    return datetime.now(timezone.utc) + timedelta(days=delta_days, hours=delta_hours)


def _d(delta_days: int = 0, delta_hours: int = 0) -> datetime:
    """Alias for _now."""
    return _now(delta_days, delta_hours)


# ─────────────────────────────────────────────────────────────────────────────
#  USERS
# ─────────────────────────────────────────────────────────────────────────────

def _seed_users(db: Session):
    if db.query(User).filter(User.email == "admin@ner.in").first():
        print("  [users] Already seeded — skipping user creation.")
        return None

    print("  [users] Creating demo accounts …")
    admin_id    = uuid.uuid4()
    patient_id  = uuid.uuid4()
    caregiver_id = uuid.uuid4()
    hw_id       = uuid.uuid4()

    users = [
        User(
            id=admin_id, email="admin@ner.in", role="admin",
            name="System Admin", phone="0000000000",
            password_hash=get_password_hash("adminpass"), is_verified=True,
        ),
        User(
            id=patient_id, email="patient@ner.in", role="patient",
            name="Rajan Sharma", phone="1111111111",
            password_hash=get_password_hash("patpass"), is_verified=True,
            state_region="Maharashtra", preferred_language="hi",
        ),
        User(
            id=caregiver_id, email="caregiver@ner.in", role="caregiver",
            name="Priya Sharma", phone="2222222222",
            password_hash=get_password_hash("carepass"), is_verified=True,
            state_region="Maharashtra",
        ),
        User(
            id=hw_id, email="hw@ner.in", role="health_worker",
            name="Anjali Desai (ASHA)", phone="3333333333",
            password_hash=get_password_hash("hwpass"), is_verified=True,
            state_region="Maharashtra",
        ),
    ]
    for u in users:
        db.add(u)
    db.flush()

    return {
        "admin_id":     admin_id,
        "patient_id":   patient_id,
        "caregiver_id": caregiver_id,
        "hw_id":        hw_id,
    }


def _seed_links(db: Session, ids: dict):
    pid = ids["patient_id"]
    cid = ids["caregiver_id"]
    hid = ids["hw_id"]

    if not db.query(CaregiverLink).filter(CaregiverLink.patient_id == pid).first():
        db.add(CaregiverLink(
            id=uuid.uuid4(), caregiver_id=cid, patient_id=pid,
            relationship="Daughter", status="active",
        ))
        print("  [links] CaregiverLink created.")

    if not db.query(HWPatientMap).filter(HWPatientMap.patient_id == pid).first():
        db.add(HWPatientMap(id=uuid.uuid4(), hw_id=hid, patient_id=pid))
        print("  [links] HWPatientMap created.")


# ─────────────────────────────────────────────────────────────────────────────
#  PATIENT PROFILE (with game difficulty set)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_profile(db: Session, patient_id):
    existing = db.query(PatientProfile).filter(PatientProfile.user_id == patient_id).first()
    if existing:
        # Ensure difficulty columns are populated
        changed = False
        for field, val in [
            ("difficulty_memory", "easy"),
            ("difficulty_attention", "medium"),
            ("difficulty_routine", "easy"),
            ("difficulty_recognition", "medium"),
        ]:
            if not getattr(existing, field):
                setattr(existing, field, val)
                changed = True
        if changed:
            print("  [profile] Updated difficulty tiers on existing profile.")
        return

    db.add(PatientProfile(
        user_id=patient_id,
        dob_or_age=74,
        dementia_stage_note="Early stage — needs gentle prompts and routine reinforcement.",
        theme_preference="light",
        onboarding_complete=True,
        guardian_consent_at=_d(-30),
        preferred_name="Rajan Ji",
        likes=["morning tea", "cricket", "old Hindi songs", "gardening"],
        dislikes=["loud noises", "rush", "spicy food"],
        routine_notes="Wakes at 6 AM, tea at 6:30. Afternoon nap 1–3 PM. Evening walk at 5 PM.",
        mobility_notes="Walks independently indoors; uses walking stick outdoors.",
        vision_notes="Wears bifocals. Large font preferred.",
        hearing_notes="Mild hearing loss in left ear. Speak clearly from the right side.",
        location_sharing_consent=True,
        identification_notes="Can become disoriented in unfamiliar places after dark.",
        difficulty_memory="easy",
        difficulty_attention="medium",
        difficulty_routine="easy",
        difficulty_recognition="medium",
    ))
    print("  [profile] PatientProfile created.")


# ─────────────────────────────────────────────────────────────────────────────
#  GAME SESSIONS (14 days of history — drives trends + streak on dashboard)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_game_sessions(db: Session, patient_id):
    if db.query(GameSession).filter(GameSession.patient_id == patient_id).first():
        print("  [games] Game sessions already present — skipping.")
        return

    print("  [games] Seeding game sessions …")
    # 14 days of data, 2 sessions per day across game types
    game_types = ["memory", "attention", "routine", "recognition"]
    difficulties = ["easy", "medium", "easy", "medium"]
    # gentle upward trend in accuracy (50–78%)
    base_accuracies = [50, 52, 55, 54, 57, 59, 61, 63, 65, 64, 68, 70, 72, 75]

    sessions = []
    for day_offset in range(-13, 1):
        day_acc = base_accuracies[day_offset + 13]
        for i, (gt, diff) in enumerate(zip(game_types, difficulties)):
            acc = min(99.0, day_acc + i * 2.5)
            sessions.append(GameSession(
                id=uuid.uuid4(),
                patient_id=patient_id,
                client_uuid=uuid.uuid4(),
                game_type=gt,
                difficulty=diff,
                score=int(acc * 1.2),
                accuracy_pct=round(acc, 1),
                time_spent_seconds=180 + i * 30,
                hints_used=max(0, 3 - i),
                completed_at=_d(day_offset, -1 - i),
            ))

    for s in sessions:
        db.add(s)
    print(f"  [games] {len(sessions)} sessions added.")


# ─────────────────────────────────────────────────────────────────────────────
#  REMINDERS + EVENTS
# ─────────────────────────────────────────────────────────────────────────────

def _seed_reminders(db: Session, patient_id, caregiver_id):
    if db.query(Reminder).filter(Reminder.patient_id == patient_id).first():
        print("  [reminders] Already present — skipping.")
        return

    print("  [reminders] Seeding reminders + events …")

    reminder_specs = [
        dict(category="medicine", message="Take Donepezil 5 mg tablet with water",
             schedule_rule={"type": "daily", "times": ["08:00"]}, critical=True, escalation_minutes=30),
        dict(category="medicine", message="Take evening Vitamin D3 supplement",
             schedule_rule={"type": "daily", "times": ["19:00"]}, critical=False, escalation_minutes=60),
        dict(category="hydration", message="Drink a glass of water — stay hydrated!",
             schedule_rule={"type": "interval", "every_hours": 2}, critical=False, escalation_minutes=120),
        dict(category="activity", message="Time for your 15-minute evening walk",
             schedule_rule={"type": "daily", "times": ["17:00"]}, critical=False, escalation_minutes=60),
        dict(category="appointment", message="Doctor visit with Dr. Mehta on Thursday at 11 AM",
             schedule_rule={"type": "once", "on": "2026-09-25T11:00:00"}, critical=True, escalation_minutes=60),
    ]

    for spec in reminder_specs:
        rule = json.dumps(spec.pop("schedule_rule"))
        reminder = Reminder(
            id=uuid.uuid4(),
            patient_id=patient_id,
            created_by=caregiver_id,
            category=spec["category"],
            message=spec["message"],
            schedule_rule=rule,
            active=True,
            critical=spec.get("critical", False),
            escalation_minutes=spec.get("escalation_minutes", 60),
            created_at=_d(-7),
        )
        db.add(reminder)
        db.flush()

        # Seed 7 days of reminder events: mix of completed/missed
        statuses = ["completed", "completed", "completed", "missed", "completed", "completed", "completed"]
        for d, status in enumerate(statuses):
            db.add(ReminderEvent(
                id=uuid.uuid4(),
                reminder_id=reminder.id,
                client_uuid=uuid.uuid4(),
                scheduled_time=_d(-6 + d, 0),
                status=status,
                action_taken_at=_d(-6 + d, 0) + timedelta(minutes=5) if status == "completed" else None,
            ))

    print("  [reminders] Done.")


# ─────────────────────────────────────────────────────────────────────────────
#  MEDICATIONS
# ─────────────────────────────────────────────────────────────────────────────

def _seed_medications(db: Session, patient_id):
    if db.query(Medication).filter(Medication.patient_id == patient_id).first():
        print("  [medications] Already present — skipping.")
        return

    print("  [medications] Seeding medications …")
    meds = [
        Medication(
            id=uuid.uuid4(), patient_id=patient_id,
            name="Donepezil (Aricept)", dose="5 mg", form="tablet",
            instructions="Once daily at 8 AM with a full glass of water. Do not crush.",
            prescribing_clinician="Dr. Suresh Mehta, Neurologist",
            start_date="2026-01-15", end_date=None, refill_date="2026-10-01",
            active=True,
            missed_dose_guidance="If missed before noon, take immediately. If after noon, skip and resume next day.",
        ),
        Medication(
            id=uuid.uuid4(), patient_id=patient_id,
            name="Vitamin D3", dose="1000 IU", form="capsule",
            instructions="Once daily in the evening with food.",
            prescribing_clinician="Dr. Suresh Mehta, Neurologist",
            start_date="2026-02-01", end_date=None, refill_date="2026-10-15",
            active=True,
            missed_dose_guidance="Take as soon as you remember. No special precautions.",
        ),
        Medication(
            id=uuid.uuid4(), patient_id=patient_id,
            name="Amlodipine", dose="5 mg", form="tablet",
            instructions="Once daily in the morning. Monitor blood pressure weekly.",
            prescribing_clinician="Dr. Kavita Nair, Cardiologist",
            start_date="2025-11-10", end_date=None, refill_date="2026-09-28",
            active=True,
            missed_dose_guidance="Take as soon as remembered on the same day. Never double-dose.",
        ),
    ]
    for m in meds:
        db.add(m)
    print(f"  [medications] {len(meds)} medications added.")


# ─────────────────────────────────────────────────────────────────────────────
#  EMERGENCY CONTACTS
# ─────────────────────────────────────────────────────────────────────────────

def _seed_emergency_contacts(db: Session, patient_id):
    if db.query(EmergencyContact).filter(EmergencyContact.patient_id == patient_id).first():
        print("  [emergency] Already present — skipping.")
        return

    print("  [emergency] Seeding emergency contacts …")
    contacts = [
        EmergencyContact(
            id=uuid.uuid4(), patient_id=patient_id,
            name="Priya Sharma", relationship="Daughter",
            phone="9876543210", is_primary=True,
        ),
        EmergencyContact(
            id=uuid.uuid4(), patient_id=patient_id,
            name="Anjali Desai (ASHA Worker)", relationship="Health Worker",
            phone="9112233445", is_primary=False,
        ),
        EmergencyContact(
            id=uuid.uuid4(), patient_id=patient_id,
            name="Dr. Suresh Mehta (Neurologist)", relationship="Doctor",
            phone="9001122334", is_primary=False,
        ),
        EmergencyContact(
            id=uuid.uuid4(), patient_id=patient_id,
            name="Neighbourhood Watch — Mr. Iyer", relationship="Neighbour",
            phone="9800011223", is_primary=False,
        ),
    ]
    for c in contacts:
        db.add(c)
    print(f"  [emergency] {len(contacts)} contacts added.")


# ─────────────────────────────────────────────────────────────────────────────
#  SAFETY CHECK-INS (last 7 days)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_safety_checkins(db: Session, patient_id):
    if db.query(SafetyCheckIn).filter(SafetyCheckIn.patient_id == patient_id).first():
        print("  [safety] Already present — skipping.")
        return

    print("  [safety] Seeding safety check-ins …")
    checkins = [
        (0,  "safe",    "Good morning! Feeling well today.",         "Home — Pune, Maharashtra"),
        (-1, "safe",    "Had a good night's sleep.",                  "Home — Pune, Maharashtra"),
        (-2, "safe",    "Went for a walk in the garden.",             "Garden — Pune"),
        (-3, "safe",    "Watching cricket on TV, all good.",          "Home — Pune, Maharashtra"),
        (-4, "safe",    None,                                         "Home — Pune, Maharashtra"),
        (-5, "confused","Felt a bit disoriented in the afternoon.",   "Home — Pune, Maharashtra"),
        (-6, "safe",    "Back to normal after afternoon rest.",       "Home — Pune, Maharashtra"),
    ]
    for day, status, note, area in checkins:
        db.add(SafetyCheckIn(
            id=uuid.uuid4(), patient_id=patient_id,
            status=status, note=note,
            share_location=True, approximate_area=area,
            consent_required=False,
            checked_in_at=_d(day, -8),   # morning check-in time
        ))
    print(f"  [safety] {len(checkins)} check-ins added.")


# ─────────────────────────────────────────────────────────────────────────────
#  MOOD & SLEEP CHECK-INS (last 14 days)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_mood_checkins(db: Session, patient_id):
    if db.query(MoodCheckin).filter(MoodCheckin.patient_id == patient_id).first():
        print("  [mood] Already present — skipping.")
        return

    print("  [mood] Seeding mood/sleep check-ins …")
    # (day_offset, mood_score 1-5, sleep_hours, sleep_quality, notes)
    records = [
        (-13, 3, 6.5, "fair",  "A little tired, but managed morning tea."),
        (-12, 4, 7.0, "good",  "Good sleep, felt refreshed."),
        (-11, 3, 5.5, "poor",  "Up at 3 AM, couldn't sleep after."),
        (-10, 4, 7.5, "good",  "Watched a cricket match, great mood!"),
        (-9,  2, 5.0, "poor",  "Had a headache in the morning."),
        (-8,  4, 7.0, "good",  "Priya visited, very happy."),
        (-7,  3, 6.5, "fair",  "Normal day, tea and newspaper."),
        (-6,  5, 8.0, "good",  "Feeling great, went for a walk!"),
        (-5,  4, 7.0, "good",  "Good mood. Watched old songs on TV."),
        (-4,  3, 6.0, "fair",  "A bit tired after lunch."),
        (-3,  4, 7.5, "good",  "Memory game was fun today."),
        (-2,  3, 6.0, "fair",  "Mild confusion around evening."),
        (-1,  4, 7.0, "good",  "Slept well, morning walk done."),
        ( 0,  4, 7.0, "good",  "Feeling positive today!"),
    ]
    for day, score, sleep_h, sleep_q, notes in records:
        db.add(MoodCheckin(
            id=uuid.uuid4(), patient_id=patient_id,
            mood_score=score, sleep_hours=sleep_h,
            sleep_quality=sleep_q, notes=notes,
            recorded_at=_d(day, -7),
        ))
    print(f"  [mood] {len(records)} check-ins added.")


# ─────────────────────────────────────────────────────────────────────────────
#  ACTIVITY / MOVEMENT LOGS (last 14 days)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_activity_logs(db: Session, patient_id):
    if db.query(ActivityLog).filter(ActivityLog.patient_id == patient_id).first():
        print("  [activity] Already present — skipping.")
        return

    print("  [activity] Seeding activity logs …")
    # (day_offset, activity_type, duration_minutes, intensity, notes)
    logs = [
        (-13, "walk",    20, "light",    "Short morning walk around the block."),
        (-12, "stretch", 10, "light",    "Morning stretches after tea."),
        (-11, "walk",    15, "light",    "Felt tired, shorter walk today."),
        (-10, "walk",    25, "moderate", "Brisk walk in the garden."),
        (-9,  "yoga",    20, "light",    "Chair yoga session with Anjali."),
        (-8,  "walk",    30, "moderate", "Walked to the park and back."),
        (-7,  "stretch", 10, "light",    "Light stretches before bed."),
        (-6,  "walk",    30, "moderate", "Evening walk, great weather!"),
        (-5,  "walk",    20, "light",    "Morning walk, felt a bit slow."),
        (-4,  "stretch", 15, "light",    "Stretching session after rest."),
        (-3,  "walk",    25, "moderate", "Enjoyed the fresh air."),
        (-2,  "yoga",    20, "light",    "Chair yoga with Anjali via video."),
        (-1,  "walk",    30, "moderate", "Healthy walk, great mood after."),
        ( 0,  "walk",    20, "light",    "Morning walk done early today."),
    ]
    for day, atype, dur, intensity, notes in logs:
        db.add(ActivityLog(
            id=uuid.uuid4(), patient_id=patient_id,
            activity_type=atype, duration_minutes=dur,
            intensity=intensity, notes=notes,
            recorded_at=_d(day, -17),   # late morning log
        ))
    print(f"  [activity] {len(logs)} logs added.")


# ─────────────────────────────────────────────────────────────────────────────
#  DAILY TASKS — "MY DAY" (today's tasks, some done)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_daily_tasks(db: Session, patient_id):
    if db.query(DailyTask).filter(DailyTask.patient_id == patient_id).first():
        print("  [daily_tasks] Already present — skipping.")
        return

    print("  [daily_tasks] Seeding daily tasks …")
    tasks = [
        # (label, icon, category, done)
        ("Morning cup of tea",          "tea",          "morning",  True),
        ("Take Donepezil tablet",       "pill",         "morning",  True),
        ("Brush teeth and freshen up",  "toothbrush",   "hygiene",  True),
        ("Wash face and hands",         "water",        "hygiene",  True),
        ("Breakfast — idli with sambar","meal",         "meals",    True),
        ("Read morning newspaper",      "newspaper",    "morning",  False),
        ("Play memory game",            "game",         "morning",  False),
        ("Lunch at 1 PM",               "meal",         "meals",    False),
        ("Afternoon rest 1–3 PM",       "rest",         "evening",  False),
        ("Evening walk at 5 PM",        "walk",         "exercise", False),
        ("Evening tea and biscuits",    "tea",          "meals",    False),
        ("Take Vitamin D3 supplement",  "pill",         "evening",  False),
        ("Call Priya (daughter)",       "phone",        "evening",  False),
        ("Light dinner",                "meal",         "meals",    False),
        ("Brush teeth before bed",      "toothbrush",   "hygiene",  False),
    ]
    now = _d()
    for label, icon, category, done in tasks:
        db.add(DailyTask(
            id=uuid.uuid4(), patient_id=patient_id,
            label=label, icon=icon, category=category,
            done=done,
            done_at=_d(0, -3) if done else None,
            created_at=_d(0, -8),
        ))
    print(f"  [daily_tasks] {len(tasks)} tasks added.")


# ─────────────────────────────────────────────────────────────────────────────
#  MEMORY LANE — Reminiscence prompts + patient responses
# ─────────────────────────────────────────────────────────────────────────────

def _seed_memory_lane(db: Session, patient_id, caregiver_id):
    if db.query(ReminiscencePrompt).filter(ReminiscencePrompt.patient_id == patient_id).first():
        print("  [memory_lane] Already present — skipping.")
        return

    print("  [memory_lane] Seeding reminiscence prompts + notes …")
    prompts_data = [
        dict(
            theme="family",
            title="Your Wedding Day",
            prompt_text="Can you tell me about your wedding day? What did you wear? Who was there?",
            note="We got married in our hometown in a beautiful mandap. My wife wore a red saree and I wore a sherwani. All the relatives had come from different cities. It was the happiest day of my life.",
        ),
        dict(
            theme="home",
            title="Your Childhood Home",
            prompt_text="What did your childhood home look like? Can you describe your favourite room?",
            note="Our house had a big courtyard where we played cricket. My favourite room was the kitchen — it always smelled of my mother's cooking. There was a big neem tree outside.",
        ),
        dict(
            theme="festivals",
            title="Diwali Celebrations",
            prompt_text="What is your favourite memory of Diwali? What did your family do?",
            note="Every Diwali we made rangoli together. My children used to help me light diyas. We would eat sweets and burst small crackers. The whole street would glow with lights.",
        ),
        dict(
            theme="work",
            title="Your Career Days",
            prompt_text="Can you tell me about the job you are most proud of?",
            note="I worked as a school teacher for 30 years. I taught mathematics. My proudest moment was when one of my students topped the state board exams. He came to thank me personally.",
        ),
        dict(
            theme="food",
            title="Favourite Home-cooked Meal",
            prompt_text="What is your all-time favourite home-cooked dish? Who used to make it for you?",
            note="My wife used to make the best dal makhani. She would cook it slowly for hours. We always had it on Sunday evenings with fresh rotis. I still miss it very much.",
        ),
        dict(
            theme="seasons",
            title="Monsoon Memories",
            prompt_text="What do you remember most about the monsoon season growing up?",
            note="The smell of the first rain on dry earth is something I can never forget. We children would run outside and get completely drenched. Our mother would scold us but then give us hot tea.",
        ),
    ]

    for i, p in enumerate(prompts_data):
        note_text = p.pop("note")
        prompt = ReminiscencePrompt(
            id=uuid.uuid4(), patient_id=patient_id,
            created_by=caregiver_id,
            created_at=_d(-14 + i * 2),
            **p,
        )
        db.add(prompt)
        db.flush()

        db.add(ReminiscenceNote(
            id=uuid.uuid4(),
            prompt_id=prompt.id,
            patient_id=patient_id,
            note_text=note_text,
            recorded_at=_d(-13 + i * 2),
        ))

    print(f"  [memory_lane] {len(prompts_data)} prompts + notes added.")


# ─────────────────────────────────────────────────────────────────────────────
#  MESSAGES (social connection thread)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_messages(db: Session, patient_id, caregiver_id, hw_id):
    if db.query(SocialMessage).filter(SocialMessage.patient_id == patient_id).first():
        print("  [messages] Already present — skipping.")
        return

    print("  [messages] Seeding messages …")
    msgs = [
        # (sender_id, text, hours_ago)
        (caregiver_id, "Good morning Papa! 🌞 Did you take your morning tablet?", -50),
        (patient_id,   "Yes Priya, I took it with tea. All good here!", -49),
        (caregiver_id, "That's great! I'll call you in the evening. Love you 💙", -48),
        (hw_id,        "Namaste Rajan Ji! This is Anjali. I will visit Thursday for your health check.", -36),
        (patient_id,   "Okay Anjali ji, I will be home. Thank you for calling.", -35),
        (caregiver_id, "Papa, remember your doctor appointment is next Thursday at 11 AM. I will take you.", -24),
        (patient_id,   "Yes yes, I remember. Should I wear the blue shirt?", -23),
        (caregiver_id, "Haha yes, wear the blue shirt 😊 Get good rest tonight.", -22),
        (hw_id,        "Rajan Ji, please do your evening walk today. Very important for health!", -12),
        (patient_id,   "I went for a walk at 5 PM. 30 minutes! Feeling good.", -10),
        (caregiver_id, "Wonderful Papa! You are doing so well. Proud of you 🌟", -8),
        (patient_id,   "Thank you beta. I played the memory game also. Was fun!", -7),
    ]
    for sender_id, text, hours_ago in msgs:
        db.add(SocialMessage(
            id=uuid.uuid4(),
            patient_id=patient_id,
            sender_id=sender_id,
            message_text=text,
            sent_at=_d(0, hours_ago),
        ))
    print(f"  [messages] {len(msgs)} messages added.")


# ─────────────────────────────────────────────────────────────────────────────
#  DOCTOR VISIT PREP (AppointmentPrep)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_appointment_preps(db: Session, patient_id, caregiver_id):
    if db.query(AppointmentPrep).filter(AppointmentPrep.patient_id == patient_id).first():
        print("  [appt_prep] Already present — skipping.")
        return

    print("  [appt_prep] Seeding appointment preps …")
    disclaimer = (
        "This preparation note is an organisational aid only and does not "
        "constitute medical advice. Discuss all clinical decisions with the patient's doctor."
    )

    preps = [
        AppointmentPrep(
            id=uuid.uuid4(),
            patient_id=patient_id,
            appointment_at="2026-09-25T11:00:00",
            doctor_name="Dr. Suresh Mehta",
            clinic_or_hospital="Mehta Neurology Clinic, Pune",
            questions_to_ask=[
                "Is the current Donepezil dose still appropriate?",
                "Should we increase to 10 mg given recent memory changes?",
                "Any new tests needed — MRI or blood work?",
                "Advice on daily activity to slow progression?",
                "Is the mild confusion in evenings (sundowning) a concern?",
            ],
            items_to_bring=[
                "National ID / Aadhaar card",
                "Medication list (current 3 medications)",
                "Blood pressure log (last 2 weeks)",
                "Previous MRI report (June 2026)",
                "Insurance card",
            ],
            transport_notes="Priya will drive. Leave home by 10:15 AM.",
            extra_notes=(
                "Rajan Ji gets anxious in waiting rooms. Bring his favourite biscuits "
                "and a small radio for comfort. Confirm appointment day before."
            ),
            created_by=caregiver_id,
            created_at=_d(-5),
            disclaimer=disclaimer,
        ),
        AppointmentPrep(
            id=uuid.uuid4(),
            patient_id=patient_id,
            appointment_at="2026-10-10T09:30:00",
            doctor_name="Dr. Kavita Nair",
            clinic_or_hospital="Heart & Vascular Care, Pune",
            questions_to_ask=[
                "Blood pressure has been slightly elevated — any medication adjustment?",
                "Is Amlodipine dose still correct?",
                "Can he continue daily walks at current intensity?",
            ],
            items_to_bring=[
                "Blood pressure log",
                "Medication list",
                "Aadhaar card",
            ],
            transport_notes="Auto-rickshaw from home. Book 1 hour before.",
            extra_notes="Routine cardiology follow-up. No fasting required.",
            created_by=caregiver_id,
            created_at=_d(-2),
            disclaimer=disclaimer,
        ),
    ]
    for p in preps:
        db.add(p)
    print(f"  [appt_prep] {len(preps)} prep notes added.")


# ─────────────────────────────────────────────────────────────────────────────
#  TRANSPORT NOTES
# ─────────────────────────────────────────────────────────────────────────────

def _seed_transport_notes(db: Session, patient_id, caregiver_id, appt_prep_ref=None):
    if db.query(TransportNote).filter(TransportNote.patient_id == patient_id).first():
        print("  [transport] Already present — skipping.")
        return

    print("  [transport] Seeding transport notes …")

    # Fetch the appointment prep we just created, to cross-reference
    prep = db.query(AppointmentPrep).filter(AppointmentPrep.patient_id == patient_id).first()

    notes = [
        TransportNote(
            id=uuid.uuid4(),
            patient_id=patient_id,
            appointment_ref=prep.id if prep else None,
            appointment_at="2026-09-25T11:00:00",
            mode="family_vehicle",
            pickup_point="Home — Flat 12, Shivneri Society, Kothrud, Pune",
            pickup_time="10:15 AM on 25 September 2026",
            driver_or_contact_name="Priya Sharma (Daughter)",
            driver_or_contact_phone="9876543210",
            destination="Mehta Neurology Clinic, FC Road, Pune — 411004",
            estimated_travel_minutes=25,
            return_notes="Return directly home after appointment. No stops unless Rajan Ji requests.",
            extra_notes="Keep windows slightly open. Rajan Ji prefers left rear seat. Carry water bottle.",
            created_by=caregiver_id,
            created_at=_d(-5),
        ),
        TransportNote(
            id=uuid.uuid4(),
            patient_id=patient_id,
            appointment_ref=None,
            appointment_at="2026-10-10T09:30:00",
            mode="taxi",
            pickup_point="Home — Flat 12, Shivneri Society, Kothrud, Pune",
            pickup_time="09:00 AM on 10 October 2026",
            driver_or_contact_name="Ola Cab — pre-booked by Anjali",
            driver_or_contact_phone="9112233445",
            destination="Heart & Vascular Care, Baner Road, Pune — 411045",
            estimated_travel_minutes=35,
            return_notes="Anjali Desai will accompany for return journey.",
            extra_notes="Anjali to sit with patient. Confirm cab booking 1 hour before.",
            created_by=caregiver_id,
            created_at=_d(-2),
        ),
    ]
    for n in notes:
        db.add(n)
    print(f"  [transport] {len(notes)} transport notes added.")


# ─────────────────────────────────────────────────────────────────────────────
#  NOTIFICATIONS (for caregiver + hw — drives the bell icon)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_notifications(db: Session, patient_id, caregiver_id, hw_id):
    if db.query(Notification).filter(Notification.target_user_id == caregiver_id).first():
        print("  [notifications] Already present — skipping.")
        return

    print("  [notifications] Seeding notifications …")
    cg_notifs = [
        ("[ALERT] Rajan Ji missed his morning Donepezil reminder 3 days ago.", -72, False),
        ("[SAFETY] Rajan Ji completed his safety check-in at 8:05 AM today. ✓", -8,  True),
        ("[MOOD] Rajan Ji logged mood: 4/5 — Good. Sleep: 7 hrs (good).", -7,   True),
        ("[ACTIVITY] Evening walk completed — 30 minutes. Great job!", -10,      True),
        ("[SOCIAL] New message from Rajan Ji: 'I played the memory game also. Was fun!'", -7, False),
        ("[REMINDER] Upcoming doctor appointment: Dr. Mehta on 25 Sep at 11 AM.", -24, False),
        ("[GAME] Rajan Ji completed a Memory game session — accuracy 75%. Improving!", -1, False),
        ("[SAFETY] Rajan Ji marked as 'confused' 5 days ago. Review care notes.", -120, True),
    ]
    for msg, hours_ago, read in cg_notifs:
        db.add(Notification(
            id=uuid.uuid4(),
            user_id=caregiver_id,
            target_user_id=caregiver_id,
            message=msg,
            channel="in_app",
            read=read,
            created_at=_d(0, hours_ago),
        ))

    hw_notifs = [
        ("[VISIT] Upcoming visit to Rajan Ji scheduled for Thursday.", -48, False),
        ("[ACTIVITY] Rajan Ji completed chair yoga session — 20 minutes.", -96, True),
        ("[MOOD] Rajan Ji reported poor sleep 3 days ago. Monitor.", -72, False),
        ("[REMINDER] Safety check-in confirmed by Rajan Ji at 8:10 AM.", -8, True),
    ]
    for msg, hours_ago, read in hw_notifs:
        db.add(Notification(
            id=uuid.uuid4(),
            user_id=hw_id,
            target_user_id=hw_id,
            message=msg,
            channel="in_app",
            read=read,
            created_at=_d(0, hours_ago),
        ))

    # Patient-side notification
    db.add(Notification(
        id=uuid.uuid4(),
        user_id=patient_id,
        target_user_id=patient_id,
        message="[REMINDER] Time to take your evening Vitamin D3 supplement 🌿",
        channel="in_app",
        read=False,
        created_at=_d(0, -3),
    ))

    print(f"  [notifications] {len(cg_notifs) + len(hw_notifs) + 1} notifications added.")


# ─────────────────────────────────────────────────────────────────────────────
#  ALERTS (drives the dashboard alert count for caregiver)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_alerts(db: Session, patient_id):
    if db.query(Alert).filter(Alert.patient_id == patient_id).first():
        print("  [alerts] Already present — skipping.")
        return

    print("  [alerts] Seeding alerts …")
    alerts = [
        Alert(
            id=uuid.uuid4(), patient_id=patient_id,
            type="missed_reminder",
            channel="in_app",
            delivered=True, resolved=True,
            simulation_label="Missed morning medication",
            explanation="Rajan Ji did not acknowledge the 8 AM Donepezil reminder on 14 Sep.",
            observed_threshold="1 missed critical reminder event",
            next_step="Reminder acknowledged next day. Consider adding a physical reminder card.",
            triggered_at=_d(-3),
        ),
        Alert(
            id=uuid.uuid4(), patient_id=patient_id,
            type="inactivity",
            channel="in_app",
            delivered=True, resolved=False,
            simulation_label="Low activity flagged",
            explanation="Only 1 activity session logged in the past 3 days.",
            observed_threshold="Fewer than 3 activity sessions in 3 days",
            next_step="Check in with Rajan Ji and encourage a short walk or chair exercises.",
            triggered_at=_d(-1),
        ),
    ]
    for a in alerts:
        db.add(a)
    print(f"  [alerts] {len(alerts)} alerts added.")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def seed_db():
    print("Ensuring database tables exist …")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Schema migrations (safe to run repeatedly on Postgres & SQLite)
        for col_sql in [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS quiet_hours_start VARCHAR",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS quiet_hours_end VARCHAR",
        ]:
            try:
                db.execute(text(col_sql + ";"))
                db.commit()
            except Exception:
                db.rollback()

        # ── 1. Users ──────────────────────────────────────────────────────────
        ids = _seed_users(db)
        if ids is None:
            # Users already exist — look up their IDs
            admin    = db.query(User).filter(User.email == "admin@ner.in").first()
            patient  = db.query(User).filter(User.email == "patient@ner.in").first()
            caregiver = db.query(User).filter(User.email == "caregiver@ner.in").first()
            hw       = db.query(User).filter(User.email == "hw@ner.in").first()
            if not (patient and caregiver and hw):
                print("ERROR: Could not look up all demo users. Aborting seed.")
                return
            ids = {
                "admin_id":     admin.id if admin else None,
                "patient_id":   patient.id,
                "caregiver_id": caregiver.id,
                "hw_id":        hw.id,
            }
        else:
            db.commit()

        pid = ids["patient_id"]
        cid = ids["caregiver_id"]
        hid = ids["hw_id"]

        # ── 2. Links ──────────────────────────────────────────────────────────
        _seed_links(db, ids)
        db.commit()

        # ── 3. Patient profile + difficulty ───────────────────────────────────
        _seed_profile(db, pid)
        db.commit()

        # ── 4. Game sessions (drives dashboard trends + streak) ───────────────
        _seed_game_sessions(db, pid)
        db.commit()

        # ── 5. Reminders + events ─────────────────────────────────────────────
        _seed_reminders(db, pid, cid)
        db.commit()

        # ── 6. Medications ────────────────────────────────────────────────────
        _seed_medications(db, pid)
        db.commit()

        # ── 7. Emergency contacts ─────────────────────────────────────────────
        _seed_emergency_contacts(db, pid)
        db.commit()

        # ── 8. Safety check-ins ───────────────────────────────────────────────
        _seed_safety_checkins(db, pid)
        db.commit()

        # ── 9. Mood + sleep ───────────────────────────────────────────────────
        _seed_mood_checkins(db, pid)
        db.commit()

        # ── 10. Activity / movement ───────────────────────────────────────────
        _seed_activity_logs(db, pid)
        db.commit()

        # ── 11. Daily tasks (My Day) ──────────────────────────────────────────
        _seed_daily_tasks(db, pid)
        db.commit()

        # ── 12. Memory lane ───────────────────────────────────────────────────
        _seed_memory_lane(db, pid, cid)
        db.commit()

        # ── 13. Messages ──────────────────────────────────────────────────────
        _seed_messages(db, pid, cid, hid)
        db.commit()

        # ── 14. Doctor visit prep ─────────────────────────────────────────────
        _seed_appointment_preps(db, pid, cid)
        db.commit()

        # ── 15. Transport notes ───────────────────────────────────────────────
        _seed_transport_notes(db, pid, cid)
        db.commit()

        # ── 16. Notifications ─────────────────────────────────────────────────
        _seed_notifications(db, pid, cid, hid)
        db.commit()

        # ── 17. Alerts ────────────────────────────────────────────────────────
        _seed_alerts(db, pid)
        db.commit()

        print("\nDatabase seeded successfully with full demo data.")
        print(f"  Patient:   patient@ner.in  / patpass")
        print(f"  Caregiver: caregiver@ner.in / carepass")
        print(f"  HW:        hw@ner.in        / hwpass")
        print(f"  Admin:     admin@ner.in     / adminpass")

    except Exception as e:
        print(f"Seed error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
