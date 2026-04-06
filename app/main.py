from __future__ import annotations
import traceback
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.config import CONFIG
from app.schemas import SwitchModelRequest, SynthesizeResponse, HealthResponse
from app.router.model_router import ModelRouter
from app.utils.audio import save_wav, bytes_to_audio, ensure_dir
from app.utils.gpu import vram_stats

app = FastAPI(title="Voice Studio API", version="1.0.0")
router = ModelRouter()
ensure_dir(CONFIG.output_dir)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(ok=True, active_model=router.active, gpu=vram_stats())


@app.post("/switch-model")
def switch_model(payload: SwitchModelRequest):
    try:
        result = router.switch(payload.model)
        return {"ok": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(
    text: str = Form(..., min_length=1),
    language: str = Form(..., min_length=2, max_length=8),
    emotion: Optional[str] = Form(default=None),
    force_model: Optional[str] = Form(default=None),
    speaker_wav: Optional[UploadFile] = File(default=None),
):
    try:
        speaker_audio = None
        speaker_sr = None
        if speaker_wav is not None:
            wav_bytes = await speaker_wav.read()
            speaker_audio, speaker_sr = bytes_to_audio(wav_bytes)

        force_model_norm = None
        if force_model:
            if force_model not in {"svara", "chatterbox"}:
                raise HTTPException(status_code=400, detail="force_model must be 'svara' or 'chatterbox'")
            force_model_norm = force_model

        audio, sr, decision = router.synthesize(
            text=text,
            language=language.lower(),
            emotion=emotion,
            speaker_audio=speaker_audio,
            speaker_sr=speaker_sr,
            force_model=force_model_norm,
        )

        out_path = save_wav(audio=audio, sr=sr, out_dir=CONFIG.output_dir, prefix=decision.model)
        return SynthesizeResponse(
            model_used=decision.model,
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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"ok": False, "error": str(exc)})
