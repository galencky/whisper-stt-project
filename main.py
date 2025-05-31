#!/usr/bin/env python3
"""
Whisper-STT pipeline daemon.

• Watches INBOX_DIR for new/changed audio using watchdog
• Waits STABILISE_SEC until files stop growing
• Processes the *current* ready batch:
    audio ➜ transcript ➜ parsed ➜ Gemini summary ➜ HackMD ➜ e-mail
• Runs forever inside Docker; clean CTRL-C / docker stop

Folder layout (all under BASE_DIR = /app/data by default):
    inbox/ processed/ transcripts/ parsed/ markdown/ uploaded/ models/ logs/
"""

import os, sys, time, signal, logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import whisper
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# ---------- your own helper modules (unchanged) ----------
from parser import batch_parse
from summarizer import summarize_all
from uploader import batch_upload_markdown_and_move
from emailer import send_email
# ---------------------------------------------------------

# ---------------- configuration via env ------------------
LOG_LEVEL      = os.getenv("LOG_LEVEL", "INFO").upper()
STABILISE_SEC  = int(os.getenv("STABILISE_SEC", 15))   # idle time → ready
PREFERRED_LANG = os.getenv("PREFERRED_LANG", "zh")     # "" = auto
BASE_DIR       = Path(os.getenv("BASE_DIR", "/app/data")).resolve()

INBOX_DIR       = BASE_DIR / "inbox"
PROCESSED_DIR   = BASE_DIR / "processed"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
PARSED_DIR      = BASE_DIR / "parsed"
MARKDOWN_DIR    = BASE_DIR / "markdown"
UPLOADED_DIR    = BASE_DIR / "uploaded"
MODEL_CACHE_DIR = BASE_DIR / "models"
LOG_DIR         = BASE_DIR / "logs"

AUDIO_EXT = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"}
# ---------------------------------------------------------


def setup_dirs() -> None:
    """Create every directory we need if missing."""
    for d in (
        INBOX_DIR,
        PROCESSED_DIR,
        TRANSCRIPTS_DIR,
        PARSED_DIR,
        MARKDOWN_DIR,
        UPLOADED_DIR,
        MODEL_CACHE_DIR,
        LOG_DIR,
    ):
        d.mkdir(parents=True, exist_ok=True)


def fmt_ts(sec: float) -> str:
    millis = int((sec - int(sec)) * 1000)
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"


def save_transcript(result: dict, out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        for seg in result["segments"]:
            f.write(f"[{fmt_ts(seg['start'])} → {fmt_ts(seg['end'])}] "
                    f"{seg['text'].strip()}\n")


# ---------------- watchdog event handler -----------------
class AudioEventHandler(PatternMatchingEventHandler):
    """Collect create/modify events for audio, update `pending` dict."""
    patterns = [f"*{ext}" for ext in AUDIO_EXT]
    ignore_directories = True

    def __init__(self, pending: Dict[Path, float], *args, **kw):
        super().__init__(*args, **kw)
        self.pending = pending

    on_created = on_modified = lambda self, e: self._mark(e.src_path)

    def _mark(self, path_str: str):
        p = Path(path_str)
        self.pending[p] = time.time()
# ---------------------------------------------------------


def transcribe_batch(model: whisper.Whisper, files: List[Path]) -> List[Path]:
    """Whisper transcription, move originals to processed/, return .txt list."""
    txt_paths = []
    for idx, audio in enumerate(files, 1):
        logging.info("▶️  (%d/%d) %s", idx, len(files), audio.name)
        kwargs = dict(word_timestamps=True, verbose=True)
        if PREFERRED_LANG:
            kwargs["language"] = PREFERRED_LANG
        result = model.transcribe(str(audio), **kwargs)
        out_txt = TRANSCRIPTS_DIR / f"{audio.stem}.txt"
        save_transcript(result, out_txt)
        audio.rename(PROCESSED_DIR / audio.name)
        txt_paths.append(out_txt)
    return txt_paths


def handle_batch(batch: List[Path], model: whisper.Whisper) -> None:
    """Run the full downstream chain for one batch."""
    logging.info("📦 Processing batch of %d file(s)", len(batch))

    # 1  Whisper
    transcript_paths = transcribe_batch(model, batch)

    # 2  Parse timestamps every 5 min
    stems = [p.stem for p in transcript_paths]
    batch_parse(stems, TRANSCRIPTS_DIR, PARSED_DIR)

    # 3  Gemini summary
    summarize_all(PARSED_DIR, MARKDOWN_DIR)

    # 4  Upload
    links = batch_upload_markdown_and_move(
        MARKDOWN_DIR, UPLOADED_DIR, os.getenv("HACKMD_TOKEN", "")
    )

    # 5  E-mail
    send_email(links, LOG_DIR / "run.log")

    logging.info("✅ Batch finished")


def main():
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)-8s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_DIR / "service.log"),
        ],
    )

    setup_dirs()
    logging.info("Loading Whisper model (large-v3)…")
    model = whisper.load_model("large-v3", download_root=str(MODEL_CACHE_DIR))
    logging.info("Model ready")

    # --- watchdog observer ---------------------------------------------------
    pending: Dict[Path, float] = {}  # path ➜ last event time
    observer = Observer()
    observer.schedule(AudioEventHandler(pending), str(INBOX_DIR), recursive=False)
    observer.start()

    def shutdown(sig, _):
        logging.info("Received %s – shutting down.", sig.name)
        observer.stop()
        observer.join()
        sys.exit(0)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, shutdown)

    # --- main loop: harvest files once stabilised ----------------------------
    while True:
        now = time.time()
        ready = [p for p, t in list(pending.items()) if now - t >= STABILISE_SEC]
        if ready:
            for p in ready: pending.pop(p, None)          # remove from pending
            handle_batch(ready, model)                    # run pipeline
        time.sleep(1)                                     # light CPU load


if __name__ == "__main__":
    main()
