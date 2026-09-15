"""R14 data-driven regional theme configuration."""
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user

router = APIRouter(tags=["regional themes"])
REGIONAL_THEMES = [
    {"id":"assam_village","state_region":"Assam","label":"Assam village","description":"Warm tea-garden colours with clear, calm contrast.","colors":{"primary":"#176b5b","primary_dark":"#0f4d41","bg":"#f4fbf7","surface":"#ffffff","text":"#17332c"}},
    {"id":"meghalaya_highlands","state_region":"Meghalaya","label":"Meghalaya highlands","description":"Cool highland greens with a soft, restful background.","colors":{"primary":"#285943","primary_dark":"#1d3f30","bg":"#f3f9f5","surface":"#ffffff","text":"#172b20"}},
    {"id":"manipur_festival","state_region":"Manipur","label":"Manipur festival","description":"Welcoming berry and gold accents while preserving readability.","colors":{"primary":"#8b3a62","primary_dark":"#642944","bg":"#fff7fb","surface":"#ffffff","text":"#321923"}},
]

@router.get("/regional-themes")
def list_regional_themes(current_user: dict = Depends(get_current_user)):
    return {"themes": REGIONAL_THEMES, "default_theme": "assam_village"}

@router.get("/regional-themes/{theme_id}")
def get_regional_theme(theme_id: str, current_user: dict = Depends(get_current_user)):
    theme = next((item for item in REGIONAL_THEMES if item["id"] == theme_id), None)
    if not theme:
        raise HTTPException(status_code=404, detail="Regional theme not found")
    return theme
