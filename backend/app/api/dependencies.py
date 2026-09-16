from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import os

from app.core.db import get_db
from app.models import User
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    # Convert SQLAlchemy model to dict to match legacy mock format for easier refactoring
    return {
        "id": str(user.id),
        "role": user.role,
        "email": user.email,
        "name": user.name,
        "phone": user.phone or "",
        "preferred_language": user.preferred_language or "",
        "state_region": user.state_region or "",
        "created_at": str(user.created_at) if user.created_at else "",
        "quiet_hours_start": user.quiet_hours_start,
        "quiet_hours_end": user.quiet_hours_end
    }

def require_caregiver_or_hw(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["caregiver", "health_worker", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted",
        )
    return current_user
