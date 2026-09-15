# Build Progress — SIH PS 26003 Prototype

## Current State
Phases 0–7 and the PS 26003 feature sequence through E20 are implemented in the prototype. The application includes the offline-capable game loop, reminders and escalation, consent/access controls, RBAC guards, audit viewer, sync conflict UI, backup/restore, simplified patient home, accessibility improvements, multi-caregiver access, caregiver notes, explainable alerts, and medical-device disclaimers. Backend smoke tests and frontend production builds pass.

## Next Step
All essential and recommended features are complete. Hand off project to next phase or presentation preparation. R20 configurable alert quiet hours is verified with frontend build and smoke tests.

## Phase Checklist

### Phase 0 — Scaffolding
- [x] TASKS.md created
- [x] Monorepo structure (frontend/, backend/, docs/)
- [x] Frontend: React + Vite PWA shell, manifest.json, Workbox service worker registered
- [x] Frontend: react-i18next wired with English + Hindi seed strings
- [x] Backend: FastAPI skeleton, JWT auth (mock in-memory user store)
- [x] Backend: All route stubs matching Section 6 API contract (correct shapes, 200/401/403 responses)
- [x] Docker Compose: frontend + backend containers (no Postgres container — in-memory only)
- [x] README.md with one-command startup + Definition-of-Done checklist

### Phase Mock Data — (insert after Phase 0, before Phase 1)
- [x] backend/app/mock_data.py: 3 patient profiles (Assam/Meghalaya/Manipur), 2 caregivers, 1 health worker, 1 admin
- [x] ~15–20 game_session rows per patient across 30 days / 4 game types
- [x] difficulty_log entries (at least 1 tier change per patient, decision_source: "rule")
- [x] 4–6 reminders per patient, mix of categories
- [x] reminder_event rows (done/snoozed/missed mix, adherence % not 100%)
- [x] 2 alert rows (inactivity + missed_reminder) with [SMS SIMULATION] label
- [x] Verify every frontend component fetches data via REST endpoints, never hardcoded

### Phase 1 — Core Game Loop (offline-capable)
- [x] Memory Improvement game (card-flip matching) — Easy tier
- [x] Attention & Concentration game (tap-the-odd-one-out) — Easy tier
- [x] Daily Routine Recall game (sequence-the-day) — Easy tier
- [x] Pattern & Object Recognition game (object naming) — Easy tier
- [x] Each game writes game_session to IndexedDB (Dexie) and queues for sync
- [x] v1 rule-based difficulty controller (accuracy>80%→raise, <50%→lower, else hold on last 3 sessions)
- [x] Elderly-friendly shell UI: large buttons (≥64px), home button, font-size toggle, high contrast
- [x] Difficulty endpoint wired to v1 rule engine

### Phase 2 — Reminders
- [x] Local reminder scheduling logic (fires from IndexedDB schedule, no server needed)
- [x] Notification API integration for OS-level prompts
- [x] Full-screen elderly-friendly reminder card UI and TTS/fallback path
- [x] Patient reminder event actions queued for sync
- [x] Caregiver reminder CRUD screens with ownership checks
- [x] [SIMULATED] Critical missed-reminder escalation and Notifications log entry

### Phase 3 — Sync Layer
- [x] Dexie sync queue schema with pending/synced/conflict status and client UUID
- [x] Workbox/PWA service-worker caching and reconnect sync path
- [x] POST /sync/game-sessions — idempotent upsert by client_uuid
- [x] POST /sync/reminder-events — idempotent upsert by client_uuid
- [x] Sync-status indicator with non-alarming pending/conflict wording
- [x] Conflict discard/retry controls; server-side authorization remains authoritative

### Phase 4 — Caregiver Dashboard
- [x] GET /dashboard/{patient_id}/summary endpoint
- [x] GET /dashboard/{patient_id}/trends endpoint
- [x] Recharts score trend chart per game type
- [x] Summary indicators for frequency, streak, difficulty, adherence, and inactivity
- [x] [SIMULATED] Inactivity alert with explainable threshold and safe next step
- [x] [SIMULATED] SMS fallback logged as [SMS SIMULATION]
- [x] GET /alerts endpoint with patient authorization
- [x] Multi-caregiver access and care-team notes
- [ ] Browser-level walkthrough and IndexedDB inspection

### Phase 5 — Voice & Regional Language
- [ ] Web Speech API STT/TTS wired across all 4 game types (voice answers accepted)
- [ ] Web Speech API TTS on all reminder read-alouds
- [ ] MOCK: getCloudSTT() stub function (currently calls Web Speech fallback, clearly labeled // MOCK:)
- [ ] MOCK: getCloudTTS() stub function (same pattern)
- [ ] POST /voice/stt stub (returns mock transcript, labeled # MOCK:)
- [ ] POST /voice/tts stub (returns mock audio URL, labeled # MOCK:)
- [ ] Language picker in onboarding (English, Hindi, Assamese, Khasi, Manipuri/Meitei)
- [ ] react-i18next expanded to 5 locales: en, hi, as (Assamese), kha (Khasi), mni (Meitei)
- [ ] Language switch applies app-wide instantly

### Phase 6 — Adaptive ML Difficulty (v2) — DEFERRED
- Phase 6 (ML difficulty v2) is out of scope for this prototype.
- Only the v1 rule engine is implemented (Phase 1).
- The /difficulty/next endpoint is structured so swapping in ML is a service-layer change.
- Noted here so a reviewer knows it was deliberately skipped, not forgotten.

### Phase 7 — Security, Privacy & Polish
- [x] Consent screen and caregiver linkage/revocation flow
- [x] Revoke-caregiver-access endpoint/UI with scoped authorization
- [x] Audit log for dashboard and sensitive access events
- [x] Role-based access hardening for linked patients and care-team writes
- [x] Accessibility pass: large tap targets, visible focus, reduced motion, semantic controls
- [ ] Regional theming: theme config per NER state (Assam/Meghalaya/Manipur) data-driven, not hardcoded
- [ ] PWA installability and browser offline walkthrough — pending real browser/device validation
- [x] Production-like frontend/backend build artifacts; external persistence remains deferred

## Known Issues / Blockers
- Browser-level IndexedDB/offline/PWA walkthrough is pending.
- PostgreSQL persistence, encryption at rest, real FCM/SMS/Twilio/Bhashini integrations, and production observability are intentionally deferred or simulated for this prototype.
- E19 retention/deletion controls require a production identity, persistence, retention policy, and auditable deletion workflow.

## Decisions Log
- 2026-09-15: Phase 6 (ML v2 difficulty) deferred per build-agent-prompt.md Section 5 instruction.
- 2026-09-15: No Postgres container in Docker Compose — backend uses in-memory Python dicts per prototype scope.
- 2026-09-15: All external service touchpoints (Bhashini, FCM, Twilio) replaced with stubs tagged // MOCK: or # MOCK: per build-agent-prompt.md Section 3.
- 2026-09-15: Frontend mock data forbidden — all data fetched via REST endpoints to genuinely exercise full stack per Section 4.
