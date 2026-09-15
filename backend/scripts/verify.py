"""
Verification script for Phase 0 + Mock Data completion.
Run from the project root: python3 backend/scripts/verify.py
"""
import sys, glob, py_compile, pathlib, json

ROOT = pathlib.Path(__file__).parent.parent.parent  # brain_blast/

errors = []

def check(cond, msg):
    if not cond:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  OK:   {msg}")

print("=== Structure check ===")
required = [
    "backend/app/main.py",
    "backend/app/mock_data.py",
    "backend/app/api/auth.py",
    "backend/app/api/patients.py",
    "backend/app/api/games.py",
    "backend/app/api/reminders.py",
    "backend/app/api/dashboard.py",
    "backend/app/api/voice.py",
    "backend/app/api/notifications.py",
    "backend/app/api/schemas.py",
    "backend/app/api/dependencies.py",
    "backend/app/core/config.py",
    "backend/app/core/auth.py",
    "backend/app/services/difficulty.py",
    "backend/scripts/smoke_test.py",
    "frontend/src/App.jsx",
    "frontend/src/main.jsx",
    "frontend/src/i18n.js",
    "frontend/src/services/api.js",
    "frontend/src/services/db.js",
    "frontend/src/services/voice.js",
    "frontend/src/services/syncManager.js",
    "frontend/src/locales/en.json",
    "frontend/src/locales/hi.json",
    "frontend/src/locales/as.json",
    "frontend/src/locales/kha.json",
    "frontend/src/locales/mni.json",
    "frontend/src/pages/LoginPage.jsx",
    "frontend/src/pages/PatientHomePage.jsx",
    "frontend/src/pages/GameShell.jsx",
    "frontend/src/pages/CaregiverDashboard.jsx",
    "frontend/src/pages/RemindersPage.jsx",
    "frontend/src/pages/SettingsPage.jsx",
    "frontend/src/pages/NotificationsPage.jsx",
    "frontend/src/games/MemoryGame.jsx",
    "frontend/src/games/AttentionGame.jsx",
    "frontend/src/games/RoutineGame.jsx",
    "frontend/src/games/RecognitionGame.jsx",
    "frontend/src/components/AuthContext.jsx",
    "frontend/src/components/ReminderCard.jsx",
    "frontend/src/components/SyncIndicator.jsx",
    "frontend/dist/index.html",
    "frontend/dist/sw.js",
    "frontend/dist/manifest.webmanifest",
    "docker-compose.yml",
    "README.md",
    "TASKS.md",
]
for f in required:
    check((ROOT / f).exists(), f"exists: {f}")

print("\n=== Python syntax check ===")
py_files = list((ROOT / "backend").rglob("*.py"))
for pf in py_files:
    try:
        py_compile.compile(str(pf), doraise=True)
        print(f"  OK:   {pf.relative_to(ROOT)}")
    except py_compile.PyCompileError as e:
        errors.append(str(e))
        print(f"  FAIL: {e}")

print("\n=== JSON locale check ===")
for loc in ["en", "hi", "as", "kha", "mni"]:
    p = ROOT / f"frontend/src/locales/{loc}.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        check("login" in data or "app_name" in data, f"locale {loc}.json has expected keys")
    except Exception as e:
        errors.append(str(e))
        print(f"  FAIL: {e}")

print("\n=== Mock data sanity ===")
sys.path.insert(0, str(ROOT / "backend"))
from app.mock_data import (
    USERS, PATIENT_PROFILES, CAREGIVER_LINKS, GAME_SESSIONS,
    DIFFICULTY_LOG, REMINDERS, REMINDER_EVENTS, ALERTS, NOTIFICATIONS_LOG,
)
check(len([u for u in USERS if u["role"] == "patient"]) == 3, "3 patient accounts")
check(len([u for u in USERS if u["role"] == "caregiver"]) == 2, "2 caregiver accounts")
check(len([u for u in USERS if u["role"] == "health_worker"]) == 1, "1 health worker account")
check(len([u for u in USERS if u["role"] == "admin"]) == 1, "1 admin account")
check(len(GAME_SESSIONS) >= 50, f">=50 game sessions ({len(GAME_SESSIONS)})")
check(len(DIFFICULTY_LOG) >= 4, f">=4 difficulty log entries ({len(DIFFICULTY_LOG)})")
check(len(REMINDERS) >= 14, f">=14 reminders ({len(REMINDERS)})")
check(len(REMINDER_EVENTS) >= 20, f">=20 reminder events ({len(REMINDER_EVENTS)})")
check(len(ALERTS) >= 2, f">=2 alerts ({len(ALERTS)})")
check(any(a["type"] == "inactivity" for a in ALERTS), "inactivity alert present")
check(any(a["type"] == "missed_reminder" for a in ALERTS), "missed_reminder alert present")
check(any("[SMS SIMULATION]" in a.get("simulation_label", "") for a in ALERTS), "SMS SIMULATION label in alerts")
check(len(NOTIFICATIONS_LOG) >= 2, f">=2 notifications ({len(NOTIFICATIONS_LOG)})")

print("\n=== PWA manifest check ===")
manifest = json.loads((ROOT / "frontend/dist/manifest.webmanifest").read_text())
check("icons" in manifest and len(manifest["icons"]) > 0, "manifest has icons")
check(manifest.get("display") == "standalone", "manifest display=standalone")
check("start_url" in manifest, "manifest has start_url")

print(f"\n{'='*40}")
if errors:
    print(f"FAILED — {len(errors)} errors")
    sys.exit(1)
else:
    total = len(required) + len(py_files)
    print(f"ALL PASSED — {total} checks OK")
    sys.exit(0)
