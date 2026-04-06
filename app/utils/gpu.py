from __future__ import annotations
import gc
import torch


def cuda_available() -> bool:
    return torch.cuda.is_available()


def clear_vram() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def vram_stats() -> dict:
    if not torch.cuda.is_available():
        return {"cuda": False}
    device = torch.cuda.current_device()
    total = torch.cuda.get_device_properties(device).total_memory
    allocated = torch.cuda.memory_allocated(device)
    reserved = torch.cuda.memory_reserved(device)
    free_est = total - reserved
    gb = 1024**3
    return {
        "cuda": True,
        "device_index": device,
        "device_name": torch.cuda.get_device_name(device),
        "total_gb": round(total / gb, 2),
        "allocated_gb": round(allocated / gb, 2),
        "reserved_gb": round(reserved / gb, 2),
        "estimated_free_gb": round(free_est / gb, 2),
    }
