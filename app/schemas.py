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
