# Migration Tracker: Mock to Real DB

This ledger tracks the step-by-step replacement of `mock_data.py` with SQLAlchemy/PostgreSQL logic.
The process is designed to be fully resumable. If interrupted, the AI will read this file and resume from the first `[ ]` Pending item.

Status keys:
`[ ]` Pending
`[~]` In Progress
`[x]` Completed & Tested

## 1. Core Authentication & Users
- [x] `app/api/auth.py`

## 7. Education & Social
- [x] `app/api/education.py`
- [x] `app/api/social.py`

## 3. Core Gameplay & Dashboard
- [x] `app/api/dashboard.py`
- [x] `app/api/games.py`
- [x] `app/services/difficulty.py`

## 4. Care & Daily Living
- [x] `app/api/activity.py`
- [x] `app/api/daily_living.py`
- [x] `app/api/mood.py`
- [x] `app/api/reminiscence.py`
- [x] `app/api/wellbeing.py`

## 5. Caregiver Coordination
- [x] `app/api/appointments.py`
- [x] `app/api/reminders.py`
- [x] `app/api/transport.py`
- [x] `app/api/visits.py`

## 7. Education & Social
- [x] `app/api/education.py`
- [x] `app/api/social.py`
