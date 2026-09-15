# Feature Implementation Ledger — PS 26003

This file is the handoff point for future models. Update the row only after code and tests pass. Status values: `planned`, `in_progress`, `implemented`, `verified`, `blocked`, `deferred`.

## Current checkpoint
- Last completed: R20 Configurable alert quiet hours.
- Current feature: Phase 8 Handoff Complete.
- Last verified: E1-E20, R1-R20; R20 configurable alert quiet hours logic verified: settings GET/PATCH, backend dispatch time-window check (handles cross-midnight), and frontend SettingsPage UI implemented; backend smoke and frontend build passed.
- Next action: Project complete! No further SIH PS 26003 features planned.
- Test rule: implement one feature, run tests, fix failures, then advance.

## Essential features
| ID | Feature | Status | Verification |
|---|---|---|---|
| E1 | Person-centered onboarding | verified | `python3 -m compileall -q backend/app && python3 backend/scripts/smoke_test.py`; `npm run build`; focused profile update PASS |
| E2 | Caregiver reminder CRUD | verified | Focused create/update/delete + cross-caregiver 403; backend smoke; frontend build |
| E3 | Reminder escalation workflow | verified | Critical missed-event escalation + simulated notification; compile, smoke, build passed |
| E4 | Emergency contacts and one-tap calling | verified | Scoped contact list, call preview confirmation, unauthorized guard; compile, smoke, build passed |
| E5 | Wandering/location safety | verified | Consent-gated latest safety check-in; no continuous location history; compile, smoke, build passed |
| E6 | Medication safety record | verified | Medication read/create guard and safe missed-dose wording; compile, smoke, build passed |
| E7 | Clinician/health-worker summary export | verified | Authorized care summary + CSV, non-diagnostic disclaimer, RBAC guard; compile, smoke, build passed |
| E8 | Caregiver red-flag safety guidance | verified | Offline-capable guidance page with urgent red flags and emergency-contact link; smoke and frontend build passed |
| E9 | Consent, access sharing, and revocation | verified | Grant listing, patient/caregiver scoped revocation, access isolation, audit events; focused API, smoke, build passed |
| E10 | RBAC hardening | verified | Patient profile/reminder write guards by role; focused API, smoke, build passed |
| E11 | Audit log viewer | verified | Scoped audit endpoint/page, patient isolation; focused API, smoke, build passed |
| E12 | Offline sync status/conflict screen | verified | Pending/conflict indicator, retry, discard controls; smoke and frontend build passed |
| E13 | Backup and restore | verified | Local JSON export/import, version validation, replacement confirmation; smoke and frontend build passed |
| E14 | Simplified patient home screen | verified | Prioritized activity, routine, and emergency actions with plain-language offline state; smoke and frontend build passed |
| E15 | Accessibility audit and improvements | verified | Visible focus, reduced-motion support, semantic patient controls; smoke and frontend build passed |
| E16 | Multi-caregiver support | verified | Multi-caregiver relationship/status view using scoped consent links; smoke and frontend build passed |
| E17 | Caregiver notes and handover log | verified | Scoped note creation/read, care-team write guard, patient isolation; focused API, smoke, build passed |
| E18 | Explainable inactivity alerts | verified | Alert threshold, explanation, safe next step, non-diagnostic wording; focused API, smoke, build passed |
| E20 | Medical-device disclaimer coverage | verified | Reusable translated disclaimer on patient/caregiver surfaces; export disclaimer retained; smoke and frontend build passed |
| E19 | Data retention/deletion controls | deferred | Requires production persistence, verified identity, retention policy, and deletion audit process |

