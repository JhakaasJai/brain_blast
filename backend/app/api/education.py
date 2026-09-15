"""R11 caregiver education library.
Prototype content is in-memory and educational, not medical advice.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user
from app.api.schemas import (
    EducationArticleListResponse,
    EducationArticleProgressIn,
    EducationArticleProgressOut,
)
from app.mock_data import EDUCATION_ARTICLES, EDUCATION_PROGRESS

router = APIRouter(tags=["education"])
DISCLAIMER = "Educational information only; discuss individual care decisions with a qualified clinician."


def require_care_team(user: dict) -> None:
    if user["role"] not in ("caregiver", "health_worker", "admin"):
        raise HTTPException(status_code=403, detail="Care team access required")


@router.get("/education/articles", response_model=EducationArticleListResponse)
def list_articles(current_user: dict = Depends(get_current_user)):
    require_care_team(current_user)
    progress = {
        row["article_id"]: row["completed"]
        for row in EDUCATION_PROGRESS
        if row["user_id"] == current_user["id"]
    }
    return {"articles": EDUCATION_ARTICLES, "progress": progress, "disclaimer": DISCLAIMER}


@router.patch("/education/articles/{article_id}/progress", response_model=EducationArticleProgressOut)
def update_progress(
    article_id: str,
    body: EducationArticleProgressIn,
    current_user: dict = Depends(get_current_user),
):
    require_care_team(current_user)
    if not any(article["id"] == article_id for article in EDUCATION_ARTICLES):
        raise HTTPException(status_code=404, detail="Article not found")
    now = datetime.now(timezone.utc).isoformat()
    existing = next(
        (row for row in EDUCATION_PROGRESS
         if row["article_id"] == article_id and row["user_id"] == current_user["id"]),
        None,
    )
    if existing:
        existing.update(completed=body.completed, updated_at=now)
        return existing
    row = {
        "article_id": article_id,
        "user_id": current_user["id"],
        "completed": body.completed,
        "updated_at": now,
    }
    EDUCATION_PROGRESS.append(row)
    return row


@router.get("/education/articles/{article_id}")
def get_article(article_id: str, current_user: dict = Depends(get_current_user)):
    require_care_team(current_user)
    article = next((a for a in EDUCATION_ARTICLES if a["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"article": article, "disclaimer": DISCLAIMER}
