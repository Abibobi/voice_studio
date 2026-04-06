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
