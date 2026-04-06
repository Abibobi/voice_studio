from __future__ import annotations
import io
import os
import uuid
import soundfile as sf
import numpy as np
from typing import Tuple


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_wav(audio: np.ndarray, sr: int, out_dir: str, prefix: str = "gen") -> str:
    ensure_dir(out_dir)
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}.wav"
    full_path = os.path.join(out_dir, filename)
    sf.write(full_path, audio, sr)
    return full_path


def bytes_to_audio(file_bytes: bytes) -> Tuple[np.ndarray, int]:
    with io.BytesIO(file_bytes) as bio:
        audio, sr = sf.read(bio, dtype="float32", always_2d=False)
    return audio, sr
