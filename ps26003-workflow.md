# AI-Based Cognitive Gaming & Memory Assistance Platform for Elderly Dementia Patients in NER
**SIH 2026 — Problem Statement 26003 | Ministry of Development of North Eastern Region (MDoNER) | Theme: MedTech / HealthTech**

> **Purpose of this document:** This is a build spec for an AI coding agent. It defines scope, architecture, data model, module-by-module logic, and a phased build order so a full-fledged working prototype can be generated without further clarification. Where a decision was open-ended, a concrete default is chosen so implementation is unblocked.

---

## 1. Problem Summary

Elderly patients in India's North Eastern Region (NER) face rising dementia/memory-decline cases with poor access to neurological/cognitive care due to remote geography and thin healthcare infrastructure. Caregivers struggle to monitor and engage patients continuously. Build a **PWA-based cognitive training + caregiver monitoring platform** that:

- Delivers adaptive memory/attention/recognition/routine-recall games
- Speaks and listens in Hindi, English, and NER regional languages
- Uses culturally local themes/visuals/sounds for engagement
- Reminds patients about medicines, hydration, activities, appointments
- Gives caregivers/health workers a progress dashboard with alerts
- Works fully offline on cheap Android tablets/phones, syncs when online
- Keeps patient health data secure

**Primary users:** (1) Elderly patient (dementia, mild-moderate), (2) Family caregiver, (3) Community health worker/ASHA-type user, (4) Clinician/admin (read-only aggregate view).

---

## 2. Tech Stack

### 2.1 Given (must use)
| Layer | Technology |
|---|---|
| Frontend / PWA | React, Workbox (service workers), IndexedDB, Web Speech API |
| Backend | FastAPI (Python), PostgreSQL, JWT auth, REST sync APIs |
| Voice / Language | Cloud STT-TTS (Hindi, English, NER languages) with fallback to on-device Web Speech API |
| Dashboard | Recharts / Chart.js for activity & score trends; push/SMS inactivity alerts |
| DevOps | Docker, Git; installable on low-cost Android tablets/phones |

### 2.2 Additions needed to fully satisfy the problem statement
| Need | Addition | Why |
|---|---|---|
| Adaptive difficulty AI | `scikit-learn` (logistic regression / contextual multi-armed bandit) served from a FastAPI microservice, or a simple rule-engine v1 that upgrades to ML v2 | Difficulty must adapt to real performance, not be hardcoded |
| On-device fallback inference | TensorFlow.js / ONNX Runtime Web (optional, v2) | Keeps adaptivity working fully offline, not just gameplay |
| PWA install/manifest | `vite-plugin-pwa` or CRA + Workbox config, `manifest.json` | "Installable on low-cost tablets" requirement |
| State/data caching | `Dexie.js` wrapper over IndexedDB | Cleaner offline read/write than raw IndexedDB |
| Push notifications | Firebase Cloud Messaging (FCM) Web Push | Needed for caregiver/patient reminders when app is backgrounded |
| SMS fallback alerts | Twilio (or a local Indian SMS gateway e.g. MSG91) | NER connectivity is patchy; caregivers need SMS if push fails |
| Regional TTS/STT | Bhashini (Govt. of India NLP mission) APIs, or Azure/Google Cloud Speech as fallback | Bhashini explicitly covers NER + Indian regional languages and is government-endorsed — strong fit for a govt SIH submission |
| i18n | `react-i18next` | Manage Hindi, English, Assamese, Bodo, Khasi, Mizo, Manipuri (Meitei), Nagamese UI strings |
| Auth/session | `passlib` + `python-jose` (JWT), refresh tokens | Pair with FastAPI JWT requirement |
| Containerization | Docker Compose (frontend, backend, Postgres, nginx reverse proxy) | Local dev + deployment parity |
| CI | GitHub Actions (lint, test, build) | Basic hygiene, optional for hackathon MVP |
| Data privacy | Field-level encryption for PII/health notes (`cryptography` / Postgres `pgcrypto`) + DPDP Act 2023 consent flow | India's Digital Personal Data Protection Act applies to health data |

