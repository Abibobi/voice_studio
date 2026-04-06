from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict


ModelName = Literal["chatterbox_multilingual", "chatterbox_turbo"]


class SwitchModelRequest(BaseModel):
    model: ModelName


class SynthesizeResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    ok: bool = True
    engine_used: ModelName
    route_reason: str
    language: str
    emotion: Optional[str] = None
    sample_rate: int
    output_wav_path: str


class HealthResponse(BaseModel):
    ok: bool
    active_model: Optional[ModelName] = None
    gpu: dict