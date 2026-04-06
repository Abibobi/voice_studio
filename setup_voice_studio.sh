#!/usr/bin/env bash
set -euo pipefail

BRANCH="feat/voice-router-svara-chatterbox"

echo "==> Checking git repo..."
git rev-parse --is-inside-work-tree >/dev/null

echo "==> Creating/switching branch: ${BRANCH}"
git checkout -b "${BRANCH}" 2>/dev/null || git checkout "${BRANCH}"

echo "==> Creating folders..."
mkdir -p app/models app/router app/utils outputs

echo "==> Writing environment.yml"
cat > environment.yml <<'YAML'
name: voice_studio
channels:
  - nvidia
  - pytorch
  - conda-forge
dependencies:
  - python=3.10
  - ffmpeg
  - cudatoolkit=11.8
  - pip
  - pip:
      - fastapi==0.115.0
      - uvicorn[standard]==0.30.6
      - pydantic==2.9.2
      - python-multipart==0.0.9
      - numpy==1.26.4
      - soundfile==0.12.1
      - librosa==0.10.2.post1
      - scipy==1.14.1
      - huggingface_hub==0.24.7
      - transformers==4.44.2
      - accelerate==0.34.2
      - safetensors==0.4.5
      - torch==2.4.1
      - torchaudio==2.4.1
      - psutil==6.0.0
      - pyyaml==6.0.2
      - httpx==0.27.2
YAML

echo "==> Writing app/__init__.py"
cat > app/__init__.py <<'PY'
# package marker
PY

echo "==> Writing app/config.py"
cat > app/config.py <<'PY'
from pydantic import BaseModel
from typing import Literal


class AppConfig(BaseModel):
    device: Literal["cuda", "cpu"] = "cuda"
    max_vram_gb: float = 7.2  # keep headroom on 8GB cards
    default_sample_rate: int = 24000
    output_dir: str = "outputs"
    svara_model_id: str = "kenpath/svara-tts-v1"
    chatterbox_repo: str = "resemble-ai/chatterbox"
    chatterbox_model_name: str = "chatterbox-multilingual"
    allow_cpu_fallback: bool = True


CONFIG = AppConfig()
PY

echo "==> Writing app/utils/audio.py"
cat > app/utils/audio.py <<'PY'
from __future__ import annotations
import io
import os
import uuid
import soundfile as sf
import numpy as np
from typing import Tuple


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_wav(audio: np.ndarray, sr: int, out_dir: str, prefix: str = "gen") -> str:
    ensure_dir(out_dir)
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}.wav"
    full_path = os.path.join(out_dir, filename)
    sf.write(full_path, audio, sr)
    return full_path


def bytes_to_audio(file_bytes: bytes) -> Tuple[np.ndarray, int]:
    with io.BytesIO(file_bytes) as bio:
        audio, sr = sf.read(bio, dtype="float32", always_2d=False)
    return audio, sr
PY

echo "==> Writing app/utils/gpu.py"
cat > app/utils/gpu.py <<'PY'
from __future__ import annotations
import gc
import torch


def cuda_available() -> bool:
    return torch.cuda.is_available()


def clear_vram() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def vram_stats() -> dict:
    if not torch.cuda.is_available():
        return {"cuda": False}
    device = torch.cuda.current_device()
    total = torch.cuda.get_device_properties(device).total_memory
    allocated = torch.cuda.memory_allocated(device)
    reserved = torch.cuda.memory_reserved(device)
    free_est = total - reserved
    gb = 1024**3
    return {
        "cuda": True,
        "device_index": device,
        "device_name": torch.cuda.get_device_name(device),
        "total_gb": round(total / gb, 2),
        "allocated_gb": round(allocated / gb, 2),
        "reserved_gb": round(reserved / gb, 2),
        "estimated_free_gb": round(free_est / gb, 2),
    }
PY

echo "==> Writing app/models/base.py"
cat > app/models/base.py <<'PY'
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class TTSModelBase(ABC):
    name: str = "base"

    def __init__(self, device: str = "cuda"):
        self.device = device
        self.loaded = False

    @abstractmethod
    def load(self) -> None:
        ...

    @abstractmethod
    def unload(self) -> None:
        ...

    @abstractmethod
    def synthesize(
        self,
        text: str,
        language: Optional[str] = None,
        emotion: Optional[str] = None,
        speaker_audio: Optional[np.ndarray] = None,
        speaker_sr: Optional[int] = None,
    ) -> tuple[np.ndarray, int]:
        ...
