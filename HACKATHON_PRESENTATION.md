# Brain Blast — Hackathon Presentation Guide
## SIH Problem Statement PS-26003
### AI-Based Cognitive Gaming & Memory Assistance Platform for Elderly Dementia Patients in NER

---

## PART 1 — TECH STACK

### Frontend
| Layer          | Technology            | Why                                                       |
|----------------|-----------------------|-----------------------------------------------------------|
| Framework      | React 19 + Vite 8     | Fast SPA, hot-reload dev, tiny production bundle          |
| Routing        | React Router v7       | Client-side navigation, role-based route guards           |
| HTTP client    | Axios                 | JWT interceptor, auto-refresh on 401, 422 error normalise |
| Offline DB     | Dexie (IndexedDB)     | Game sessions and reminders saved locally when offline    |
| Sync engine    | Custom syncManager.js | Queues writes offline, flushes when connection returns    |
| PWA            | vite-plugin-pwa       | Installable on Android/desktop, works without internet    |
| Charts         | Recharts              | Score trend line charts on caregiver dashboard            |
| i18n           | i18next               | Multi-language support (English + regional NER languages) |
| Voice/TTS      | Web Speech API        | Read-aloud for elderly patients with low literacy         |
| Deployment     | Vercel                | Zero-config CI/CD on every git push to main               |

### Backend
| Layer          | Technology              | Why                                                         |
|----------------|-------------------------|-------------------------------------------------------------|
| Framework      | FastAPI 0.111           | Async, auto OpenAPI docs at /docs, Pydantic validation      |
| Server         | Uvicorn + uvloop        | Production ASGI server, high concurrency                    |
| ORM            | SQLAlchemy 2.0          | Type-safe DB queries, migration-friendly models             |
| Auth           | python-jose + passlib   | JWT access + refresh tokens, bcrypt password hashing        |
| Email          | Resend SDK              | Email verification on registration                          |
| Deployment     | Render                  | Auto-deploy from GitHub, Python 3.11, managed environment   |

### Database
| Layer          | Technology              | Why                                                         |
|----------------|-------------------------|-------------------------------------------------------------|
| Database       | PostgreSQL (Supabase)   | Managed Postgres, Connection Pooler for Render compatibility|
| Driver         | psycopg2-binary         | Binary wheel, no build step needed on Render                |

### Architecture at a glance

```
Patient / Caregiver / HW / Admin
         |
  [ React PWA — Vercel ]
         |  HTTPS REST (JWT Bearer)
  [ FastAPI — Render ]
         |  SQLAlchemy ORM
  [ PostgreSQL — Supabase ]
```

---

## PART 2 — HOW THE PROJECT WORKS

### The Problem
India's North East Region has a growing population of elderly dementia patients with very limited
access to specialists. Caregivers and ASHA health workers have no coordinated digital tool.
Patients drift into isolation, miss medications, and forget daily routines. Families have no
real-time view of how their loved one is doing.

### What Brain Blast Does
Brain Blast is a full-stack web platform that serves FOUR user roles, each with a purpose-built
interface, all connected through one shared backend.

---

### USER ROLES

**1. Patient (elderly dementia patient)**
- Logs in and sees a large-button, accessible home screen
- Plays 4 cognitive games: Memory, Attention, Routine, Recognition
- AI adapts game difficulty automatically based on past performance (DifficultyLog)
- Logs daily mood and sleep quality
- Logs physical activity
- Marks daily tasks as done (morning routine, meals, etc.)
- Does safety check-ins ("I am safe today")
- Reads/receives social messages from family
- Reviews medication reminders
- Browser reads the page aloud (Web TTS) for low-literacy users
- Works offline — game sessions saved to IndexedDB, synced later

**2. Caregiver (family member or paid carer)**
- Dashboard shows real assigned patients (from CaregiverLink table)
- Live score trend charts (accuracy % over 30 days, per game type)
- Alert feed (inactivity alerts, missed sessions)
- Manages medication reminders for each patient
- Writes handover / care notes
- Prepares appointment notes (doctor name, questions, items to bring)
- Creates transport notes (pickup point, driver, route)
- Views mood and sleep history
- Caregiver wellbeing check-in (their own stress/burnout tracking)
- Education library (dementia care articles)

