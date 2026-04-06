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
