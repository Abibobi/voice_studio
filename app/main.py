from __future__ import annotations

import traceback
from typing import Optional, Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.config import CONFIG
from app.router.model_router import ModelRouter
from app.schemas import (
    HealthResponse,
    SwitchModelRequest,
    SynthesizeResponse,
)
from app.utils.audio import bytes_to_audio, save_wav
from app.utils.gpu import vram_stats

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Voice Studio API", version="0.1.0")

# Allow the React dev server to hit the API + fetch audio files
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ensure folder exists
os.makedirs(CONFIG.output_dir, exist_ok=True)

# expose generated files at /outputs/*
app.mount("/outputs", StaticFiles(directory=CONFIG.output_dir), name="outputs")

router = ModelRouter()

ModelName = Literal["chatterbox_multilingual", "chatterbox_turbo"]


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        ok=True,
        active_model=router.active,
        gpu=vram_stats(),
    )


@app.post("/switch-model")
def switch_model(req: SwitchModelRequest):
    try:
        result = router.switch(req.model)
        return {"ok": True, **result}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(
    text: str = Form(..., min_length=1),
    language: str = Form(..., min_length=2, max_length=8),
    emotion: Optional[str] = Form(default=None),
    force_model: Optional[str] = Form(default=None),  # chatterbox_multilingual | chatterbox_turbo
    prefer_similarity: bool = Form(default=False),
    speaker_wav: Optional[UploadFile] = File(default=None),
):
    try:
        # Always define defaults
        speaker_audio = None
        speaker_sr = None

        if speaker_wav is not None:
            wav_bytes = await speaker_wav.read()
            speaker_audio, speaker_sr = bytes_to_audio(wav_bytes)

        valid_models = {"chatterbox_multilingual", "chatterbox_turbo"}
        if force_model and force_model not in valid_models:
            raise HTTPException(
                status_code=400,
                detail="force_model must be 'chatterbox_multilingual' or 'chatterbox_turbo'",
            )

        audio, sr, decision = router.synthesize(
            text=text,
            language=language.lower(),
            emotion=emotion,
            speaker_audio=speaker_audio,
            speaker_sr=speaker_sr,
            force_model=force_model,  # type: ignore[arg-type]
            prefer_similarity=prefer_similarity,
        )

        out_path = save_wav(
            audio=audio,
            sr=sr,
            out_dir=CONFIG.output_dir,
            prefix=decision.model,
        )

        return SynthesizeResponse(
            ok=True,
            engine_used=decision.model,
            route_reason=decision.reason,
            language=language.lower(),
            emotion=emotion,
            sample_rate=sr,
            output_wav_path=out_path,
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel
from app.services.gemini_translate import translate_preserve_style

class TranslateRequest(BaseModel):
    text: str
    target_language: str

class TranslateResponse(BaseModel):
    translated_text: str

@app.post("/translate", response_model=TranslateResponse)
async def translate(req: TranslateRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    if not req.target_language.strip():
        raise HTTPException(status_code=400, detail="target_language is required")
    try:
        translated = translate_preserve_style(req.text, req.target_language)
        return TranslateResponse(translated_text=translated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}")