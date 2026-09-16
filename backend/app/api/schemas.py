"""
Pydantic request/response schemas for all endpoints.
These define the real contract that production would also use.
"""
from typing import Optional, Literal
from pydantic import BaseModel


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Literal["patient", "caregiver", "health_worker"]
    phone: Optional[str] = None

class AdminAssignCaregiverRequest(BaseModel):
    caregiver_id: str
    patient_id: str
    relationship: str

class VerifyEmailRequest(BaseModel):
    token: str

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Users / Profile ───────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: str
    role: str
    name: str
    phone: str
    preferred_language: str
    state_region: str
    created_at: str
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class PatientProfileOut(BaseModel):
    user_id: str
    dob_or_age: Optional[int] = None
    dementia_stage_note: Optional[str] = None
    theme_preference: Optional[str] = "assam_village"
    onboarding_complete: bool = False
    guardian_consent_at: Optional[str] = None
    current_difficulty: dict = {
        "memory": "easy",
        "attention": "easy",
        "routine": "easy",
        "recognition": "easy",
    }
    preferred_name: Optional[str] = None
    likes: list[str] = []
    dislikes: list[str] = []
    routine_notes: Optional[str] = None
    mobility_notes: Optional[str] = None
    vision_notes: Optional[str] = None
    hearing_notes: Optional[str] = None
    location_sharing_consent: bool = False
    identification_notes: Optional[str] = None


class PatientProfileUpdate(BaseModel):
    dob_or_age: Optional[int] = None
    dementia_stage_note: Optional[str] = None
    theme_preference: Optional[str] = None
    onboarding_complete: Optional[bool] = None
    guardian_consent_at: Optional[str] = None
    preferred_name: Optional[str] = None
    likes: Optional[list[str]] = None
    dislikes: Optional[list[str]] = None
    routine_notes: Optional[str] = None
    mobility_notes: Optional[str] = None
    vision_notes: Optional[str] = None
    hearing_notes: Optional[str] = None
    location_sharing_consent: Optional[bool] = None
    identification_notes: Optional[str] = None


# ── Medication records ─────────────────────────────────────────────────────────

class MedicationCreate(BaseModel):
    patient_id: str
    name: str
    dose: str
    form: str = "tablet"
    instructions: str = "Follow the clinician or pharmacist instructions."
    prescribing_clinician: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    refill_date: Optional[str] = None
    active: bool = True


class MedicationOut(MedicationCreate):
    id: str
    missed_dose_guidance: str


# ── Safety check-ins ────────────────────────────────────────────────────────────

class SafetyCheckInCreate(BaseModel):
    patient_id: str
    status: Literal["home", "with_caregiver", "out", "needs_help"]
    note: Optional[str] = None
    share_location: bool = False
    approximate_area: Optional[str] = None


class SafetyCheckInOut(SafetyCheckInCreate):
    id: str
    checked_in_at: str
    consent_required: bool = True


# ── Emergency Contacts ────────────────────────────────────────────────────────

class EmergencyContactCreate(BaseModel):
    patient_id: str
    name: str
    phone: str
    relationship: str
    is_primary: bool = False


class EmergencyContactOut(EmergencyContactCreate):
    id: str


# ── Caregiver Links ───────────────────────────────────────────────────────────

class CaregiverLinkCreate(BaseModel):
    patient_id: str
    relationship: str
    caregiver_id: Optional[str] = None


class CaregiverLinkOut(BaseModel):
    id: str
    caregiver_id: str
    patient_id: str
    relationship: str
    status: str


class CaregiverLinkPatch(BaseModel):
    status: Literal["active", "revoked"]


class AuditEntryOut(BaseModel):
    id: str
    actor_id: str
    patient_id: str
    action: str
    accessed_at: str


class CaregiverNoteCreate(BaseModel):
    patient_id: str
    note: str
    category: Literal["handover", "observation", "appointment", "routine", "other"] = "handover"


class CaregiverNoteOut(CaregiverNoteCreate):
    id: str
    author_id: str
    created_at: str


# ── Game Sessions ─────────────────────────────────────────────────────────────

class GameSessionIn(BaseModel):
    patient_id: str
    game_type: Literal["memory", "attention", "routine", "recognition"]
    difficulty: Literal["easy", "medium", "hard"]
    score: int
    accuracy: float
    reaction_time_avg_ms: int
    errors: int
    started_at: str
    completed_at: str
    client_uuid: str


class GameSessionOut(GameSessionIn):
    id: str
    sync_status: str


class SyncGameSessionsRequest(BaseModel):
    sessions: list[GameSessionIn]


class SyncGameSessionsResponse(BaseModel):
    synced: int
    skipped: int


# ── Reminders ─────────────────────────────────────────────────────────────────

