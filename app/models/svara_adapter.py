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