## Recommended features
| ID | Feature | Status |
|---|---|---|
| R1 | Reminiscence therapy | verified | Text prompts seeded by caregiver; patient writes memory notes; cross-patient 403 guard; smoke, focused API checks, frontend build passed |
| R2 | Social connection mode | verified | Async patient-caregiver message thread; cross-patient 403, sender impersonation guard, simulated in-app notification; smoke, focused API, frontend build passed |
| R3 | Daily living assistance | verified | 10-item daily task checklist; toggle/done_at; caregiver view; cross-patient 403; smoke, focused API, frontend build passed |
| R4 | Sleep and mood check-ins | verified | Daily mood (1-5) + sleep hours/quality; score validation; caregiver view; cross-patient 403; smoke, focused API, frontend build passed |
| R5 | Physical activity module | verified | Patient activity log with type, duration, intensity; validation, caregiver view, cross-patient 403; smoke, focused API, frontend build passed |
| R6 | Personalized difficulty calibration | verified | Existing v1 rule engine verified for memory, attention, routine, and recognition; bounded tier output, >=3-session inputs, non-diagnostic reasons; smoke, focused API, frontend build passed |
| R7 | Hint and encouragement system | verified | Patient-controlled hints for all four games; accessible status semantics; supportive completion feedback; non-diagnostic wording; smoke, static UI check, frontend build passed |
| R8 | Game pause and resume | verified | Game-shell pause/resume overlay; accessible dialog; blocks game interaction while preserving mounted game state; backend smoke, static UI check, frontend build passed |
| R9 | Language-specific voice packs | verified | Locale-aware Web Speech tags for en/hi/as plus explicit fallback disclosure for Khasi/Meitei; voice test control and status feedback; backend smoke, static UI check, frontend build passed |
| R10 | Audio-first navigation | verified | Patient-home opt-in narration, stop control, locale-aware voice reuse, navigation announcements, browser fallback handling; backend smoke, static UI check, frontend build passed |
| R11 | Caregiver education library | verified | Care-team article library, per-user read progress, disclaimer, patient role guard, 404 guard; compile, smoke, focused API checks, frontend build passed |
| R12 | Caregiver wellbeing check-ins | verified | Private care-team self-check-ins for energy/stress, support request and notes; score validation and patient role guard; focused API, compile, smoke, frontend build passed |
| R13 | Health-worker route/visit planning | verified | Health-worker/admin route plan with scoped patient visits, create/list/status updates, cancellation, validation, and role guard; focused API, compile, smoke, frontend build passed |
| R14 | Regional theme configuration | verified | Data-driven Assam, Meghalaya, and Manipur palettes; authenticated theme endpoints, patient profile persistence, invalid-theme guard, settings controls; focused API, compile, smoke, frontend build passed |
| R15 | Patient identification profile | verified | Patient identification notes in profile, onboarding form and caregiver dashboard; focused API, compile, smoke, frontend build passed |
| R16 | Appointment preparation | verified | CRUD with RBAC; caregiver creates prep (doctor, clinic, questions, items, transport); patient reads own; cross-patient 403; focused API 9/9 PASS, compile, smoke, frontend build passed |
| R17 | Appointment transport/location notes | verified | Transport notes CRUD + RBAC; mode validation; seeded 3 records; patient reads own; cross-patient 403; focused API 17/17 PASS, compile, smoke, frontend build passed |
| R18 | Caregiver dashboard search/filtering | verified | React state for search query and region filter applied to patient dropdown; frontend build passed |
| R19 | Plain-language trend explanations | verified | Trend endpoint computes stable/improving/declining summary text over time ranges; frontend displays below Recharts graph; smoke + frontend build passed |
| R20 | Configurable alert quiet hours | verified | Quiet hours UI in Settings; `/auth/me` endpoints added; notification dispatcher evaluates cross-midnight window and prepends `[QUIET HOURS HELD]`; smoke + frontend build passed |

## Non-essential / differentiation
| ID | Feature | Status |
|---|---|---|
| N1 | Family timeline | planned |
| N2 | Memory album | planned |
| N3 | Festival/cultural calendar | planned |
| N4 | Music and sound library | planned |
| N5 | Voice diary | planned |
| N6 | Photo object recognition | planned |
| N7 | AI caregiver assistant | planned |
| N8 | Natural-language caregiver notes | planned |
| N9 | Automated weekly report | planned |
| N10 | QR caregiver pairing | planned |
| N11 | Device management | planned |
| N12 | PWA installation helper | planned |
| N13 | Low-bandwidth media optimization | planned |
| N14 | Multidevice synchronization | planned |
| N15 | Anonymous aggregate dashboard | planned |
| N16 | Research/evaluation mode | planned |
| N17 | Feature flags | planned |
| N18 | Health-worker printable visit sheet | planned |
| N19 | Household safety checklist | planned |
| N20 | Voice-controlled caregiver dashboard | planned |

## Technical/security requirements
| ID | Feature | Status |
|---|---|---|
| T1 | Secure token/session handling | planned |
| T2 | Encryption | blocked — requires production persistence/deployment |
| T3 | PostgreSQL persistence | deferred — prototype is intentionally in-memory |
| T4 | API hardening | planned |
| T5 | Robust sync/conflict handling | planned |
| T6 | Unit/API/browser/accessibility tests | in_progress |
| T7 | Observability | planned |
| T8 | Data minimization | planned |

## Safety boundary
Unvalidated diagnosis, dementia progression prediction, medication advice, automatic emergency calls from game scores, opaque risk scores, public leaderboards, and manipulative engagement loops will not be implemented as clinical claims. Any safe alternative will be labeled as support/engagement only.

## Handoff protocol
1. Read this file and `TASKS.md` before changing code.
2. Work only on the first `in_progress`/`planned` feature in dependency order.
3. After implementation, run the relevant backend test/smoke command and `npm run build`.
4. Record exact verification output and change the status to `verified` only after passing.
5. If interrupted, leave `Current checkpoint` and the active feature accurate.
6. Never mark a feature verified based on static inspection alone.

