#!/usr/bin/env python3
"""
parser.py

Reads Whisper‐generated transcript .txt files from TRANSCRIPTS_DIR, applies a
“every 5 minutes” timestamp filter, and writes parsed .txt files to PARSED_DIR.

Functions:
    batch_parse(stems: List[str], transcripts_dir: Path, parsed_dir: Path)
"""

import re
from datetime import timedelta
from pathlib import Path
from typing import List

# Regex to match lines like: [00:00:00.579 → 00:00:01.399] text
timestamp_pattern = re.compile(
    r"\[(\d{2}:\d{2}:\d{2}\.\d{3})\s*→\s*(\d{2}:\d{2}:\d{2}\.\d{3})\]\s*(.*)"
)


def parse_time(s: str) -> timedelta:
    """
    Convert a string like "HH:MM:SS.mmm" into a timedelta.
    """
    h, m, rest = s.split(":")
    s_part, ms = rest.split(".")
    return timedelta(
        hours=int(h), minutes=int(m), seconds=int(s_part), milliseconds=int(ms)
    )


def process_transcript(text: str) -> str:
    """
    Given the full text of a Whisper transcript, produce an output string where:

    • We keep one timestamp every 5 minutes (300 seconds).
    • Each block starts with “[HH:MM:SS.mmm]” (the segment’s start time).
    • We concatenate all lines within that 5-minute window into one paragraph,
      then insert a blank line.
    """
    lines = text.splitlines()
    segments = []

    # 1) Extract all parsed lines into (timestamp, start_str, content)
    for line in lines:
        m = timestamp_pattern.match(line)
        if m:
            start_ts_str, end_ts_str, content = m.groups()
            start_td = parse_time(start_ts_str)
            segments.append((start_td, start_ts_str, content.strip()))

    if not segments:
        return ""

    result_chunks = []
    buffer = ""
    last_mark_minute = None

    for ts_td, start_ts_str, content in segments:
        curr_minute = int(ts_td.total_seconds() // 300)  # each 300 s = 5 min
        if last_mark_minute is None or curr_minute != last_mark_minute:
            # new 5-minute block
            if buffer:
                result_chunks.append(buffer.strip())
                buffer = ""
            result_chunks.append(f"[{start_ts_str}]")
            last_mark_minute = curr_minute
        buffer += content + " "

    # flush final buffer
    if buffer:
        result_chunks.append(buffer.strip())

    # Combine into "[timestamp]\n<text>\n\n" blocks
    output_lines = []
    for i in range(0, len(result_chunks), 2):
        ts_line = result_chunks[i]
        para = result_chunks[i + 1] if i + 1 < len(result_chunks) else ""
        output_lines.append(ts_line)
        output_lines.append(para)
        output_lines.append("")  # blank line

    return "\n".join(output_lines).strip()


def batch_parse(stems: List[str], transcripts_dir: Path, parsed_dir: Path) -> None:
    """
    For each stem in stems, read TRANSCRIPTS_DIR/{stem}.txt, process, and write
    to PARSED_DIR/{stem}_parsed.txt.
    """
    transcripts_dir = Path(transcripts_dir)
    parsed_dir.mkdir(parents=True, exist_ok=True)

    for stem in stems:
        txt_name = f"{stem}.txt"
        src_path = transcripts_dir / txt_name
        if not src_path.exists():
            # Skip if file missing
            continue

        try:
            text = src_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"[parser.py][ERROR] Could not read {src_path}: {e}")
            continue

        processed = process_transcript(text)
        out_name = f"{stem}_parsed.txt"
        out_path = parsed_dir / out_name
        try:
            out_path.write_text(processed, encoding="utf-8")
            print(f"[parser.py] Parsed {txt_name} → {out_name}")
        except Exception as e:
            print(f"[parser.py][ERROR] Could not write {out_path}: {e}")
