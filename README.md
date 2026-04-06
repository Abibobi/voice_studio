# Voice Studio (Svara + Chatterbox Multilingual)

A VRAM-aware FastAPI app for voice generation/voice-clone style synthesis with:

- Svara TTS (`kenpath/svara-tts-v1`) for Indian languages/accent-oriented generation.
- Resemble AI Chatterbox multilingual (`resemble-ai/chatterbox`) for emotion and global languages.

## Setup
```bash
conda env create -f environment.yml
conda activate voice_studio
