-- Database Schema Initialization
-- Used to migrate from mock_data to Supabase Postgres

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('patient', 'caregiver', 'health_worker', 'admin')),
    name TEXT NOT NULL,
    phone TEXT,
    preferred_language TEXT,
    state_region TEXT,
    password_hash TEXT,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Patient Profiles
CREATE TABLE IF NOT EXISTS patient_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    dob_or_age INT,
    dementia_stage_note TEXT,
    theme_preference TEXT,
    onboarding_complete BOOLEAN DEFAULT FALSE,
    guardian_consent_at TIMESTAMP WITH TIME ZONE,
    preferred_name TEXT,
    likes TEXT[] DEFAULT '{}',
    dislikes TEXT[] DEFAULT '{}',
    routine_notes TEXT,
    mobility_notes TEXT,
    vision_notes TEXT,
    hearing_notes TEXT,
    location_sharing_consent BOOLEAN DEFAULT FALSE,
    identification_notes TEXT,
    difficulty_memory TEXT DEFAULT 'easy',
    difficulty_attention TEXT DEFAULT 'easy',
    difficulty_routine TEXT DEFAULT 'easy',
    difficulty_recognition TEXT DEFAULT 'easy'
);

-- 3. Caregiver Links
CREATE TABLE IF NOT EXISTS caregiver_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    caregiver_id UUID REFERENCES users(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'revoked')),
    UNIQUE(caregiver_id, patient_id)
);

-- 4. Health Worker Maps
CREATE TABLE IF NOT EXISTS hw_patient_maps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hw_id UUID REFERENCES users(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(hw_id, patient_id)
);

-- 5. Caregiver Notes
CREATE TABLE IF NOT EXISTS caregiver_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Safety Check-Ins
CREATE TABLE IF NOT EXISTS safety_check_ins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    share_location BOOLEAN DEFAULT FALSE,
    approximate_area TEXT,
    consent_required BOOLEAN DEFAULT FALSE,
    checked_in_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Emergency Contacts
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    phone TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE
);

-- 8. Reminders
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    time TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reminder_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reminder_id UUID REFERENCES reminders(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'missed')),
    action_taken_at TIMESTAMP WITH TIME ZONE
);

-- 9. Medications
CREATE TABLE IF NOT EXISTS medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    frequency TEXT NOT NULL,
    missed_dose_guidance TEXT
);

-- 10. Audit Log
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID REFERENCES users(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 11. Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    channel TEXT NOT NULL,
    delivered BOOLEAN DEFAULT FALSE,
    resolved BOOLEAN DEFAULT FALSE,
    simulation_label TEXT,
    explanation TEXT,
    observed_threshold TEXT,
    next_step TEXT
);

-- 12. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    target_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    channel TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    silenced BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 13. Game Sessions
CREATE TABLE IF NOT EXISTS game_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    game_type TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    score INT NOT NULL,
    accuracy_pct FLOAT NOT NULL,
    duration_seconds INT NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    hints_used INT DEFAULT 0
);

-- 14. Activity Logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL,
    duration_minutes INT NOT NULL,
    intensity TEXT NOT NULL,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 15. Mood Logs
CREATE TABLE IF NOT EXISTS mood_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    mood_score INT NOT NULL,
    sleep_quality TEXT,
    notes TEXT,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 16. Daily Living Tasks
CREATE TABLE IF NOT EXISTS daily_living_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    date DATE NOT NULL
);

-- 17. Reminiscence Media & Prompts
CREATE TABLE IF NOT EXISTS reminiscence_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    media_url TEXT,
    media_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reminiscence_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_id UUID REFERENCES reminiscence_prompts(id) ON DELETE CASCADE,
    response_audio_url TEXT,
    response_text TEXT,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 18. Social Messages
CREATE TABLE IF NOT EXISTS social_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    audio_url TEXT,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 19. Visits
CREATE TABLE IF NOT EXISTS visits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    hw_id UUID REFERENCES users(id) ON DELETE CASCADE,
    visit_date TIMESTAMP WITH TIME ZONE NOT NULL,
    purpose TEXT NOT NULL,
    location TEXT NOT NULL,
    notes TEXT,
    status TEXT NOT NULL CHECK (status IN ('planned', 'completed', 'cancelled'))
);

-- 20. Transport Notes
CREATE TABLE IF NOT EXISTS transport_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id) ON DELETE CASCADE,
    mode TEXT NOT NULL,
    pickup_point TEXT,
    driver_contact TEXT,
    destination TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 21. Appointment Preps
CREATE TABLE IF NOT EXISTS appointment_preps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id) ON DELETE CASCADE,
    doctor_name TEXT NOT NULL,
    clinic_name TEXT,
    questions TEXT[] DEFAULT '{}',
    items_to_bring TEXT[] DEFAULT '{}',
    transport_note_id UUID REFERENCES transport_notes(id) ON DELETE SET NULL,
    disclaimer TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