**3. Health Worker / ASHA**
- Same dashboard as caregiver
- Linked to patients via HWPatientMap (separate from CaregiverLink)
- Route and visit planning (schedule home visits, mark completed/cancelled)
- Access to appointment prep and transport notes
- Can manage reminders just like caregiver

**4. Admin**
- Sees ALL users and ALL patients in the system
- Assigns caregivers to patients (POST /auth/admin/assign-caregiver)
  — works for both caregivers (CaregiverLink) and health workers (HWPatientMap)
- Full audit log of all actions
- Control panel with user management table

---

### DATA FLOW — step by step for a single patient session

```
1. Patient opens app on phone (PWA / browser)
2. Login → POST /auth/login → JWT (access + refresh token) stored in localStorage
3. Home screen loads → GET /patients/{id}/profile (name, dementia stage)
4. GET /difficulty/next?patient_id=...&game_type=memory
   Backend reads DifficultyLog, returns 'easy'/'medium'/'hard'
5. Patient plays Memory Game
6. On finish → score saved to IndexedDB (offline-first)
7. syncManager flushes → POST /sync/game-sessions → GameSession row created
8. Caregiver opens dashboard → GET /my-patients → list of linked patients
9. GET /dashboard/{patient_id}/summary → totals, streak, inactivity hours
10. GET /dashboard/{patient_id}/trends?game_type=memory → accuracy time series
11. Chart renders. Caregiver sees patient's weekly trend instantly.
12. Caregiver sets a medicine reminder → POST /reminders
    Backend checks caregiver is linked to that patient before allowing
13. Patient gets reminder notification → GET /notifications/
14. Patient marks safety check-in → POST /patients/{id}/safety-check-in
15. Health worker opens visit planning → GET /health-worker/visits
16. Health worker marks visit completed → PATCH /health-worker/visits/{id}
```

---

### KEY TECHNICAL DECISIONS

**JWT with refresh tokens**
Access token expires in 30 minutes. Axios interceptor on the frontend silently
refreshes using the refresh token. User never gets kicked out mid-session.

**Role-based access control on every endpoint**
`get_patients_for_user(current_user, db)` is called on every patient-scoped
endpoint. Caregiver → CaregiverLink table. Health worker → HWPatientMap.
Admin → all patients. A caregiver cannot read another caregiver's patient.

**Offline-first gaming**
Dexie (IndexedDB) stores game sessions locally. syncManager checks online
status and flushes the queue. This is critical for NER where connectivity
is intermittent. The UI shows a sync indicator.

**Adaptive difficulty**
After each session, the backend reads the last 5 sessions for that game type.
If accuracy > 80% consistently, difficulty steps up. Below 50%, steps down.
This is real personalised AI without an LLM — pure rule-based adaptation.

**Pydantic v2 field_serializer pattern**
SQLAlchemy returns UUID and datetime objects. Pydantic v2 strict mode rejects
them if the schema declares `str`. Every response schema uses `id: Any` +
`@field_serializer("id")` → `str(v)` to coerce correctly at serialization time.

**Seeded demo data**
On every cold start, `seed.py` runs and inserts: 4 demo users, patient profile,
56 game sessions, 14 mood check-ins, 14 activity logs, 15 daily tasks, 3
medications, 4 emergency contacts, 7 safety check-ins, 12 social messages,
2 appointment preps, 2 transport notes, 13 notifications, 2 alerts.
This means the demo always has real-looking data with zero setup from the judge.

---

## PART 3 — HACKATHON DEMO SCRIPT

### Credentials (live on https://brain-blast-backend.onrender.com)
```
Patient:    patient@ner.in   / patpass
Caregiver:  caregiver@ner.in / carepass
Health Worker: hw@ner.in     / hwpass
Admin:      admin@ner.in     / adminpass
```

Frontend URL: your Vercel deployment URL

---

### OPENING SPEECH (30 seconds)

"Good [morning/afternoon]. We are presenting Brain Blast — our solution to
SIH Problem Statement PS-26003.

Dementia affects over 5 million people in India. In the North East, specialist
access is nearly zero. Patients forget routines, miss medications, and families
have no visibility. Caregivers burn out with no coordination tool.