### 2.3 Explicit non-goals for MVP
No native mobile app (PWA covers "installable on tablets/phones" via Add-to-Home-Screen). No real diagnostic/clinical claims — this is a cognitive engagement and monitoring tool, not a medical device; UI copy and reports must say so.

---

## 3. System Architecture

```
┌─────────────────────────────── DEVICE (offline-first) ───────────────────────────────┐
│  React PWA (Service Worker via Workbox)                                              │
│  ├─ Game Engine (4 game modules, difficulty controller)                              │
│  ├─ Voice Layer (Web Speech API primary; Bhashini/cloud STT-TTS when online)          │
│  ├─ Reminder Engine (local schedule + Notification API)                              │
│  ├─ IndexedDB (Dexie): sessions, scores, reminders, profile, sync-queue              │
│  └─ Sync Manager (background sync, retry queue, conflict resolution)                 │
└───────────────────────────────────────┬──────────────────────────────────────────────┘
                                         │ REST (JWT) — resumes when connectivity returns
┌────────────────────────────────────────▼──────────────────────────────────────────────┐
│  FastAPI Backend                                                                       │
│  ├─ Auth Service (JWT issue/refresh, roles: patient/caregiver/health_worker/admin)     │
│  ├─ Sync API (idempotent upsert endpoints, last-write-wins + server timestamp)         │
│  ├─ Adaptive Difficulty Service (scores in → next-difficulty out)                      │
│  ├─ Reminder Service (schedules, delivery status)                                      │
│  ├─ Notification Dispatcher (FCM push → SMS fallback via Twilio/MSG91 on push failure) │
│  ├─ Analytics/Aggregation Service (feeds caregiver dashboard)                          │
│  └─ Voice Proxy (routes to Bhashini/cloud STT-TTS, keeps API keys server-side)         │
└───────────────────────────────────────┬──────────────────────────────────────────────┘
                                         │
                              ┌──────────▼──────────┐
                              │ PostgreSQL (pgcrypto │
                              │ for PII fields)      │
                              └──────────────────────┘
```

**Offline-first principle:** every user-facing action (playing a game, setting a reminder, recording a voice note) must complete and persist to IndexedDB *before* attempting network sync. The UI never blocks on network.

---

## 4. Core Modules

### 4.1 Cognitive Game Engine
Four game families, each with 3 difficulty tiers (Easy/Medium/Hard) and regional-theme skins (village life, festivals, local food/animals per NER state):

1. **Memory Improvement** — card-flip matching, "what changed" spot-the-difference, recall-the-sequence.
2. **Attention & Concentration** — tap-the-odd-one-out, sustained-attention timed taps, sound-source identification (using STT to confirm spoken answers).
3. **Daily Routine Recall** — sequence-the-day (order pictures of morning/meal/medicine/sleep), "did you do X today" voice check-ins.
4. **Pattern & Object Recognition** — culturally local object naming (regional fruits, tools, festival items), pattern completion grids.

Every game session writes a `game_session` record: `{game_type, difficulty, score, reaction_time_avg, errors, completed_at}`.

### 4.2 Adaptive Difficulty (AI/ML)
- **v1 (MVP, rule-based):** if last 3 sessions' accuracy > 80% → raise tier; < 50% → lower tier; else hold. Ships day one, zero training data needed.
- **v2 (ML):** logistic regression / contextual bandit trained on `(accuracy, reaction_time, error_pattern, days_since_last_play) → next_difficulty`, retrained periodically per-patient. Runs as a FastAPI endpoint the game engine calls after each session; falls back to the v1 rule when offline or under-trained.
- Store every difficulty-change decision with its inputs for explainability (a clinician/caregiver should be able to see *why* difficulty moved).

### 4.3 Voice & Multilingual Layer
- Web Speech API (on-device) is the default STT/TTS for zero-connectivity use — supports English/Hindi reasonably; regional language coverage is limited.
- When online, route through **Bhashini** (or cloud STT-TTS) for Assamese, Bodo, Khasi, Mizo, Manipuri (Meitei), Nagamese, Bengali as spoken in NER.
- All UI copy sourced through `react-i18next` locale files, not hardcoded strings, so new regional languages can be added without touching game logic.
- Voice is an *input/output modality*, not a gate: every voice interaction has an equivalent large-button/tap alternative for patients who can't or won't speak to the device.

