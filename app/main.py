# === app/main.py ===

import argparse, logging
from pathlib import Path

from .utils import setup_logging, purge_dir, zip_results
from .config import (INBOX_DIR, PROCESSED_DIR, TRANSCRIPTS_DIR,
                     PARSED_DIR, MARKDOWN_DIR, LOG_DIR)
from .transcriber import batch_transcribe
from .parser import batch_parse
from .summarizer import summarize_all
from .emailer import send_email

def _package_and_clean(stems: list[str]) -> None:
    for stem in stems:
        audio = next((p for p in PROCESSED_DIR.iterdir() if p.stem == stem), None)
        if audio is None:
            logging.warning("Audio for %s not found in processed/", stem)
            continue
        zip_path = zip_results(stem, audio)
        logging.info("📦 Bundled → %s", zip_path.name)

    send_email([], LOG_DIR / "run.log")

    for d in (INBOX_DIR, PROCESSED_DIR, TRANSCRIPTS_DIR,
              PARSED_DIR, MARKDOWN_DIR):
        purge_dir(d)

    (LOG_DIR / "run.log").unlink(missing_ok=True)

def run_pipeline(stage: str = "all") -> None:
    setup_logging()
    logging.info("🚀 Starting stage: %s", stage)

    if stage == "transcribe":
        batch_transcribe()
    elif stage == "parse":
        batch_parse()
    elif stage == "summarise":
        summarize_all()
    elif stage == "all":
        batch_transcribe()
        batch_parse()
        stems = summarize_all()
        _package_and_clean(stems)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", nargs="?", default="all",
                        choices=["transcribe", "parse", "summarise", "all"],
                        help="stage to execute (default: full pipeline)")
    args = parser.parse_args()
    run_pipeline(args.task)

if __name__ == "__main__":
    main()
