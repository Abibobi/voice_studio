from __future__ import annotations
from typing import Optional
import numpy as np
import torch

from app.models.base import TTSModelBase
from app.utils.gpu import clear_vram


class ChatterboxMultilingualAdapter(TTSModelBase):
    name = "chatterbox_multilingual"

    def __init__(self, device: str = "cuda"):
        super().__init__(device=device)
        self.engine = None
        self.sr = 24000

    def _runtime_device(self) -> str:
        return "cuda" if torch.cuda.is_available() and self.device == "cuda" else "cpu"

    def load(self) -> None:
        if self.loaded:
            return
        try:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # type: ignore
            dev = self._runtime_device()
            # your installed package supports from_pretrained(device)
            self.engine = ChatterboxMultilingualTTS.from_pretrained(dev)
            self.sr = int(getattr(self.engine, "sr", 24000))
            self.loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load multilingual model: {e}")

    def unload(self) -> None:
        self.engine = None
        self.loaded = False
        clear_vram()

    def _normalize(self, result) -> tuple[np.ndarray, int]:
        if isinstance(result, tuple) and len(result) == 2:
            audio, sr = result
            return np.asarray(audio, dtype=np.float32).squeeze(), int(sr)

        if isinstance(result, np.ndarray):
            return result.astype(np.float32).squeeze(), self.sr

        if isinstance(result, torch.Tensor):
            return result.detach().float().cpu().numpy().squeeze(), self.sr

        if isinstance(result, dict):
            if "audio" in result:
                return np.asarray(result["audio"], dtype=np.float32).squeeze(), int(result.get("sample_rate", self.sr))
            if "wav" in result:
                return np.asarray(result["wav"], dtype=np.float32).squeeze(), int(result.get("sr", self.sr))

        raise RuntimeError(f"Unsupported multilingual output format: {type(result)}")

    def synthesize(
        self,
        text: str,
        language: Optional[str] = None,
        emotion: Optional[str] = None,       # intentionally unused (defaults-only)
        speaker_audio: Optional[np.ndarray] = None,  # intentionally unused in minimal version
        speaker_sr: Optional[int] = None,            # intentionally unused in minimal version
    ) -> tuple[np.ndarray, int]:
        if not self.loaded or self.engine is None:
            raise RuntimeError("Multilingual model is not loaded.")

        lang = (language or "en").lower()

        # minimal/default official-style call
        try:
            result = self.engine.generate(text, lang)
            return self._normalize(result)
        except Exception as e:
            raise RuntimeError(f"Multilingual inference failed: {e}")