Brain Blast is a full-stack, offline-capable web platform that connects the
patient, caregiver, health worker, and admin in one system — each with their
own purpose-built interface — backed by adaptive AI and real-time data.

Let me show you how it works."

---

### DEMO FLOW — STEP BY STEP

---

#### STEP 1 — Patient login (2 minutes)

Action: Open the frontend URL. Login as patient@ner.in / patpass.

Say:
"This is the patient home screen. Notice the large buttons — designed for
elderly users with low vision or limited digital literacy. The patient
can tap the speaker icon and the entire page is read aloud using the
device's Text-to-Speech. This works in regional languages too."

Show: The four game tiles — Memory, Attention, Routine, Recognition.

---

#### STEP 2 — Play a cognitive game (2 minutes)

Action: Tap Memory Game. Play one round.

Say:
"This is the Memory Card game. The difficulty was set automatically by our
backend. When this patient started, it was on Easy. After consistently
scoring above 80%, the system moved them to Medium — no manual tuning by
the caregiver required. This is adaptive AI built on real session history."

Show: Game completes. Show the result screen with the accuracy score.

Say:
"That result is now saved. If this phone had no internet, it would save
to the local browser database and sync later — offline-first design."

---

#### STEP 3 — Patient daily activities (1 minute)

Action: Navigate to Mood check-in. Set mood to Good, sleep to 7 hours. Save.

Say:
"The patient logs how they feel and how they slept today. This feeds into
the caregiver's dashboard automatically."

Action: Navigate to My Day. Show daily task checklist.

Say:
"The daily task list shows morning routine items. The patient taps to mark
each one done. ASHA workers and caregivers can customise this list."

Action: Navigate to Safety check-in. Press the button.

Say:
"One-tap safety confirmation. If the patient doesn't check in, the system
can alert the caregiver. Simple for the patient, powerful for the carer."

---

#### STEP 4 — Caregiver dashboard (3 minutes)

Action: Open a new tab. Login as caregiver@ner.in / carepass.

Say:
"Now I am logged in as the caregiver. The system automatically shows only
the patients assigned to this caregiver — role-based access control. The
admin assigned this patient through the admin panel."

Show: The patient is already selected in the dropdown.

Say:
"Look at the summary cards — total sessions, this week's sessions, day
streak, average accuracy over 7 days, and how many hours since last
activity. This is real data from the game sessions the patient just played."

Action: Click the score trend chart. Toggle between Memory, Attention, Routine.

Say:
"This is a 30-day accuracy trend per game type. The caregiver can see at
a glance whether the patient is improving, plateauing, or declining in
each cognitive domain. The system also generates a plain-language
explanation of the trend below the chart."

---

#### STEP 5 — Reminders (1 minute)

Action: Click Manage Reminders.

Say:
"The caregiver manages medication and activity reminders here. Each reminder
has a category, message, time, and frequency. The patient receives these
reminders on their home screen. If a reminder is missed repeatedly, the
system can escalate and notify the caregiver."

Action: Create a new reminder — category Medicine, message "Take Donepezil",
time 09:00, daily.

Say:
"Reminder created. The patient will see this tomorrow morning."

---

#### STEP 6 — Care notes and appointment prep (1 minute)

Action: Click Care Notes. Show existing notes.

Say:
"Handover notes — when multiple caregivers or shift workers cover the same
patient, they leave structured notes here. Nothing is lost in verbal handover."

Action: Navigate to Appointment Prep.

Say:
"Before a hospital visit, the caregiver fills this form — doctor name,
clinic, questions to ask, items to bring, transport notes. The patient
or accompanying person can read this on their phone at the hospital."

---

#### STEP 7 — Health Worker view (1 minute)

Action: Open a new tab. Login as hw@ner.in / hwpass.

Say:
"This is the ASHA health worker view. Same dashboard, but this user is
linked to the patient through the HWPatientMap — a separate assignment
that the admin controls. The health worker can plan home visits here."

Action: Click Plan Visits. Show the visit planning page.

Say:
"The health worker schedules visits by patient, date, purpose, and location.
After the visit they mark it completed. This gives supervisors a full
route history for each ASHA worker."

---

#### STEP 8 — Admin control panel (1 minute)

Action: Open a new tab. Login as admin@ner.in / adminpass.

