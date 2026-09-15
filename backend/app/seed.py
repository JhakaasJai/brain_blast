import uuid
from sqlalchemy.orm import Session
from app.core.db import engine, SessionLocal
from app.models import Base, User, PatientProfile, CaregiverLink, HWPatientMap
from app.core.auth import get_password_hash

def seed_db():
    print("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if users are already seeded
        if db.query(User).filter(User.email == "admin@ner.in").first():
            print("Database already seeded. Skipping.")
            return

        print("Seeding database with demo users...")
        admin_id = uuid.uuid4()
        patient_id = uuid.uuid4()
        caregiver_id = uuid.uuid4()
        hw_id = uuid.uuid4()

        users = [
            User(id=admin_id, email="admin@ner.in", role="admin", name="System Admin", phone="0000000000", password_hash=get_password_hash("adminpass")),
            User(id=patient_id, email="patient@ner.in", role="patient", name="Demo Patient", phone="1111111111", password_hash=get_password_hash("patpass")),
            User(id=caregiver_id, email="caregiver@ner.in", role="caregiver", name="Primary Caregiver", phone="2222222222", password_hash=get_password_hash("carepass")),
            User(id=hw_id, email="hw@ner.in", role="health_worker", name="Health Worker (ASHA)", phone="3333333333", password_hash=get_password_hash("hwpass")),
        ]
        
        for u in users:
            db.add(u)
            
        db.flush() # ensure IDs are usable
        
        # Add basic profile and mapping
        profile = PatientProfile(
            user_id=patient_id,
            dob_or_age=75,
            theme_preference="light",
            dementia_stage_note="Early stage"
        )
        db.add(profile)

        link = CaregiverLink(
            id=uuid.uuid4(),
            caregiver_id=caregiver_id,
            patient_id=patient_id,
            relationship="Son",
            status="active"
        )
        db.add(link)
        
        hw_map = HWPatientMap(
            id=uuid.uuid4(),
            hw_id=hw_id,
            patient_id=patient_id
        )
        db.add(hw_map)

        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error seeding DB: {e}")
        db.rollback()
    finally:
        db.close()