class ReminderCreate(BaseModel):
    patient_id: str
    category: Literal["medicine", "hydration", "activity", "appointment"]
    message: str
    schedule_rule: dict
    active: bool = True
    critical: bool = False
    escalation_minutes: int = 60


class ReminderUpdate(BaseModel):
    category: Optional[Literal["medicine", "hydration", "activity", "appointment"]] = None
    message: Optional[str] = None
    schedule_rule: Optional[dict] = None
    active: Optional[bool] = None
    critical: Optional[bool] = None
    escalation_minutes: Optional[int] = None


class ReminderOut(ReminderCreate):
    id: str
    critical: bool = False
    escalation_minutes: int = 60


class ReminderEscalationOut(BaseModel):
    reminder_id: str
    patient_id: str
    escalated: bool
    reason: str
    notification_ids: list[str] = []


class ReminderEventIn(BaseModel):
    reminder_id: str
    patient_id: str
    fired_at: str
    action: Literal["done", "snoozed", "missed"]
    client_uuid: str


class ReminderEventOut(ReminderEventIn):
    id: str
    sync_status: str


class SyncReminderEventsRequest(BaseModel):
    events: list[ReminderEventIn]


class SyncReminderEventsResponse(BaseModel):
    synced: int
    skipped: int


# ── Difficulty ────────────────────────────────────────────────────────────────

class DifficultyResponse(BaseModel):
    patient_id: str
    game_type: str
    current_tier: str
    next_tier: str
    decision_source: str
    reason: str
    inputs: dict


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    patient_id: str
    patient_name: str
    total_sessions: int
    sessions_last_7_days: int
    streak_days: int
    avg_accuracy_last_7_days: float
    reminder_adherence_pct: float
    last_session_at: Optional[str]
    inactivity_hours: float
    current_difficulty: dict


class CareSummaryOut(BaseModel):
    patient_id: str
    patient_name: str
    generated_at: str
    period_days: int
    activity: dict
    reminders: dict
    current_difficulty: dict
    medications: list[dict]
    disclaimer: str


class SummaryExportOut(BaseModel):
    filename: str
    content_type: str
    content: str
    disclaimer: str


class TrendPoint(BaseModel):
    date: str
    score: float
    accuracy: float
    difficulty: str


class TrendResponse(BaseModel):
    patient_id: str
    game_type: str
    range_days: int
    points: list[TrendPoint]
    plain_language_summary: Optional[str] = None


# ── Alerts ────────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    id: str
    patient_id: str
    type: str
    triggered_at: str
    channel: str
    delivered: bool
    resolved: bool
    simulation_label: Optional[str] = None
    explanation: Optional[str] = None
    observed_threshold: Optional[str] = None
    next_step: Optional[str] = None


# ── Voice ─────────────────────────────────────────────────────────────────────

class STTRequest(BaseModel):
    audio_base64: str
    language: str = "en"


class STTResponse(BaseModel):
    transcript: str
    language: str
    source: str   # "web_speech_fallback" or "bhashini" — MOCK: always web_speech_fallback


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


class TTSResponse(BaseModel):
    audio_url: str
    language: str
    source: str   # MOCK: always web_speech_fallback


# ── Reminiscence Therapy ───────────────────────────────────────────────────────

class ReminiscencePromptOut(BaseModel):
    id: str
    patient_id: str
    theme: str          # family | home | festivals | seasons | work | food
    title: str
    prompt_text: str
    created_by: str     # caregiver/admin user_id
    created_at: str


class ReminiscenceNoteIn(BaseModel):
    prompt_id: str
    patient_id: str
    note_text: str      # patient's written memory response


class ReminiscenceNoteOut(BaseModel):
    id: str
    prompt_id: str
    patient_id: str
    note_text: str
    recorded_at: str


# ── Social Connection ──────────────────────────────────────────────────────────

class SocialMessageIn(BaseModel):
    patient_id: str
    sender_id: str
    message_text: str


class SocialMessageOut(BaseModel):
    id: str
    patient_id: str
    sender_id: str
    sender_name: str
    sender_role: str
    message_text: str
    sent_at: str


# ── Daily Living Assistance ───────────────────────────────────────────────────

class DailyTaskOut(BaseModel):
    id: str
    patient_id: str
    label: str          # e.g. "Morning tea", "Take medication"
    category: str       # morning | hygiene | meals | exercise | evening
    done: bool
    done_at: Optional[str] = None


class DailyTaskToggle(BaseModel):
    done: bool


# ── Sleep and Mood Check-ins ──────────────────────────────────────────────────

class MoodCheckinIn(BaseModel):
    patient_id: str
    mood_score: int           # 1 = very low, 5 = very good
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[str] = None  # poor | fair | good
    notes: Optional[str] = None


class MoodCheckinOut(BaseModel):
    id: str
    patient_id: str
    mood_score: int
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: str


# ── Physical Activity ──────────────────────────────────────────────────────────

