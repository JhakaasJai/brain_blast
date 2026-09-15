"""Quick smoke-test script for the backend API."""
import sys
import urllib.request
import urllib.error
import json

BASE = "http://127.0.0.1:8000"

def req(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()}

# Health
h = req("GET", "/health")
assert h == {"status": "ok"}, f"health failed: {h}"
print("OK /health")

# Login — all 7 roles
accounts = [
    ("patient1@ner.in",   "patient1pass",  "patient"),
    ("patient2@ner.in",   "patient2pass",  "patient"),
    ("patient3@ner.in",   "patient3pass",  "patient"),
    ("caregiver1@ner.in", "cg1pass",       "caregiver"),
    ("caregiver2@ner.in", "cg2pass",       "caregiver"),
    ("hw1@ner.in",        "hw1pass",       "health_worker"),
    ("admin@ner.in",      "adminpass",     "admin"),
]
tokens = {}
for email, pw, role in accounts:
    r = req("POST", "/auth/login", {"email": email, "password": pw})
    assert "access_token" in r, f"Login failed for {email}: {r}"
    assert r["role"] == role, f"Wrong role for {email}: {r}"
    tokens[email] = r["access_token"]
    print(f"OK login {email} -> role={role}")

# Patient profile (caregiver reads patient1)
cg1_tok = tokens["caregiver1@ner.in"]
profile = req("GET", "/patients/user-patient-1/profile", token=cg1_tok)
assert "dob_or_age" in profile, f"Profile failed: {profile}"
print(f"OK /patients/user-patient-1/profile name_from_mock=Rina Borah dob={profile['dob_or_age']}")

# Dashboard summary
summary = req("GET", "/dashboard/user-patient-1/summary", token=cg1_tok)
assert "total_sessions" in summary, f"Dashboard failed: {summary}"
print(f"OK /dashboard/user-patient-1/summary sessions={summary['total_sessions']} adherence={summary['reminder_adherence_pct']}%")

# Trends
trends = req("GET", "/dashboard/user-patient-1/trends?game_type=memory&range=30", token=cg1_tok)
assert "points" in trends, f"Trends failed: {trends}"
print(f"OK /dashboard/user-patient-1/trends points={len(trends['points'])}")

# Difficulty v1 rule engine
diff = req("GET", "/difficulty/next?patient_id=user-patient-1&game_type=memory", token=cg1_tok)
assert "next_tier" in diff, f"Difficulty failed: {diff}"
print(f"OK /difficulty/next decision={diff['decision_source']} tier={diff['current_tier']}→{diff['next_tier']} reason={diff['reason'][:60]}")

# Alerts
alerts = req("GET", "/alerts", token=cg1_tok)
assert isinstance(alerts, list), f"Alerts failed: {alerts}"
print(f"OK /alerts count={len(alerts)}")

# Reminders
rems = req("GET", "/reminders?patient_id=user-patient-1", token=cg1_tok)
assert isinstance(rems, list) and len(rems) > 0, f"Reminders failed: {rems}"
print(f"OK /reminders count={len(rems)}")

# Voice stubs
p1_tok = tokens["patient1@ner.in"]
stt = req("POST", "/voice/stt", {"audio_base64": "dGVzdA==", "language": "as"}, token=p1_tok)
assert stt["source"] == "web_speech_fallback", f"STT failed: {stt}"
print(f"OK /voice/stt source={stt['source']}")

# Sync a new game session
import uuid
new_uuid = str(uuid.uuid4())
sync = req("POST", "/sync/game-sessions", {
    "sessions": [{
        "patient_id": "user-patient-1",
        "game_type": "memory",
        "difficulty": "easy",
        "score": 750,
        "accuracy": 75.0,
        "reaction_time_avg_ms": 1800,
        "errors": 2,
        "started_at": "2026-09-15T10:00:00+00:00",
        "completed_at": "2026-09-15T10:15:00+00:00",
        "client_uuid": new_uuid,
    }]
}, token=p1_tok)
assert sync["synced"] == 1 and sync["skipped"] == 0, f"Sync failed: {sync}"
print(f"OK /sync/game-sessions synced={sync['synced']}")

# Idempotency: same UUID should be skipped
sync2 = req("POST", "/sync/game-sessions", {
    "sessions": [{"patient_id":"user-patient-1","game_type":"memory","difficulty":"easy",
                  "score":750,"accuracy":75.0,"reaction_time_avg_ms":1800,"errors":2,
                  "started_at":"2026-09-15T10:00:00+00:00","completed_at":"2026-09-15T10:15:00+00:00",
                  "client_uuid": new_uuid}]
}, token=p1_tok)
assert sync2["synced"] == 0 and sync2["skipped"] == 1, f"Idempotency failed: {sync2}"
print(f"OK /sync/game-sessions idempotency skipped={sync2['skipped']}")

# Role guard: patient should not read another patient's dashboard
summary403 = req("GET", "/dashboard/user-patient-2/summary", token=p1_tok)
assert summary403.get("error") == 403 or "detail" in summary403, f"Should be 403: {summary403}"
print(f"OK role guard: patient1 blocked from patient2 dashboard")

print("\n=== ALL SMOKE TESTS PASSED ===")
