import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Make sure env vars are loaded even if the server runner doesn't do it
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

DATABASE_URL = os.environ.get("DATABASE_URL")

# Handle Supabase specific connection requirements
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Depending on environment we might need to add sslmode=require
if DATABASE_URL and "sslmode" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"

if DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

Base = declarative_base()

def get_db():
    if not SessionLocal:
        raise RuntimeError("Database URL not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