class ActivityLogIn(BaseModel):
    patient_id: str
    activity_type: str      # walk | stretch | yoga | exercise | other
    duration_minutes: int
    intensity: Optional[str] = None   # light | moderate | vigorous
    notes: Optional[str] = None


class ActivityLogOut(BaseModel):
    id: str
    patient_id: str
    activity_type: str
    duration_minutes: int
    intensity: Optional[str] = None
    notes: Optional[str] = None
    logged_at: str


# ── Caregiver Education Library ───────────────────────────────────────────────

class EducationArticleOut(BaseModel):
    id: str
    title: str
    category: str
    summary: str
    body: str
    language: str
    source_note: str
    updated_at: str
    read_time_minutes: int


class EducationArticleProgressIn(BaseModel):
    completed: bool


class EducationArticleProgressOut(BaseModel):
    article_id: str
    user_id: str
    completed: bool
    updated_at: str
    


class EducationArticleProgressMapOut(BaseModel):
    progress: dict[str, bool]
    updated_at: Optional[str] = None


class EducationArticleCreate(BaseModel):
    title: str
    category: str
    summary: str
    body: str
    language: str = "en"
    source_note: str = "Prototype educational content; discuss care decisions with a qualified clinician."
    read_time_minutes: int = 3


class EducationArticleListResponse(BaseModel):
    articles: list[EducationArticleOut]
    progress: dict[str, bool]
    disclaimer: str


# ── Caregiver Wellbeing Check-ins ─────────────────────────────────────────────

class CaregiverWellbeingIn(BaseModel):
    energy_score: int
    stress_score: int
    support_needed: Optional[str] = None
    notes: Optional[str] = None


class CaregiverWellbeingOut(BaseModel):
    id: str
    user_id: str
    energy_score: int
    stress_score: int
    support_needed: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: str


# ── Health-worker Route / Visit Planning ───────────────────────────────────────

class VisitPlanIn(BaseModel):
    patient_id: str
    scheduled_at: str
    purpose: str
    location: str
    notes: Optional[str] = None


class VisitPlanUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


class VisitPlanOut(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    scheduled_at: str
    purpose: str
    location: str
    notes: Optional[str] = None
    status: str
    created_by: str
    created_at: str


# ── Appointment Preparation (R16) ─────────────────────────────────────────────

class AppointmentPrepCreate(BaseModel):
    patient_id: str
    appointment_at: str                          # ISO datetime
    doctor_name: str
    clinic_or_hospital: str
    questions_to_ask: list[str] = []            # plain-language questions for doctor
    items_to_bring: list[str] = []              # e.g. ["ID card", "Previous reports"]
    transport_notes: Optional[str] = None       # e.g. "Auto from village stand at 9am"
    extra_notes: Optional[str] = None


class AppointmentPrepUpdate(BaseModel):
    appointment_at: Optional[str] = None
    doctor_name: Optional[str] = None
    clinic_or_hospital: Optional[str] = None
    questions_to_ask: Optional[list[str]] = None
    items_to_bring: Optional[list[str]] = None
    transport_notes: Optional[str] = None
    extra_notes: Optional[str] = None


class AppointmentPrepOut(AppointmentPrepCreate):
    id: str
    created_by: str
    created_at: str
    disclaimer: str = (
        "This preparation note is an organisational aid only and does not "
        "constitute medical advice. Discuss all clinical decisions with the patient's doctor."
    )


# ── Appointment Transport / Location Notes (R17) ──────────────────────────────

class TransportNoteCreate(BaseModel):
    patient_id: str
    appointment_ref: Optional[str] = None          # free-text or appointment_prep id
    appointment_at: str                             # ISO datetime of the appointment
    mode: str                                       # walk | auto | taxi | bus | family_vehicle | ambulance | other
    pickup_point: str                               # plain-language address / landmark
    pickup_time: str                                # e.g. "09:30" or ISO datetime
    driver_or_contact_name: Optional[str] = None   # name of driver / escort
    driver_or_contact_phone: Optional[str] = None  # phone number (not validated beyond non-empty)
    destination: str                                # clinic / hospital name + ward
    estimated_travel_minutes: Optional[int] = None
    return_notes: Optional[str] = None             # instructions for return journey
    extra_notes: Optional[str] = None


class TransportNoteUpdate(BaseModel):
    appointment_ref: Optional[str] = None
    appointment_at: Optional[str] = None
    mode: Optional[str] = None
    pickup_point: Optional[str] = None
    pickup_time: Optional[str] = None
    driver_or_contact_name: Optional[str] = None
    driver_or_contact_phone: Optional[str] = None
    destination: Optional[str] = None
    estimated_travel_minutes: Optional[int] = None
    return_notes: Optional[str] = None
    extra_notes: Optional[str] = None


class TransportNoteOut(TransportNoteCreate):
    id: str
    created_by: str
    created_at: str
