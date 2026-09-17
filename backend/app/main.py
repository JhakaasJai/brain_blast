"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, patients, games, reminders, dashboard, voice, notifications, reminiscence, social, daily_living, mood, activity, education, wellbeing, visits, regional, appointments, transport
from app.seed import seed_db

app = FastAPI(
    title="SMARAN — Cognitive Gaming & Memory Assistance Platform",
    description="AI-Based Cognitive Gaming & Memory Assistance Platform for Elderly Dementia Patients in NER (Prototype)",
    version="0.1.0-prototype",
)

@app.on_event("startup")
def on_startup():
    seed_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(games.router)
app.include_router(reminders.router)
app.include_router(dashboard.router)
app.include_router(voice.router)
app.include_router(notifications.router)
app.include_router(reminiscence.router)
app.include_router(social.router)
app.include_router(daily_living.router)
app.include_router(mood.router)
app.include_router(activity.router)
app.include_router(education.router)
app.include_router(wellbeing.router)
app.include_router(visits.router)
app.include_router(regional.router)
app.include_router(appointments.router)
app.include_router(transport.router)


@app.get("/", tags=["health"])
def root():
    return {
        "status": "ok",
        "service": "smaran-backend",
        "version": "0.1.0-prototype",
        "mock": True,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
