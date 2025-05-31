import shutil, time, logging
from pathlib import Path
import whisper

from .config import (INBOX_DIR, PROCESSED_DIR, TRANSCRIPTS_DIR,
                     MODEL_CACHE_DIR, PREFERRED_LANGUAGE, AUDIO_EXT)
from .utils import fmt_ts, now

def _save(result: dict, out_path: Path):
    with out_path.open("w", encoding="utf-8") as f:
        for seg in result["segments"]:
            f.write(f"[{fmt_ts(seg['start'])} → {fmt_ts(seg['end'])}] "
                    f"{seg['text'].strip()}\n")

def batch_transcribe() -> None:
    start = time.time()
    logging.info("Loading Whisper large-v3 …")
    model = whisper.load_model("large-v3", download_root=str(MODEL_CACHE_DIR))
    logging.info("Whisper model ready (%.1fs)", time.time()-start)

    audio_files = [p for p in INBOX_DIR.iterdir()
                   if p.suffix.lower() in AUDIO_EXT]

    if not audio_files:
        logging.info("📂 Inbox empty – nothing to transcribe.")
        return

    for idx, audio in enumerate(audio_files, 1):
        logging.info("▶️  (%d/%d) %s", idx, len(audio_files), audio.name)
        kwargs = dict(word_timestamps=True, verbose=True)
        if PREFERRED_LANGUAGE:
            kwargs["language"] = PREFERRED_LANGUAGE
        result = model.transcribe(str(audio), **kwargs)

        out_txt = TRANSCRIPTS_DIR / f"{audio.stem}.txt"
        _save(result, out_txt)
        logging.info("Saved transcript → %s", out_txt.name)

        shutil.move(audio, PROCESSED_DIR / audio.name)
        logging.info("Moved audio to processed/")
