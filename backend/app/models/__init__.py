import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    preferred_language = Column(String)
    state_region = Column(String)
    password_hash = Column(String)
    quiet_hours_start = Column(String)
    quiet_hours_end = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    dob_or_age = Column(Integer)
    dementia_stage_note = Column(Text)
    theme_preference = Column(String)
    onboarding_complete = Column(Boolean, default=False)
    guardian_consent_at = Column(DateTime(timezone=True))
    preferred_name = Column(String)
    likes = Column(ARRAY(String), default=list)
    dislikes = Column(ARRAY(String), default=list)
    routine_notes = Column(Text)
    mobility_notes = Column(Text)
    vision_notes = Column(Text)
    hearing_notes = Column(Text)
    location_sharing_consent = Column(Boolean, default=False)
    identification_notes = Column(Text)
    difficulty_memory = Column(String, default="easy")
    difficulty_attention = Column(String, default="easy")
    difficulty_routine = Column(String, default="easy")
    difficulty_recognition = Column(String, default="easy")

class CaregiverLink(Base):
    __tablename__ = "caregiver_links"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caregiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    relationship = Column(String, nullable=False)
    status = Column(String, nullable=False)

class GameSession(Base):
    __tablename__ = "game_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    client_uuid = Column(UUID(as_uuid=True), unique=True)
    game_type = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    accuracy_pct = Column(Float, nullable=False)
    time_spent_seconds = Column(Integer, nullable=False, default=0)
    hints_used = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)
    time = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReminderEvent(Base):
    __tablename__ = "reminder_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reminder_id = Column(UUID(as_uuid=True), ForeignKey("reminders.id", ondelete="CASCADE"))
    client_uuid = Column(UUID(as_uuid=True), unique=True)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False)
    action_taken_at = Column(DateTime(timezone=True))

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    type = Column(String, nullable=False)
    channel = Column(String)
    delivered = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)
    simulation_label = Column(String)
    explanation = Column(String)
    observed_threshold = Column(String)
    next_step = Column(String)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())

class ReminiscencePrompt(Base):
    __tablename__ = "reminiscence_prompts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    theme = Column(String, nullable=False)
    title = Column(String)
    prompt_text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReminiscenceNote(Base):
    __tablename__ = "reminiscence_notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(UUID(as_uuid=True), ForeignKey("reminiscence_prompts.id", ondelete="CASCADE"))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    note_text = Column(Text, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class CaregiverWellbeing(Base):
    __tablename__ = "caregiver_wellbeing"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    energy_score = Column(Integer, nullable=False)
    stress_score = Column(Integer, nullable=False)
    support_needed = Column(Boolean, default=False)
    notes = Column(String)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class AppointmentPrep(Base):
    __tablename__ = "appointment_preps"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    appointment_at = Column(String, nullable=False) # ISO String or DateTime
    doctor_name = Column(String, nullable=False)
    clinic_or_hospital = Column(String, nullable=False)
    questions_to_ask = Column(ARRAY(String), default=[])
    items_to_bring = Column(ARRAY(String), default=[])
    transport_notes = Column(String)
    extra_notes = Column(String)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    disclaimer = Column(String)

class TransportNote(Base):
    __tablename__ = "transport_notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    appointment_ref = Column(UUID(as_uuid=True), ForeignKey("appointment_preps.id", ondelete="SET NULL"))
    appointment_at = Column(String)
    mode = Column(String, nullable=False)
    pickup_point = Column(String, nullable=False)
    pickup_time = Column(String, nullable=False)
    driver_or_contact_name = Column(String)
    driver_or_contact_phone = Column(String)
    destination = Column(String, nullable=False)
    estimated_travel_minutes = Column(Integer)
    return_notes = Column(String)
    extra_notes = Column(String)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VisitPlan(Base):
    __tablename__ = "visit_plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    patient_name = Column(String, nullable=False)
    scheduled_at = Column(String, nullable=False)
    purpose = Column(String, nullable=False)
    location = Column(String, nullable=False)
    notes = Column(String)
    status = Column(String, default="planned")
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    target_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    message = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WellbeingGoal(Base):
    __tablename__ = "wellbeing_goals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    goal_text = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DailyTask(Base):
    __tablename__ = "daily_tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    label = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    category = Column(String, nullable=False)
    done = Column(Boolean, default=False)
    done_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MoodCheckin(Base):
    __tablename__ = "mood_checkins"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    mood_score = Column(Integer, nullable=False)
    sleep_hours = Column(Float)
    sleep_quality = Column(String)
    notes = Column(String)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    activity_type = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    intensity = Column(String)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

class CaregiverNote(Base):
    __tablename__ = "caregiver_notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SafetyCheckIn(Base):
    __tablename__ = "safety_check_ins"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(String, nullable=False)
    share_location = Column(Boolean, default=False)
    approximate_area = Column(String)
    consent_required = Column(Boolean, default=False)
    checked_in_at = Column(DateTime(timezone=True), server_default=func.now())

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    relationship = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)

class Medication(Base):
    __tablename__ = "medications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    missed_dose_guidance = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    action = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class HWPatientMap(Base):
    __tablename__ = "hw_patient_maps"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hw_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    __table_args__ = {'extend_existing': True}

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    activity_type = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    intensity = Column(String)
    notes = Column(String)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class EducationProgress(Base):
    __tablename__ = "education_progress"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    article_id = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SocialMessage(Base):
    __tablename__ = "social_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    message_text = Column(String, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

class DifficultyLog(Base):
    __tablename__ = "difficulty_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    game_type = Column(String, nullable=False)
    previous_tier = Column(String, nullable=False)
    new_tier = Column(String, nullable=False)
    decision_source = Column(String)
    inputs_json = Column(Text)
    decided_at = Column(DateTime(timezone=True), server_default=func.now())
