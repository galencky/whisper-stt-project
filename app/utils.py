import datetime, logging, sys, shutil, zipfile
from pathlib import Path
from typing import Optional

from .config import (OUTPUT_DIR, TRANSCRIPTS_DIR, PARSED_DIR, MARKDOWN_DIR,
                     LOG_DIR)

# ───────────────── logging ─────────────────
def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "run.log", mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ───────────────── helpers ─────────────────
def fmt_ts(seconds: float) -> str:
    h, m = divmod(int(seconds), 3600)
    m, s = divmod(m, 60)
    ms   = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

def purge_dir(folder: Path):
    """Delete all contents (files & subfolders) inside *folder*."""
    for item in folder.iterdir():
        if item.is_file():
            item.unlink(missing_ok=True)
        else:
            shutil.rmtree(item, ignore_errors=True)

def zip_results(stem: str, audio_path: Path) -> Path:
    """
    Bundle audio + all intermediate artefacts for <stem> into output/<stem>.zip
    """
    zip_path = OUTPUT_DIR / f"{stem}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(audio_path,                               arcname=audio_path.name)
        z.write(TRANSCRIPTS_DIR / f"{stem}.txt",          arcname=f"{stem}.txt")
        z.write(PARSED_DIR      / f"{stem}_parsed.txt",   arcname=f"{stem}_parsed.txt")
        z.write(MARKDOWN_DIR    / f"{stem}.md",           arcname=f"{stem}.md")
    return zip_path