### 4.4 Reminders
- Categories: Medicine, Hydration, Daily Activity, Medical Appointment.
- Local-first scheduling (works with zero connectivity): stored in IndexedDB, fired via the Notification API + on-screen full-card alert (not just a small OS notification — elderly users need high-visibility prompts) with TTS read-aloud of the reminder text.
- On completion/snooze/miss, patient action is logged and queued for sync; caregiver dashboard reflects adherence.
- **Escalation:** a missed critical reminder (e.g., medicine) unactioned after a configurable window triggers a caregiver push notification, falling back to SMS if push isn't delivered within N minutes.

### 4.5 Caregiver / Health Worker Dashboard
- Recharts/Chart.js views: score trend per game type over time, session frequency/streak, difficulty-tier progression, reminder adherence %, inactivity gaps.
- **Inactivity alert:** no session logged in a configurable threshold (e.g., 48h) → push, then SMS fallback to caregiver.
- Multi-patient view for health workers (one worker may support several elderly users in a village/cluster).
- Everything server-side aggregated so the dashboard is lightweight to render; raw session data stays queryable for clinicians who want detail.

### 4.6 Offline Sync
- Sync queue pattern: every local write gets a `sync_status` (`pending`/`synced`/`conflict`) and a client timestamp + UUID.
- On connectivity restore, Sync Manager POSTs queued items in batches to idempotent `/sync/*` endpoints (server dedupes by UUID).
- Conflict rule: last-write-wins by server timestamp for score/session data (append-only, so true conflicts are rare); patient-profile edits use field-level merge with server timestamp priority.
- Workbox background sync retries automatically; UI shows a simple "waiting to sync (N items)" indicator, never an error that alarms the elderly user.

### 4.7 Elderly-Friendly UI/UX
- Large tap targets (min 64px), high color contrast, minimal text per screen, icon-first navigation, adjustable font size, optional full read-aloud of every screen.
- No more than one decision per screen where possible; a persistent, obvious "Home"/"Help" button.
- Culturally familiar visuals (regional clothing, festivals, food, landscapes) selectable per user's state/language during onboarding.

### 4.8 Security & Privacy
- JWT auth with short-lived access token + refresh token; role-based access control (patient/caregiver/health_worker/admin scopes).
- PII and any free-text health notes encrypted at rest (`pgcrypto` or app-layer `cryptography` Fernet).
- Explicit consent screen for caregiver linkage and data sharing (DPDP Act 2023 alignment); patient/guardian can revoke caregiver access.
- Audit log on all dashboard data access by non-patient roles.

---

## 5. Data Model (PostgreSQL, core tables)

```
users            (id, role[patient|caregiver|health_worker|admin], name, phone,
                  preferred_language, state_region, password_hash, created_at)

patient_profile  (user_id FK, dob_or_age, dementia_stage_note, theme_preference,
                  onboarding_complete, guardian_consent_at)

caregiver_link   (id, caregiver_id FK, patient_id FK, relationship, status[active|revoked])

game_session     (id, patient_id FK, game_type, difficulty, score, accuracy,
                  reaction_time_avg_ms, started_at, completed_at,
                  client_uuid, sync_status)

difficulty_log   (id, patient_id FK, game_type, previous_tier, new_tier,
                  decision_source[rule|ml], inputs_json, decided_at)

reminder         (id, patient_id FK, category[medicine|hydration|activity|appointment],
                  message, schedule_rule, active)

reminder_event   (id, reminder_id FK, patient_id FK, fired_at,
                  action[done|snoozed|missed], client_uuid, sync_status)

alert            (id, patient_id FK, type[inactivity|missed_reminder],
                  triggered_at, channel[push|sms], delivered, resolved)

audit_log        (id, actor_id FK, patient_id FK, action, accessed_at)
```

---

## 6. Key API Endpoints (FastAPI, indicative)

