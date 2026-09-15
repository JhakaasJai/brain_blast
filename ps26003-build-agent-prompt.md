# Build Agent Instructions — SIH PS 26003 Prototype
**Companion file to: `ps26003-workflow.md` — read that file FIRST, in full, before writing any code.**

Paste this prompt into your coding agent (Claude Code, Cursor, etc.) alongside `ps26003-workflow.md`. This file tells the agent *how* to build; the workflow file tells it *what* to build.

---

## 0. Your Role

You are building a **working, demoable, full-stack prototype** of the AI-Based Cognitive Gaming & Memory Assistance Platform described in `ps26003-workflow.md` (SIH 2026, PS 26003, MDoNER). You will write real, running code for every module in that spec — but for this prototype phase, backend "intelligence" is simulated with mock data and deterministic logic, not live services (see Section 3). The codebase must still be structured so those mocks can be swapped for real integrations later without a rewrite.

Treat `ps26003-workflow.md` as the single source of truth for scope, architecture, data model, and feature list. If anything here conflicts with it, this file wins on *process* (how to work), that file wins on *product* (what to build).

---

## 1. Anti-Hallucination Rules (non-negotiable)

1. **Build only what's specified.** Every feature you implement must trace back to a line in `ps26003-workflow.md` or an explicit instruction here. Do not invent extra features, screens, or endpoints "because they'd be nice."
2. **Never fabricate library APIs, package names, or versions.** If you're not certain a method/package/import exists as you're about to write it, check the installed package's actual docs/types/source before using it — don't guess and move on.
3. **Never claim something works without running it.** "Implemented X" in the task file only gets checked off after you've actually executed/built/tested it, not after writing the code that should do it.
4. **No silent scope changes.** If you hit a blocker that forces a deviation from the spec (a library doesn't support something, a feature needs a real API key you don't have), log it explicitly in the task file's Decisions Log — don't quietly drop or alter the feature.
5. **State assumptions, don't hide them.** Any time the spec is ambiguous and you make a judgment call, write one line about it in the Decisions Log at the time you make it.

---

## 2. The Task File — Mandatory, Read-First-Every-Session

Create `TASKS.md` at the project root **before writing any other code.** This is how work resumes cleanly across sessions/context resets — always the first file you read when starting or resuming work, and it must always reflect the true current state before you stop working.

### Required structure

```markdown
# Build Progress — SIH PS 26003 Prototype

## Current State
<2-4 sentences: what runs right now, what doesn't yet>

## Next Step
<the single next concrete action — not a list>

## Phase Checklist
### Phase 0 — Scaffolding
- [ ] Monorepo structure (frontend/, backend/, docs/)
- [ ] Frontend: React + Vite PWA shell, manifest.json, Workbox service worker
- [ ] Frontend: react-i18next wired with English + Hindi seed strings
- [ ] Backend: FastAPI skeleton, JWT auth (mock user store, see Sec. 3)
- [ ] Docker Compose: frontend + backend containers (no Postgres container yet — see Sec. 3)
... (mirror every phase from ps26003-workflow.md Section 7, broken into checkable sub-tasks;
     add a "Mock Data" sub-phase after Phase 0 — see Section 4 below)

## Known Issues / Blockers
<anything broken or blocked, with why>

## Decisions Log
<dated one-liners for every judgment call or deviation from spec>
```

**Rules for using it:**
- Update the checklist the moment a sub-task is actually verified working — not in a batch at the end.
- Update "Current State" and "Next Step" every time you stop, even mid-task — assume the next session starts cold with zero memory of this one.
- Never delete history from the Decisions Log; append only.
- If you discover the plan needs to change (a phase should be reordered, split, etc.), edit the checklist to reflect it and note why in the Decisions Log — don't just start ignoring it.

---

## 3. Prototype Scope: What's Real vs. Mocked

This is a **showcase prototype** — no real database, no real cloud/AI service calls. Everything must still be wired through the real architecture (real FastAPI endpoints, real request/response shapes matching the Section 5/6 schema and API list in `ps26003-workflow.md`) so a later swap to production services is a config change, not a rewrite.

