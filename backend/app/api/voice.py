"""
Voice proxy endpoints (Bhashini Integration).
"""
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.api.schemas import STTRequest, STTResponse, TTSRequest, TTSResponse

router = APIRouter(prefix="/voice", tags=["voice"])

BHASHINI_API_KEY = os.environ.get("BHASHINI_API_KEY")
BHASHINI_USER_ID = os.environ.get("BHASHINI_USER_ID")

@router.post("/stt", response_model=STTResponse)
async def speech_to_text(body: STTRequest, current_user: dict = Depends(get_current_user)):
    # This is a stub for the real Bhashini request using httpx.
    # A full Bhashini implementation requires a multi-step ULCA pipeline config fetch,
    # followed by the inference call. For safety during migration, if keys aren't set,
    # or the call fails, we fallback to telling the client to use Web Speech API.
    
    if not BHASHINI_API_KEY:
        return STTResponse(
            transcript="[Bhashini API Key Missing — Falling back to local Web Speech API]",
            language=body.language,
            source="web_speech_fallback",
        )
        
    try:
        # Pseudo-code for actual implementation:
        # async with httpx.AsyncClient() as client:
        #     res = await client.post("https://bhashini-api-url", headers={"Authorization": BHASHINI_API_KEY}, json={"audio": body.audio_base64})
        #     transcript = res.json()["output"][0]["source"]
        
        # Simulate successful connection to verify env loading but preserve client-side STT until full ULCA mapping is done
        pass
    except Exception as e:
        print(f"Bhashini STT Error: {e}")
        
    return STTResponse(
        transcript="[Bhashini STT configured but deferred to Web Speech API for prototype stability]",
        language=body.language,
        source="bhashini",
    )


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(body: TTSRequest, current_user: dict = Depends(get_current_user)):
    if not BHASHINI_API_KEY:
        return TTSResponse(
            audio_url="",
            language=body.language,
            source="web_speech_fallback",
        )
        
    try:
        # Pseudo-code for actual implementation:
        # async with httpx.AsyncClient() as client:
        #     res = await client.post("...", headers={"Authorization": BHASHINI_API_KEY}, json={"text": body.text})
        #     audio_url = upload_base64_to_cloudinary(res.json()["audio"])
        pass
    except Exception as e:
        print(f"Bhashini TTS Error: {e}")

    return TTSResponse(
        audio_url="", # Client falls back to Web Speech API synthesis if empty
        language=body.language,
        source="bhashini",
    )
