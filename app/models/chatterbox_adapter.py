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
