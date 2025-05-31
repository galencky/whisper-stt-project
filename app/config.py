"""
Central configuration shared by all modules.
Override any path with environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────
# Project root & .env
# ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)

# ──────────────────────────────────────────────────────────
# Base data directory (bind-mount this on Synology)
# ──────────────────────────────────────────────────────────
BASE_DIR        = Path(os.getenv("BASE_DIR"       , "/data"))
INBOX_DIR       = Path(os.getenv("INBOX_DIR"      , BASE_DIR / "inbox"))
PROCESSED_DIR   = Path(os.getenv("PROCESSED_DIR"  , BASE_DIR / "processed"))
TRANSCRIPTS_DIR = Path(os.getenv("TRANSCRIPTS_DIR", BASE_DIR / "transcripts"))
PARSED_DIR      = Path(os.getenv("PARSED_DIR"     , BASE_DIR / "parsed"))
MARKDOWN_DIR    = Path(os.getenv("MARKDOWN_DIR"   , BASE_DIR / "markdown"))
MODEL_CACHE_DIR = Path(os.getenv("MODEL_CACHE_DIR", BASE_DIR / "models"))
OUTPUT_DIR      = Path(os.getenv("OUTPUT_DIR"     , BASE_DIR / "output"))
LOG_DIR         = Path(BASE_DIR / "logs")

PROMPT_PATH     = Path(os.getenv("PROMPT_PATH",
                                  PROJECT_ROOT / "prompts" /
                                  "speech_summary_prompt.txt"))

# ──────────────────────────────────────────────────────────
# Keys & misc
# ──────────────────────────────────────────────────────────
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY")
EMAIL_USER          = os.getenv("EMAIL_USER")
EMAIL_PASS          = os.getenv("EMAIL_PASS")
EMAIL_TO            = os.getenv("EMAIL_TO")
PREFERRED_LANGUAGE  = os.getenv("PREFERRED_LANGUAGE", "zh")  # "" => autodetect
AUDIO_EXT = {
    ".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm",
    ".mp4", ".aac", ".wma", ".alac", ".aiff", ".opus", ".mkv", ".mov"
}

# Ensure every folder exists
for d in (INBOX_DIR, PROCESSED_DIR, TRANSCRIPTS_DIR, PARSED_DIR,
          MARKDOWN_DIR, MODEL_CACHE_DIR, OUTPUT_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)