Say:
"The admin sees all users in the system. They can assign caregivers and
health workers to patients from here. This is how the entire role graph
is managed centrally."

Show: The user table. Show the assign caregiver form.

---

#### STEP 9 — Technical highlight (30 seconds)

Open browser DevTools → Network tab. Reload the caregiver dashboard.

Say:
"Every API call carries a JWT Bearer token. The backend verifies the token,
checks the role, and checks whether this specific caregiver is authorised
to see this specific patient — all in under 50ms. No data leaks between
users. The backend runs on Render, database on Supabase PostgreSQL behind
a connection pooler, frontend on Vercel — fully cloud-native, no servers
to manage."

---

#### CLOSING SPEECH (30 seconds)

"To summarise — Brain Blast solves PS-26003 end to end.

For the patient: cognitive games with adaptive difficulty, daily routine
management, safety check-ins, offline-first.

For the caregiver: real-time dashboard, trend charts, reminders, care notes,
appointment prep, transport coordination, wellbeing tracking.

For the ASHA health worker: visit planning, the same clinical tools as caregivers.

For the system: role-based security, audit logs, admin control.

All connected. All real data. All live. Thank you."

---

## PART 4 — JUDGE QUESTIONS AND ANSWERS

**Q: How does the AI work?**
A: Adaptive difficulty is rule-based AI — the backend reads the patient's
last 5 game sessions for each game type and adjusts difficulty up or down
based on accuracy thresholds. No LLM is needed for this. For future work,
we plan natural language summarisation of care trends using Bhashini's
regional-language NLP models.

**Q: What happens without internet?**
A: The frontend is a PWA. Game sessions are written to IndexedDB first.
The sync manager detects when the connection returns and flushes the queue
to the backend. All other pages show cached data and disable write actions
gracefully.

**Q: How is patient data kept private?**
A: Every patient-scoped endpoint calls `get_patients_for_user()` which checks
the CaregiverLink or HWPatientMap table. A caregiver can only see patients
explicitly assigned to them by an admin. JWTs are short-lived (30 min) with
refresh tokens. Passwords are bcrypt-hashed. Full audit log on sensitive reads.

**Q: Why NER specifically?**
A: Problem statement PS-26003 targets NER. The platform supports multi-language
via i18next (Assamese, Meitei, Khasi can be added). The adaptive game difficulty
compensates for varying education levels. The offline-first design handles
poor connectivity common in rural NER.

**Q: Can this scale?**
A: Yes. Supabase PostgreSQL scales horizontally. Render can add instances.
The backend is stateless (JWT) so multiple Render instances work without
session sharing. The frontend on Vercel CDN serves globally.

**Q: Is the data real or mocked?**
A: Real. The database is a live Supabase PostgreSQL instance. The seed script
creates realistic historical data on first deploy. All API calls go to the
real backend. The admin panel loads real user rows. Every number you see
on the dashboard is computed from real database records.

---

## PART 5 — QUICK REFERENCE CARD (print this for the table)

```
URLs
  Frontend  : [your Vercel URL]
  Backend   : https://brain-blast-backend.onrender.com
  API Docs  : https://brain-blast-backend.onrender.com/docs

LOGIN CREDENTIALS
  Patient       patient@ner.in   / patpass
  Caregiver     caregiver@ner.in / carepass
  Health Worker hw@ner.in        / hwpass
  Admin         admin@ner.in     / adminpass

TECH STACK
  Frontend   React 19 + Vite + Axios + Dexie + i18next + PWA
  Backend    FastAPI + SQLAlchemy + Pydantic v2 + python-jose
  Database   PostgreSQL on Supabase (Connection Pooler)
  Hosting    Vercel (FE) + Render (BE)

KEY FEATURES
  4 adaptive cognitive games (Memory, Attention, Routine, Recognition)
  Auto difficulty scaling from real session history
  Offline-first with IndexedDB + sync queue
  4 user roles with strict role-based access control
  Real-time caregiver dashboard with trend charts
  Medication reminders, daily tasks, safety check-ins
  Appointment prep, transport notes, visit planning
  Multi-language TTS for low-literacy patients
  Audit log, admin control panel
  Seeded demo data — works instantly on first open
```
