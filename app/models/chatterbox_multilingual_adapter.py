from __future__ import annotations
from typing import Optional
import os
import tempfile
import numpy as np
import torch
import torchaudio as ta

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

    def _save_reference_wav(self, speaker_audio: np.ndarray, speaker_sr: int) -> str:
        """Write reference audio to a temp .wav file and return the path."""
        tmp_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

        arr = np.asarray(speaker_audio, dtype=np.float32)
        if arr.ndim == 0:
            raise RuntimeError("Reference audio is empty/scalar.")
        elif arr.ndim == 1:
            arr = arr[None, :]
        elif arr.ndim == 2:
            if arr.shape[1] in (1, 2) and arr.shape[0] > arr.shape[1]:
                arr = arr.T
        else:
            raise RuntimeError(f"Unsupported reference audio shape: {arr.shape}")

        if arr.shape[0] < 1 or arr.shape[1] < 1:
            raise RuntimeError(f"Invalid reference audio shape: {arr.shape}")

        wav = torch.clamp(torch.from_numpy(arr).contiguous().cpu(), -1.0, 1.0)
        ta.save(tmp_path, wav, int(speaker_sr), encoding="PCM_F", bits_per_sample=32)
        return tmp_path

    def synthesize(
        self,
        text: str,
        language: Optional[str] = None,
        emotion: Optional[str] = None,
        speaker_audio: Optional[np.ndarray] = None,
        speaker_sr: Optional[int] = None,
    ) -> tuple[np.ndarray, int]:
        if not self.loaded or self.engine is None:
            raise RuntimeError("Multilingual model is not loaded.")

        lang = (language or "en").lower()

        # With reference audio → voice cloning
        if speaker_audio is not None and speaker_sr is not None:
            tmp_path = None
            try:
                tmp_path = self._save_reference_wav(speaker_audio, speaker_sr)
                result = self.engine.generate(text, lang, audio_prompt_path=tmp_path)
                return self._normalize(result)
            except Exception as e:
                raise RuntimeError(f"Multilingual voice-clone inference failed: {e}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

        # Without reference audio → default voice
        try:
            result = self.engine.generate(text, lang)
            return self._normalize(result)
        except Exception as e:
            raise RuntimeError(f"Multilingual inference failed: {e}")