PY

echo "==> Writing app/models/chatterbox_adapter.py"
cat > app/models/chatterbox_adapter.py <<'PY'
from __future__ import annotations
from typing import Optional
import numpy as np
from .base import TTSModelBase
from app.utils.gpu import clear_vram


class ChatterboxAdapter(TTSModelBase):
    name = "chatterbox"

    def __init__(self, device: str = "cuda", repo: str = "resemble-ai/chatterbox"):
        super().__init__(device=device)
        self.repo = repo
        self.engine = None

    def load(self) -> None:
        if self.loaded:
            return

        try:
            from chatterbox.api import ChatterboxMultilingual  # type: ignore
            self.engine = ChatterboxMultilingual(device=self.device)
            self.loaded = True
            return
        except Exception:
            pass

        try:
            import chatterbox  # type: ignore
            if hasattr(chatterbox, "load_model"):
                self.engine = chatterbox.load_model("multilingual", device=self.device)
                self.loaded = True
                return
        except Exception:
            pass

        raise RuntimeError(
            "Could not load Chatterbox multilingual. "
            "Install/update from https://github.com/resemble-ai/chatterbox and verify API compatibility."
        )

    def unload(self) -> None:
        self.engine = None
        self.loaded = False
        clear_vram()

    def synthesize(
        self,
        text: str,
        language: Optional[str] = None,
        emotion: Optional[str] = None,
        speaker_audio: Optional[np.ndarray] = None,
        speaker_sr: Optional[int] = None,
    ) -> tuple[np.ndarray, int]:
        if not self.loaded or self.engine is None:
            raise RuntimeError("Chatterbox model is not loaded.")

        try:
            result = self.engine.synthesize(
                text=text,
                language=language,
                emotion=emotion,
                speaker_wav=speaker_audio,
                speaker_sr=speaker_sr,
            )
        except Exception:
            try:
                result = self.engine.generate(
                    text=text,
                    lang=language,
                    style=emotion,
                    prompt_wav=speaker_audio,
                    prompt_sr=speaker_sr,
                )
            except Exception as e:
                raise RuntimeError(f"Chatterbox inference failed: {e}") from e

        if isinstance(result, tuple) and len(result) == 2:
            audio, sr = result
            return np.asarray(audio, dtype=np.float32), int(sr)

        if isinstance(result, dict) and "audio" in result:
            sr = int(result.get("sample_rate", 24000))
            return np.asarray(result["audio"], dtype=np.float32), sr

        raise RuntimeError("Unsupported Chatterbox output format.")
PY

echo "==> Writing app/models/svara_adapter.py"
cat > app/models/svara_adapter.py <<'PY'
from __future__ import annotations
from typing import Optional
import numpy as np
import torch
from transformers import AutoProcessor, AutoModel

from .base import TTSModelBase
from app.utils.gpu import clear_vram


