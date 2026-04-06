from __future__ import annotations
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

LANGUAGE_NAMES = {
    "ar": "Arabic",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hi": "Hindi",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ms": "Malay",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ru": "Russian",
    "sv": "Swedish",
    "sw": "Swahili",
    "tr": "Turkish",
    "zh": "Chinese",
}


def translate_preserve_style(text: str, target_language: str) -> str:
    code = target_language.strip().lower()
    language_name = LANGUAGE_NAMES.get(code, code)

    prompt = f"""
You are an expert localization translator for voice scripts.

Translate the script into {language_name} ({code}).

Requirements:
- Preserve original meaning, tone, emotional feel, and speaking style.
- Keep it natural for spoken TTS.
- Do NOT summarize or explain.
- Keep punctuation and emphasis naturally.
- Return ONLY the translated script text.

Script:
{text}
""".strip()

    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    out = (resp.text or "").strip()
    if not out:
        raise RuntimeError("Gemini returned empty translation.")
    return out