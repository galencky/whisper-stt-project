# === File: watcher.py ===

import os
import time
import threading
from pathlib import Path
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from app.main import run_pipeline
from app.config import INBOX_DIR, AUDIO_EXT

STABILIZATION_TIME = 15  # seconds


def is_file_stable(path: Path, wait: int = STABILIZATION_TIME) -> bool:
    """Return True if file size hasn't changed after `wait` seconds."""
    if not path.exists():
        return False
    initial_size = path.stat().st_size
    time.sleep(wait)
    return path.exists() and path.stat().st_size == initial_size


class InboxHandler(FileSystemEventHandler):
    def __init__(self):
        self.lock = threading.Lock()
        self.scheduled = False

    def _schedule_run(self):
        with self.lock:
            if not self.scheduled:
                self.scheduled = True
                threading.Thread(target=self._trigger_pipeline).start()

    def _trigger_pipeline(self):
        print("⏳ Waiting for files to stabilize…")
        time.sleep(STABILIZATION_TIME)
        audio_files = [
            f for f in INBOX_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in AUDIO_EXT
        ]

        # Filter to only stable files
        stable_files = [f for f in audio_files if is_file_stable(f)]
        if stable_files:
            print("✅ Stable files detected, starting pipeline…")
            run_pipeline("all")
        else:
            print("⚠️ No stable audio files yet.")

        with self.lock:
            self.scheduled = False

    def on_created(self, event):
        if not event.is_directory and Path(event.src_path).suffix.lower() in AUDIO_EXT:
            self._schedule_run()

    def on_moved(self, event):
        if not event.is_directory and Path(event.dest_path).suffix.lower() in AUDIO_EXT:
            self._schedule_run()


if __name__ == "__main__":
    print(f"👀 Watching inbox: {INBOX_DIR}")
    observer = PollingObserver(timeout=5)
    handler = InboxHandler()
    observer.schedule(handler, str(INBOX_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