```
POST   /auth/register            POST /auth/login          POST /auth/refresh
GET    /patients/{id}/profile     PUT  /patients/{id}/profile
POST   /caregiver-links           PATCH /caregiver-links/{id}   (revoke)

POST   /sync/game-sessions        (batch upsert, idempotent by client_uuid)
POST   /sync/reminder-events      (batch upsert, idempotent by client_uuid)
GET    /reminders?patient_id=
POST   /reminders

GET    /difficulty/next?patient_id=&game_type=     (v1 rule or v2 ML)

GET    /dashboard/{patient_id}/summary
GET    /dashboard/{patient_id}/trends?game_type=&range=

POST   /voice/stt      (proxies to Bhashini/cloud STT, keeps keys server-side)
POST   /voice/tts

GET    /alerts?patient_id=&status=
```

All endpoints require a JWT bearer token except `/auth/*`; role scopes enforced per-route (e.g., only linked caregivers/health workers can read a given patient's dashboard).

---

## 7. Build Order (phased, each phase independently demoable)

**Phase 0 — Scaffolding**
Docker Compose (React PWA, FastAPI, Postgres, nginx). Base React app with `react-i18next` (English + Hindi seeded), PWA manifest + Workbox service worker registered (installable check passes). FastAPI skeleton with JWT auth and `users`/`patient_profile` tables.

**Phase 1 — Core Game Loop (offline-capable)**
Build one game per family (4 total, Easy tier only) writing to IndexedDB. Local rule-based difficulty (v1). Basic elderly-friendly shell UI (large buttons, home button, font-size toggle).

**Phase 2 — Reminders**
Local reminder scheduling + Notification API + TTS read-aloud. Reminder CRUD screens for caregiver.

**Phase 3 — Sync Layer**
Sync queue + `/sync/*` idempotent endpoints. Background sync via Workbox. Sync-status indicator in UI.

**Phase 4 — Caregiver Dashboard**
Aggregation endpoints + Recharts/Chart.js views (score trends, adherence, inactivity). FCM push integration; Twilio/MSG91 SMS fallback for alerts.

**Phase 5 — Voice & Regional Language**
Web Speech API wiring for all games/reminders. Bhashini (or cloud STT-TTS) proxy endpoints for regional languages; language picker in onboarding; expand `react-i18next` locale set to target NER languages.

**Phase 6 — Adaptive ML Difficulty (v2)**
Train/serve the ML difficulty model from accumulated `game_session` + `difficulty_log` data; A/B against the v1 rule; keep v1 as automatic fallback offline/cold-start.

**Phase 7 — Security, Privacy, Polish**
Field-level encryption, consent flow, audit log, role-based access hardening, accessibility pass (contrast/font/tap-target audit), regional theming assets, final Docker deployment config.

---

## 8. NER-Specific Considerations
- Target languages: Assamese, Bengali (Barak Valley), Bodo, Khasi, Garo, Mizo, Manipuri (Meitei/Meitei Mayek script), Nagamese, plus Hindi/English as bridge languages.
- Prefer **Bhashini** for STT/TTS/translation where coverage exists — it's the Govt. of India NLP initiative built for exactly this multilingual-India use case and strengthens the submission's alignment with a government theme.
- Low-connectivity design isn't optional polish — treat offline mode as the primary mode and "online sync" as the enhancement, given NER's terrain and infrastructure gaps.
- Regional cultural theming (visuals/sounds/festivals per state) should be data-driven (a theme config per region), not hardcoded, so it's easy to extend to more NER states.

---

## 9. Evaluation / Success Metrics to surface in the demo
- Session completion rate and streak length per patient (engagement).
- Score/accuracy trend over time per game type (cognitive engagement proxy — **not** a diagnostic claim).
- Reminder adherence %.
- Time-to-sync after reconnect (offline robustness).
- Caregiver alert delivery latency (push vs SMS fallback).
- Language coverage exercised in demo (show at least one non-Hindi/English NER language end-to-end).

---

## 10. Guardrails for the Building AI
- This is a **cognitive engagement and monitoring tool**, not a diagnostic or clinical device — never phrase outputs as a diagnosis or treatment.
- Offline-first is a hard constraint, not a stretch goal: every core patient-facing flow (play a game, get/act on a reminder) must work with zero connectivity.
- Every screen a dementia patient sees should default to the simplest, largest, most forgiving interaction pattern; put complexity (settings, analytics, multi-patient views) behind the caregiver/health-worker role only.
