# Migration Audit Document

## 1. Feature-by-Feature State vs. Required Production State

| Feature Area | Current State (Mocked) | Required Production State |
|--------------|------------------------|---------------------------|
| **Authentication & User Management** | Hardcoded users in `mock_data.py`. JWTs generated via PyJWT locally. | Supabase Auth (PostgreSQL DB). JWTs verified via Supabase SDK. Real user roles and Row-Level Security (RLS). |
| **Database & Persistence** | In-memory Python data structures (`list`, `dict`) in `mock_data.py` (lost on server restart). | Supabase PostgreSQL. Tables for users, patients, sessions, notes, reminders, etc., mapped via an ORM (e.g., Prisma or SQLAlchemy) or Supabase client. |
| **Media & File Storage** | None (currently relies on static local assets or no media). | Cloudinary (or Supabase Storage) for image/audio uploads (e.g., for Reminiscence therapy). |
| **AI Text-to-Speech (TTS) & Speech-to-Text (STT)** | Simulated endpoints in `voice.py` that return mock transcripts. | Bhashini API integration. Real-time translation, Indic language STT/TTS routing. |
| **AI Trend Generation & Explanations** | Static rule-based strings generated based on predefined thresholds in `dashboard.py`. | Optionally Bhashini/LLM integration to provide contextualized natural language summaries for caregivers. |
| **Notifications (SMS/Push)** | `NOTIFICATIONS_LOG` in memory. `print()` statements simulating SMS to console. | E-mail via Resend, or Push notifications (e.g., via FCM/Supabase Edge Functions). |
| **Frontend Routing & State** | Works locally with Vite dev server or static build. API calls hit `127.0.0.1:8000`. | Deployed to Vercel. API URLs dynamically pulled from `process.env.VITE_API_BASE_URL`. |
| **Background Cron/Jobs (e.g., missed reminders)** | Assumed to be simulated on endpoint calls or missing. | Supabase pg_cron or Render cron jobs to execute reminder escalation scripts. |

## 2. Refactoring Scope

### A. Database and ORM / Supabase Integration
*   **Remove:** `backend/app/mock_data.py` entirely.
*   **Add:** Database connection logic (`backend/app/core/db.py` or similar).

### B. Route Refactoring (Files to update)
Every endpoint in `backend/app/api/` needs to replace `from app.mock_data import ...` with actual DB queries:
*   `activity.py` -> Replace local `ACTIVITY_LOGS` lists with DB CRUD.
*   `appointments.py` -> Replace `APPOINTMENT_PREPS` with DB CRUD.
*   `auth.py` -> Remove `get_user_by_email` mock; integrate Supabase Auth admin or verify JWTs from frontend Supabase client.
*   `daily_living.py`, `dashboard.py`, `education.py`, `games.py`, `mood.py`, `notifications.py`, `patients.py`, `regional.py`, `reminders.py`, `reminiscence.py`, `social.py`, `transport.py`, `visits.py`, `wellbeing.py` -> Refactor all endpoints to query PostgreSQL.
*   `schemas.py` -> Ensure Pydantic models align exactly with the new SQL schema.

### C. Frontend Service Refactoring
*   `frontend/src/services/api.js`: Change hardcoded interceptors and Axios base URLs. Attach Supabase Auth tokens if moving to frontend Supabase client auth, or continue using standard JWT headers if keeping custom login.
*   **Voice Integration:** `frontend/src/services/voice.js` or backend `voice.py` needs Bhashini API integration logic.

## 3. Potential Deployment Blockers
*   **CORS Configuration:** The backend `main.py` currently might be configured for `localhost` or `*`. It must strictly allow the Vercel frontend URL.
*   **Database Migrations:** A rigid database schema needs to be established in PostgreSQL before deployment. Alembic (for SQLAlchemy) or Supabase CLI migrations must be set up.
*   **Clock Skew & Timezones:** Python `_now()` mocks currently generate localized time. Server timezone on Render is UTC; the app must gracefully handle timezone offsets (especially for reminders and quiet hours).
*   **Secrets Management:** Local testing didn't require external secrets. Deployments will crash if Vercel and Render don't have the `.env` variables mapped properly in their dashboards.
*   **Audio/WebRTC Restrictions:** Browsers require HTTPS for microphone access (for Bhashini STT). Vercel provides this out-of-the-box, but local testing connecting to Render requires careful configuration.