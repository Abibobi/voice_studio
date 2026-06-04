# Voice Studio (Svara + Chatterbox)

A VRAM-aware FastAPI app for voice generation and voice-clone style synthesis with:

- Svara TTS (`kenpath/svara-tts-v1`) for Indian languages and accent-oriented generation.
- Resemble AI Chatterbox (multilingual + turbo) for emotion and global languages.

## Requirements

- Conda (recommended) or a Python 3.10 environment
- Node.js + npm (for the React frontend)

## Backend setup (FastAPI)

Create the environment and install Python deps:

```bash
conda env create -f environment.yml
conda activate voice_studio

# Required by API auth + translation modules
pip install sqlalchemy python-jose[cryptography] passlib[bcrypt] python-dotenv google-genai email-validator
```

Set your Gemini key (required because the translation module loads at startup):

Create a `.env` file in the repo root:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
```

Run the API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Notes:

- The SQLite DB file `voice_studio.db` is created on first run.
- Generated audio is served from `/outputs` and stored in `outputs/`.
- If you do not have a CUDA GPU, set `device="cpu"` in `app/config.py`.
- Model weights download on first synthesis call and may take a while.

## Frontend setup (React + Vite)

```bash
cd voice-studio-web
npm install
npm run dev
```

The frontend expects the API at `http://127.0.0.1:8000` (see `voice-studio-web/src/api.ts`).

## Optional: Gradio test UI

```bash
pip install gradio requests
python frontend_app.py
```

This runs on `http://127.0.0.1:7860` and uses the same API.
