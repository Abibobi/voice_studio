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
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import os, shutil, uuid

from app.db import Base, engine, SessionLocal
from app.models.user_models import User, VoiceProfile
from app.auth import hash_password, verify_password, create_access_token, decode_access_token
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

# ── Database setup ──
Base.metadata.create_all(bind=engine)
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = decode_access_token(cred.credentials)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == sub).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


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
    voice_profile_id: Optional[int] = Form(default=None),
    db: Session = Depends(get_db),
):
    try:
        # Always define defaults
        speaker_audio = None
        speaker_sr = None

        # Load audio from saved voice profile if profile ID is given
        if voice_profile_id is not None:
            vp = db.query(VoiceProfile).filter(VoiceProfile.id == voice_profile_id).first()
            if not vp:
                raise HTTPException(status_code=404, detail="Voice profile not found")
            if not os.path.exists(vp.sample_wav_path):
                raise HTTPException(status_code=404, detail="Voice profile audio file missing")
            with open(vp.sample_wav_path, "rb") as f:
                wav_bytes = f.read()
            speaker_audio, speaker_sr = bytes_to_audio(wav_bytes)
        elif speaker_wav is not None:
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



class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=req.email, password_hash=hash_password(req.password))
    db.add(user)
    db.commit()
    return {"ok": True}

@app.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}

@app.post("/voice-profiles")
async def create_voice_profile(
    name: str = Form(...),
    language: str = Form(default="en"),
    sample_wav: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    os.makedirs("voice_profiles", exist_ok=True)
    ext = os.path.splitext(sample_wav.filename or "sample.wav")[1] or ".wav"
    fname = f"{uuid.uuid4().hex}{ext}"
    out_path = os.path.join("voice_profiles", fname)

    with open(out_path, "wb") as f:
        shutil.copyfileobj(sample_wav.file, f)

    vp = VoiceProfile(
        user_id=user.id,
        name=name,
        language=language,
        sample_wav_path=out_path,
    )
    db.add(vp)
    db.commit()
    db.refresh(vp)

    return {
        "id": vp.id,
        "name": vp.name,
        "language": vp.language,
        "sample_wav_path": vp.sample_wav_path,
        "created_at": str(vp.created_at),
    }

@app.get("/voice-profiles")
def list_voice_profiles(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.query(VoiceProfile).filter(VoiceProfile.user_id == user.id).order_by(VoiceProfile.id.desc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "language": r.language,
            "sample_wav_path": r.sample_wav_path,
            "created_at": str(r.created_at),
        }
        for r in rows
    ]

@app.delete("/voice-profiles/{profile_id}")
def delete_voice_profile(
    profile_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vp = db.query(VoiceProfile).filter(VoiceProfile.id == profile_id, VoiceProfile.user_id == user.id).first()
    if not vp:
        raise HTTPException(status_code=404, detail="Not found")
    if os.path.exists(vp.sample_wav_path):
        os.remove(vp.sample_wav_path)
    db.delete(vp)
    db.commit()
    return {"ok": True}