| Layer | Prototype behavior | Later (production) |
|---|---|---|
| Database | **In-memory Python data structures** in the FastAPI app (dicts/lists seeded at startup from the mock fixtures in Section 4), exposed through the *same* REST endpoint contracts as the real spec | PostgreSQL, per Section 5 schema |
| Adaptive difficulty | **v1 rule-based logic only** (from workflow Section 4.2) — real, deterministic, no external calls. Do not build or call any ML model. | v2 ML service |
| Voice STT/TTS | **Browser-native Web Speech API only.** Do not call Bhashini or any cloud STT/TTS provider — leave a clearly marked stub function (`getCloudSTT()` / `getCloudTTS()`) that currently just calls the Web Speech fallback, so swapping in a real provider later is a one-function change | Bhashini / cloud STT-TTS |
| Push notifications | **Simulated in-UI**: an in-app toast/banner + an entry in a visible "Notifications" log screen. Do not integrate Firebase. | FCM push |
| SMS alerts | **Simulated**: logged to console and to the same in-app Notifications log, clearly labeled `[SMS SIMULATION]` | Twilio / MSG91 |
| Auth | Real JWT issuing/verification, but against the mock in-memory user store from Section 4 (a handful of seeded accounts) — not a real user-registration/DB-backed flow | Full auth against Postgres |
| Offline sync | **Real** — this genuinely works client-side today: IndexedDB (Dexie) caching, Workbox background sync, and a sync queue against the mock in-memory backend endpoints. Don't fake this part; it's demonstrable as-is. | Same, against Postgres |
| Encryption/DPDP consent flow | UI/flow only (consent screen, revoke-access toggle) — no real field-level encryption needed for mock data | pgcrypto / field encryption |

**Do not add real API keys, `.env` secrets for third-party services, or SDK calls for Bhashini/Firebase/Twilio/any cloud provider in this prototype.** Every "external service" touchpoint must be a clearly named stub/mock function so a reviewer can find and swap every one of them later by searching for `// MOCK:` or `# MOCK:` comments — tag every mocked integration point with that comment.

---

## 4. Mock Data Spec

Seed the in-memory backend at startup (e.g., `backend/app/mock_data.py`) with fixtures matching the Section 5 schema in `ps26003-workflow.md`:

- **3 patient profiles**, each a different NER state/theme/language (e.g., Assam/Assamese, Meghalaya/Khasi, Manipur/Meitei), varied difficulty tiers and onboarding states.
- **2 caregiver accounts** and **1 health-worker account**, linked to patients via `caregiver_link`, plus **1 admin account** — enough to demo every role's dashboard view.
- **~15–20 `game_session` rows per patient** spread over the last 30 days, across all 4 game types, with varying accuracy/reaction time so the dashboard trend charts show real-looking movement (not a flat line).
- Matching **`difficulty_log`** entries showing at least one tier change per patient, with `decision_source: "rule"`.
- **4–6 reminders per patient** across all four categories, with a mix of `reminder_event` outcomes (done/snoozed/missed) so adherence % isn't 100%.
- **A couple of `alert` rows** (one inactivity, one missed-reminder) so the caregiver alert UI has something to show, marked with the appropriate `[SMS SIMULATION]`/push label per Section 3.

Fixtures should be plain Python data (or a JSON file loaded at startup) — not a real database migration. Frontend game/dashboard components must fetch this through the actual REST endpoints (never hardcode mock data directly into React components) so the demo genuinely exercises the full stack.

---

## 5. Build Order

Follow the phase order in `ps26003-workflow.md` Section 7, with these prototype-specific adjustments:
- Insert a **"Mock Data" step right after Phase 0**: build the in-memory data layer and seed fixtures before any game/dashboard UI, so every later phase has real data to hit from day one.
- **Skip** any sub-task that requires a real external API key (Bhashini calls, FCM registration, Twilio account) — replace with the mocked equivalent per Section 3, tagged `// MOCK:`.
- Phase 6 (ML difficulty) is **out of scope for this prototype** — implement only the v1 rule engine; note in the task file that v2 is deferred, don't attempt a fake ML model.
- Everything else in Phases 1–5 and 7 should be built for real (real game logic, real offline sync, real UI/UX polish, real consent-flow screens) — "mocked" applies to external services, not to the app's own logic or UI.

---

## 6. Definition of Done for This Prototype

A reviewer should be able to clone the repo, run one command (document it in `README.md`), and:
1. Log in as a patient, caregiver, health worker, and admin (seeded mock accounts).
2. Play all 4 game types as a patient, see difficulty adjust per the v1 rule after a few sessions.
3. See and act on reminders (mark done/snooze), including the full-screen elderly-friendly reminder UI with TTS read-aloud.
4. Switch the UI language (at least English, Hindi, and one NER regional language) and see it apply app-wide.
5. Go offline (dev-tools network throttling is fine), keep playing/interacting, come back online, and watch the sync queue drain.
6. Log in as a caregiver and see the Recharts/Chart.js dashboard populated with the seeded mock data — score trends, adherence %, and the simulated alert log.
7. Install the app to home screen (PWA installability check passes).

Write this checklist into `README.md` as manual verification steps, and only mark the corresponding `TASKS.md` items complete once you've actually walked through them.

---

## 7. Final Deliverables

- `TASKS.md` — kept current throughout, per Section 2.
- `README.md` — setup/run instructions, the Definition-of-Done checklist from Section 6, and a short "What's mocked vs. real" table (reuse Section 3's table).
- Full monorepo (`frontend/`, `backend/`, `docker-compose.yml`) that runs locally end-to-end with zero external API keys required.
