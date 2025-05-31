import re, logging
from datetime import timedelta
from pathlib import Path

from .config import TRANSCRIPTS_DIR, PARSED_DIR

TIMESTAMP_RE = re.compile(
    r"\[(\d{2}:\d{2}:\d{2}\.\d{3})\s*→\s*(\d{2}:\d{2}:\d{2}\.\d{3})]\s*(.*)"
)

def _to_td(ts: str) -> timedelta:
    h, m, rest = ts.split(":")
    s, ms = rest.split(".")
    return timedelta(hours=int(h), minutes=int(m),
                     seconds=int(s), milliseconds=int(ms))

def _reformat(raw_text: str) -> str:
    segments, out, buf, last_block = [], [], "", None
    for line in raw_text.splitlines():
        m = TIMESTAMP_RE.match(line)
        if not m:
            continue
        start_ts, _, content = m.groups()
        td = _to_td(start_ts)
        block = int(td.total_seconds() // 300)  # 5-min blocks
        if last_block is None or block != last_block:
            if buf:
                out.append(buf.strip())
                buf = ""
            out.append(f"[{start_ts}]")
            last_block = block
        buf += content.strip() + " "
    if buf:
        out.append(buf.strip())

    # interleave timestamp + paragraph + blank line
    final = []
    for i in range(0, len(out), 2):
        final.append(out[i])
        if i+1 < len(out):
            final.extend([out[i+1], ""])
    return "\n".join(final).strip()

def batch_parse() -> None:
    for txt in TRANSCRIPTS_DIR.glob("*.txt"):
        parsed = PARSED_DIR / f"{txt.stem}_parsed.txt"
        parsed.write_text(_reformat(txt.read_text(encoding="utf-8")),
                          encoding="utf-8")
        logging.info("🪄 Parsed %s → %s", txt.name, parsed.name)
