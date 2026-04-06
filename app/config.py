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
