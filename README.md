# SIH PS 26003 — AI-Based Cognitive Gaming & Memory Assistance Platform

> Ministry of Development of North Eastern Region (MDoNER)
> SIH 2026 | Theme: MedTech / HealthTech

A PWA-based cognitive training + caregiver monitoring platform for elderly dementia patients in India's North Eastern Region.
Offline-first, multilingual (EN/HI/AS/KHA/MNI), elderly-friendly (64px tap targets, TTS, large fonts).

---

## Quick Start (one command)

### Option A — Docker (recommended for reviewers)

    docker compose up --build

Then open http://localhost (frontend) and http://localhost:8000/docs (backend API docs).

### Option B — Local dev (no Docker)

    # Terminal 1 — Backend
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

    # Terminal 2 — Frontend
    cd frontend
    npm install
    npm run dev
    # Open http://localhost:3000

---

## Demo Accounts

| Role           | Email                  | Password     |
|----------------|------------------------|--------------|
| Patient (Assam)| patient1@ner.in        | patient1pass |
| Patient (Meghalaya) | patient2@ner.in   | patient2pass |
| Patient (Manipur)   | patient3@ner.in   | patient3pass |
| Caregiver 1    | caregiver1@ner.in      | cg1pass      |
| Caregiver 2    | caregiver2@ner.in      | cg2pass      |
| Health Worker  | hw1@ner.in             | hw1pass      |
| Admin          | admin@ner.in           | adminpass    |

---

## What's Mocked vs. Real

| Layer               | Prototype behaviour                                      | Production swap             |
|---------------------|----------------------------------------------------------|-----------------------------|
| Database            | In-memory Python dicts (`backend/app/mock_data.py`)      | PostgreSQL                  |
| Adaptive difficulty | v1 rule engine (real logic, deterministic)               | v2 ML service               |
| Voice STT/TTS       | Browser Web Speech API — stubs: `getCloudSTT/TTS()`     | Bhashini / cloud STT-TTS    |
| Push notifications  | In-app toast + Notifications log screen                  | Firebase Cloud Messaging    |
| SMS alerts          | Console log + Notifications log — tagged [SMS SIMULATION] | Twilio / MSG91             |
| Auth                | Real JWT, against in-memory user store                   | DB-backed user registration |
| Offline sync        | **Real** — IndexedDB (Dexie) + Workbox background sync  | Same, against Postgres      |
| Consent flow        | UI/flow only — no field-level encryption                 | pgcrypto / Fernet           |

All mocked integration points are tagged `// MOCK:` (JS) or `# MOCK:` (Python) — search for that string to find every stub that needs a real implementation.

---

## Definition-of-Done Checklist (manual verification)

Run through each step after `docker compose up --build`:

1. [ ] Log in as patient1@ner.in, patient2@ner.in, patient3@ner.in, caregiver1@ner.in, hw1@ner.in, admin@ner.in — all succeed with correct role.
2. [ ] Log in as patient1@ner.in. Play all 4 game types (Memory Match, Spot the Odd, Daily Routine, Object Names). After playing, verify a game session record appears via the backend API (`GET /dashboard/user-patient-1/summary`).
3. [ ] As patient, go to Reminders. Tap a reminder → full-screen card appears → TTS reads the message → tap Done / Remind Later → action is logged.
4. [ ] Go to Settings. Switch language to हिंदी — verify app text switches app-wide. Switch back to English. Try Assamese, Khasi, Meitei.
5. [ ] In browser DevTools → Network → "Offline". Play a game. Verify the session is saved locally (no error shown). Go back online. Verify the sync indicator briefly shows N items → disappears as sync drains.
6. [ ] Log in as caregiver1@ner.in → Dashboard. Verify:
       - Score trend chart shows lines (30 days of mock data for each game type).
       - Reminder adherence % is shown (around 60%).
       - Alerts section shows the 2 seeded [SMS SIMULATION] alerts.
       - Notifications log shows simulated SMS entries.
7. [ ] In Chrome → Address bar → install icon → Install app. Verify PWA installs to home screen / taskbar.

---

## Architecture

    Frontend (React PWA / Vite)
      ├─ 4 game modules (Memory, Attention, Routine, Recognition)
      ├─ Web Speech API — STT + TTS (stubs for Bhashini)
      ├─ Reminder Engine (Notification API + full-screen card)
      ├─ IndexedDB via Dexie — offline data store
      └─ Sync Manager — queues local writes, flushes on reconnect

    Backend (FastAPI / Python — in-memory for prototype)
      ├─ JWT auth (7 seeded accounts, 4 roles)
      ├─ Sync endpoints — idempotent upsert by client_uuid
      ├─ Difficulty v1 rule engine
      ├─ Dashboard aggregation (summary + trends)
      ├─ Alerts + Notifications log (simulated)
      └─ Voice proxy stubs (# MOCK: tagged)

    Docker Compose — frontend + backend (no DB container for prototype)

---

## Phase 6 (Deferred)

ML difficulty v2 is out of scope for this prototype. The `/difficulty/next` endpoint is structured so a drop-in ML service replaces the rule engine with no frontend changes. See `backend/app/services/difficulty.py` for the swap point.

---

## File Structure

    brain_blast/
    ├── backend/
    │   ├── app/
    │   │   ├── main.py               FastAPI entry point
    │   │   ├── mock_data.py          In-memory data + seed fixtures
    │   │   ├── api/                  auth.py, patients.py, games.py,
    │   │   │                         reminders.py, dashboard.py, voice.py,
    │   │   │                         notifications.py, schemas.py, dependencies.py
    │   │   ├── core/                 auth.py (JWT), config.py
    │   │   └── services/             difficulty.py (v1 rule engine)
    │   ├── scripts/
    │   │   └── smoke_test.py         17 assertions — run to verify backend
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── frontend/
    │   ├── src/
    │   │   ├── App.jsx               Router + auth guards
    │   │   ├── main.jsx              Entry point
    │   │   ├── i18n.js               react-i18next init (EN/HI/AS/KHA/MNI)
    │   │   ├── locales/              en.json hi.json as.json kha.json mni.json
    │   │   ├── components/           AuthContext, ReminderCard, SyncIndicator
    │   │   ├── pages/                Login, PatientHome, GameShell, CaregiverDashboard,
    │   │   │                         Reminders, Settings, Notifications
    │   │   ├── games/                MemoryGame, AttentionGame, RoutineGame, RecognitionGame
    │   │   └── services/             api.js, db.js (Dexie), voice.js, syncManager.js
    │   ├── Dockerfile
    │   ├── vite.config.js
    │   └── nginx.conf
    ├── TASKS.md                      Build progress tracker — read first on resume
    ├── docker-compose.yml
    └── README.md                     This file
