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
    RegisterRequest, AdminAssignCaregiverRequest
)
from app.core.auth import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.db import get_db
from app.models import User, PatientProfile, Notification, CaregiverLink

router = APIRouter(prefix="/auth", tags=["auth"])

def is_valid_password(password: str) -> bool:
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    if len(password) < 8: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[0-9]", password): return False
    return True

@router.post("/register", response_model=TokenResponse, status_code=201)
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
        target_user_id=new_user.id,
        patient_id=new_user.id if body.role == "patient" else None,
        message=f"Welcome to Brain Blast, {body.name}! We're glad to have you.",
        channel="in_app",
        created_at=datetime.now(timezone.utc)
    )
    db.add(welcome_msg)
    db.commit()

    token_data = {"sub": str(new_user.id), "role": new_user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user_id=str(new_user.id),
        role=new_user.role,
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
