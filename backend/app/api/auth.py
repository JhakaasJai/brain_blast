"""
Auth endpoints: /auth/login, /auth/refresh, /auth/register
"""
import uuid
import re
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.schemas import (
    LoginRequest, TokenResponse, RefreshRequest, UserOut, UserUpdate, 
    RegisterRequest, AdminAssignCaregiverRequest, VerifyEmailRequest
)
from app.core.auth import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.db import get_db
from app.models import User, PatientProfile, Notification, CaregiverLink
import resend
import os

router = APIRouter(prefix="/auth", tags=["auth"])
resend.api_key = os.getenv("RESEND_API_KEY")

def is_valid_password(password: str) -> bool:
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    if len(password) < 8: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[0-9]", password): return False
    return True

@router.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if not is_valid_password(body.password):
        raise HTTPException(
            status_code=400, 
            detail="Password must be at least 8 characters long, include an uppercase letter, a lowercase letter, and a number."
        )
        
    existing_user = db.query(User).filter(User.email == body.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    new_user = User(
        id=uuid.uuid4(),
        email=body.email,
        name=body.name,
        role=body.role,
        phone=body.phone,
        password_hash=get_password_hash(body.password),
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.flush()

    if body.role == "patient":
        profile = PatientProfile(user_id=new_user.id)
        db.add(profile)

    # Welcome notification
    welcome_msg = Notification(
        id=uuid.uuid4(),
        user_id=new_user.id,
        target_user_id=new_user.id,
        message=f"Welcome to Brain Blast, {body.name}! We're glad to have you.",
        channel="in_app",
        created_at=datetime.now(timezone.utc)
    )
    db.add(welcome_msg)
    db.commit()

    # Generate verification token
    from datetime import timedelta
    verify_token = create_access_token(
        {"sub": str(new_user.id), "type": "verify"}, 
        expires_delta=timedelta(hours=24)
    )
    
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verify_link = f"{frontend_url}/verify-email?token={verify_token}"
    
    if resend.api_key:
        try:
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": body.email,
                "subject": "Verify your Brain Blast account",
                "html": f'<p>Welcome to Brain Blast!</p><p>Please click <a href="{verify_link}">here</a> to verify your account.</p>'
            })
        except Exception as e:
            print(f"Error sending email: {e}")
            
    return {"message": "Registration successful. Please check your email to verify your account."}

@router.post("/verify-email", response_model=TokenResponse)
def verify_email(body: VerifyEmailRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.token)
    if not payload or payload.get("type") != "verify":
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
    user_id = payload.get("sub", "")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_verified = True
    db.commit()
    
    token_data = {"sub": str(user.id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user_id=str(user.id),
        role=user.role,
    )

@router.get("/admin/users", response_model=list[UserOut])
def admin_list_users(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return db.query(User).order_by(User.created_at.desc()).all()

@router.post("/admin/assign-caregiver")
def admin_assign_caregiver(
    body: AdminAssignCaregiverRequest, 
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
        
    caregiver = db.query(User).filter(User.id == body.caregiver_id, User.role == "caregiver").first()
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found or invalid role")
        
    patient = db.query(User).filter(User.id == body.patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or invalid role")
        
    existing = db.query(CaregiverLink).filter(
        CaregiverLink.caregiver_id == body.caregiver_id,
        CaregiverLink.patient_id == body.patient_id
    ).first()
    
    if existing:
        existing.status = "active"
        existing.relationship = body.relationship
    else:
        link = CaregiverLink(
            id=uuid.uuid4(),
            caregiver_id=body.caregiver_id,
            patient_id=body.patient_id,
            relationship=body.relationship,
            status="active"
        )
        db.add(link)
        
    db.commit()
    return {"ok": True, "detail": "Caregiver successfully assigned"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(body: UserUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    updates = body.model_dump(exclude_none=True)
    for k, v in updates.items():
        setattr(user, k, v)
        current_user[k] = v
        
    db.commit()
    return current_user


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before logging in."
        )
        
    token_data = {"sub": str(user.id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user_id=str(user.id),
        role=user.role,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    user_id = payload.get("sub", "")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    token_data = {"sub": str(user.id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user_id=str(user.id),
        role=user.role,
    )