class SvaraAdapter(TTSModelBase):
    name = "svara"

    def __init__(self, device: str = "cuda", model_id: str = "kenpath/svara-tts-v1"):
        super().__init__(device=device)
        self.model_id = model_id
        self.processor = None
        self.model = None

    def load(self) -> None:
        if self.loaded:
            return

        try:
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            self.model = AutoModel.from_pretrained(
                self.model_id,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            self.model.to(self.device)
            self.model.eval()
            self.loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load Svara model ({self.model_id}): {e}") from e

    def unload(self) -> None:
        self.processor = None
        self.model = None
        self.loaded = False
        clear_vram()

    def synthesize(
        self,
        text: str,
        language: Optional[str] = "hi",
        emotion: Optional[str] = None,
        speaker_audio: Optional[np.ndarray] = None,
        speaker_sr: Optional[int] = None,
    ) -> tuple[np.ndarray, int]:
        if not self.loaded or self.model is None or self.processor is None:
            raise RuntimeError("Svara model is not loaded.")

        try:
            inputs = self.processor(
                text=text,
                language=language,
                return_tensors="pt",
            )
            inputs = {k: v.to(self.device) if hasattr(v, "to") else v for k, v in inputs.items()}

            with torch.inference_mode():
                if hasattr(self.model, "generate"):
                    out = self.model.generate(**inputs)
                elif hasattr(self.model, "synthesize"):
                    out = self.model.synthesize(**inputs)
                else:
                    raise RuntimeError("Svara model has no generate/synthesize method.")

            if isinstance(out, dict) and "audio" in out:
                audio = out["audio"]
                sr = int(out.get("sample_rate", 24000))
            elif isinstance(out, tuple) and len(out) == 2:
                audio, sr = out
                sr = int(sr)
            else:
                audio = out
                sr = 24000

            if isinstance(audio, torch.Tensor):
                audio = audio.detach().float().cpu().numpy()

            audio = np.asarray(audio, dtype=np.float32).squeeze()
            return audio, sr

        except Exception as e:
            raise RuntimeError(f"Svara synthesis failed: {e}") from e
PY

echo "==> Writing app/router/model_router.py"
cat > app/router/model_router.py <<'PY'
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional
import threading

from app.config import CONFIG
from app.models.svara_adapter import SvaraAdapter
from app.models.chatterbox_adapter import ChatterboxAdapter
from app.utils.gpu import clear_vram, vram_stats


ModelName = Literal["svara", "chatterbox"]


@dataclass
class RouteDecision:
    model: ModelName
    reason: str


class ModelRouter:
    def __init__(self):
        self._lock = threading.RLock()
        self.active: Optional[ModelName] = None
        self.svara = SvaraAdapter(device=CONFIG.device, model_id=CONFIG.svara_model_id)
        self.chatterbox = ChatterboxAdapter(device=CONFIG.device, repo=CONFIG.chatterbox_repo)

    def decide_model(self, language: str, emotion: Optional[str]) -> RouteDecision:
        indian_langs = {"hi", "bn", "ta", "te", "ml", "mr", "kn", "gu", "pa", "or", "as", "ur"}
        if language.lower() in indian_langs and not emotion:
            return RouteDecision(model="svara", reason="Indian language without emotion preference.")
        return RouteDecision(model="chatterbox", reason="Global language or emotion requested.")

    def switch(self, target: ModelName) -> dict:
        with self._lock:
            if self.active == target:
                return {"active_model": self.active, "changed": False, "vram": vram_stats()}

            if self.active == "svara":
                self.svara.unload()
            elif self.active == "chatterbox":
                self.chatterbox.unload()

            clear_vram()

            if target == "svara":
                self.svara.load()
            else:
                self.chatterbox.load()

            self.active = target
            return {"active_model": self.active, "changed": True, "vram": vram_stats()}

    def synthesize(
        self,
        text: str,
        language: str,
        emotion: Optional[str],
        speaker_audio=None,
        speaker_sr=None,
        force_model: Optional[ModelName] = None,
    ):
        with self._lock:
            decision = self.decide_model(language, emotion) if force_model is None else RouteDecision(
                model=force_model, reason=f"Forced model: {force_model}"
            )
            self.switch(decision.model)

            if decision.model == "svara":
                audio, sr = self.svara.synthesize(
                    text=text,
                    language=language,
                    emotion=emotion,
                    speaker_audio=speaker_audio,
                    speaker_sr=speaker_sr,
                )
            else:
                audio, sr = self.chatterbox.synthesize(
                    text=text,
                    language=language,
                    emotion=emotion,
                    speaker_audio=speaker_audio,
                    speaker_sr=speaker_sr,
                )

            return audio, sr, decision
PY

echo "==> Writing app/schemas.py"
cat > app/schemas.py <<'PY'
from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel


class SwitchModelRequest(BaseModel):
    model: Literal["svara", "chatterbox"]


class SynthesizeResponse(BaseModel):
    ok: bool = True
    model_used: Literal["svara", "chatterbox"]
    route_reason: str
    language: str
    emotion: Optional[str] = None
    sample_rate: int
    output_wav_path: str


class HealthResponse(BaseModel):
    ok: bool
    active_model: Optional[Literal["svara", "chatterbox"]] = None
    gpu: dict
PY

echo "==> Writing app/main.py"
cat > app/main.py <<'PY'
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
PY

echo "==> Writing README.md"
cat > README.md <<'MD'
# Voice Studio (Svara + Chatterbox Multilingual)

A VRAM-aware FastAPI app for voice generation/voice-clone style synthesis with:

- Svara TTS (`kenpath/svara-tts-v1`) for Indian languages/accent-oriented generation.
- Resemble AI Chatterbox multilingual (`resemble-ai/chatterbox`) for emotion and global languages.

## Setup
```bash
conda env create -f environment.yml
conda activate voice_studio
