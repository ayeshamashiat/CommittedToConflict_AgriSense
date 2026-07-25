"""POST /transcribe - Tier 2 voice input via OpenAI Whisper.

Accepts a multipart audio upload (a farmer's recorded voice note) and returns
the transcribed text. Runs server-side (unlike the browser's Web Speech API)
so voice input works consistently across browsers, not just Chrome/Edge.
"""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.llm.client import LLMClient

router = APIRouter(tags=["transcribe"])
_llm = LLMClient()

_MAX_AUDIO_BYTES = 15 * 1024 * 1024  # 15MB


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str | None = Form(default=None),
) -> dict:
    raw = await audio.read()
    if not raw:
        raise HTTPException(status_code=422, detail="Empty audio file.")
    if len(raw) > _MAX_AUDIO_BYTES:
        raise HTTPException(status_code=422, detail="Audio too large (max 15MB).")

    if not _llm.available:
        raise HTTPException(
            status_code=503,
            detail="Voice transcription requires an OpenAI API key, which is not configured on this server.",
        )

    text = _llm.transcribe_audio(raw, filename=audio.filename or "audio.webm", language=language)
    if text is None:
        raise HTTPException(status_code=502, detail="Transcription failed — please try again.")

    return {"text": text}
