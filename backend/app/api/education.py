"""R11 caregiver education library.
Prototype content is in-memory and educational, not medical advice.
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models import EducationProgress
from app.api.dependencies import get_current_user
from app.api.schemas import (
    EducationArticleListResponse,
    EducationArticleProgressIn,
    EducationArticleProgressOut,
)

EDUCATION_ARTICLES = [
    {
        "id": "1",
        "title": "Understanding Stroke Recovery",
        "summary": "Stroke recovery involves retraining the brain through neuroplasticity.",
        "body": "Stroke recovery is a gradual process that involves retraining the brain (neuroplasticity). With consistent practice and support, many patients can regain significant function. Physical therapy, speech therapy, and occupational therapy are key pillars of recovery.",
        "category": "recovery",
        "language": "en",
        "source_note": "Educational information only; discuss individual care decisions with a qualified clinician.",
        "read_time_minutes": 4,
        "updated_at": "2025-01-01T00:00:00Z",
    },
    {
        "id": "2",
        "title": "Nutrition for Brain Health",
        "summary": "A balanced diet rich in omega-3 fatty acids and antioxidants supports cognitive function.",
        "body": "A diet rich in omega-3 fatty acids, antioxidants, and vitamins supports cognitive function. Foods like fish, leafy greens, berries, and nuts are particularly beneficial. Staying hydrated and limiting processed food also helps maintain brain health.",
        "category": "nutrition",
        "language": "en",
        "source_note": "Educational information only; discuss individual care decisions with a qualified clinician.",
        "read_time_minutes": 3,
        "updated_at": "2025-01-01T00:00:00Z",
    },
    {
        "id": "3",
        "title": "Managing Caregiver Stress",
        "summary": "Caring for a loved one can be demanding — self-care and support networks are vital.",
        "body": "Caring for a loved one can be demanding. It is important to take time for yourself, seek support from friends and caregiver groups, and recognise the signs of burnout early. Regular breaks and professional support can make a significant difference.",
        "category": "wellbeing",
        "language": "en",
        "source_note": "Educational information only; discuss individual care decisions with a qualified clinician.",
        "read_time_minutes": 3,
        "updated_at": "2025-01-01T00:00:00Z",
    }
]

router = APIRouter(tags=["education"])
DISCLAIMER = "Educational information only; discuss individual care decisions with a qualified clinician."

def require_care_team(user: dict) -> None:
    if user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Care team access required")

@router.get("/education/articles", response_model=EducationArticleListResponse)
def list_articles(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    require_care_team(current_user)
    
    rows = db.query(EducationProgress).filter(EducationProgress.user_id == current_user["id"]).all()
    progress = {row.article_id: row.completed for row in rows}
    
    return {"articles": EDUCATION_ARTICLES, "progress": progress, "disclaimer": DISCLAIMER}

@router.patch("/education/articles/{article_id}/progress", response_model=EducationArticleProgressOut)
def update_progress(
    article_id: str,
    body: EducationArticleProgressIn,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_care_team(current_user)
    if not any(article["id"] == article_id for article in EDUCATION_ARTICLES):
        raise HTTPException(status_code=404, detail="Article not found")
        
    existing = db.query(EducationProgress).filter(
        EducationProgress.article_id == article_id, 
        EducationProgress.user_id == current_user["id"]
    ).first()
    
    if existing:
        existing.completed = body.completed
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing
        
    row = EducationProgress(
        id=uuid.uuid4(),
        article_id=article_id,
        user_id=current_user["id"],
        completed=body.completed,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.get("/education/articles/{article_id}")
def get_article(article_id: str, current_user: dict = Depends(get_current_user)):
    require_care_team(current_user)
    article = next((a for a in EDUCATION_ARTICLES if a["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"article": article, "disclaimer": DISCLAIMER}
