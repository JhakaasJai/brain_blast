"""
Voice proxy endpoints.
# MOCK: Both endpoints currently return simulated responses.
# In production, these would proxy to Bhashini ASR/TTS APIs,
# keeping API keys server-side and never exposing them to the client.
#
# To swap in real Bhashini:
#   1. Set BHASHINI_API_KEY and BHASHINI_USER_ID in .env
#   2. Replace the stub bodies below with real HTTP calls using httpx
#   3. Remove the # MOCK: comments
"""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.api.schemas import STTRequest, STTResponse, TTSRequest, TTSResponse

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/stt", response_model=STTResponse)
def speech_to_text(body: STTRequest, current_user: dict = Depends(get_current_user)):
    # MOCK: Real implementation would call Bhashini ULCA ASR pipeline here.
    # For the prototype, return a generic transcript to exercise the endpoint shape.
    return STTResponse(
        transcript="[MOCK transcript — Web Speech API handles STT on the client]",
        language=body.language,
        source="web_speech_fallback",
    )


@router.post("/tts", response_model=TTSResponse)
def text_to_speech(body: TTSRequest, current_user: dict = Depends(get_current_user)):
    # MOCK: Real implementation would call Bhashini ULCA TTS pipeline here.
    # Client uses Web Speech API SpeechSynthesis as the actual fallback.
    return TTSResponse(
        audio_url="",   # MOCK: empty — client falls back to Web Speech API
        language=body.language,
        source="web_speech_fallback",
    )
