from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional
import threading

from app.config import CONFIG
from app.utils.gpu import clear_vram, vram_stats
from app.models.chatterbox_multilingual_adapter import ChatterboxMultilingualAdapter
from app.models.chatterbox_turbo_adapter import ChatterboxTurboAdapter

ModelName = Literal["chatterbox_multilingual", "chatterbox_turbo"]


@dataclass
class RouteDecision:
    model: ModelName
    reason: str


class ModelRouter:
    def __init__(self):
        self._lock = threading.RLock()
        self.active: Optional[ModelName] = None
        self.multilingual = ChatterboxMultilingualAdapter(device=CONFIG.device)
        self.turbo = ChatterboxTurboAdapter(device=CONFIG.device)

    def decide_model(self, language: str, prefer_similarity: bool = False) -> RouteDecision:
        lang = language.lower()
        if lang != "en":
            return RouteDecision(
                model="chatterbox_multilingual",
                reason="Non-English language routed to multilingual model.",
            )
        if prefer_similarity:
            return RouteDecision(
                model="chatterbox_turbo",
                reason="English + similarity preference routed to turbo.",
            )
        return RouteDecision(
            model="chatterbox_turbo",
            reason="Default English route to turbo.",
        )

    def _unload_active(self):
        if self.active == "chatterbox_multilingual":
            self.multilingual.unload()
        elif self.active == "chatterbox_turbo":
            self.turbo.unload()

    def switch(self, target: ModelName) -> dict:
        with self._lock:
            if self.active == target:
                return {"active_model": self.active, "changed": False, "vram": vram_stats()}

            self._unload_active()
            clear_vram()

            if target == "chatterbox_multilingual":
                self.multilingual.load()
            else:
                self.turbo.load()

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
        prefer_similarity: bool = False,
    ):
        with self._lock:
            decision = (
                RouteDecision(model=force_model, reason=f"Forced model: {force_model}")
                if force_model
                else self.decide_model(language=language, prefer_similarity=prefer_similarity)
            )

            self.switch(decision.model)

            if decision.model == "chatterbox_multilingual":
                audio, sr = self.multilingual.synthesize(
                    text=text,
                    language=language,
                    emotion=emotion,
                    speaker_audio=speaker_audio,
                    speaker_sr=speaker_sr,
                )
            else:
                audio, sr = self.turbo.synthesize(
                    text=text,
                    language=language,
                    emotion=emotion,
                    speaker_audio=speaker_audio,
                    speaker_sr=speaker_sr,
                )

            return audio, sr, decision