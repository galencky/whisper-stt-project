#!/usr/bin/env python3
"""
uploader.py

Uploads each Markdown (.md) file from MARKDOWN_DIR to HackMD via API, moves
successful uploads into UPLOADED_DIR, and returns a list of shared‐link dicts.

Functions:
    batch_upload_markdown_and_move(markdown_dir: Path, uploaded_dir: Path, hackmd_token: str)
"""

import os
import shutil
import requests
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────────────────────
def _upload_to_hackmd(md_content: str, filename: str, api_token: str) -> Dict[str, str]:
    """
    Given raw Markdown text and a filename (ending in .md), post to HackMD,
    return {"title": ..., "url": ...} if successful, else None.
    """
    # Prepare title: strip “_parsed” or other suffixes, replace underscores
    name_no_ext = filename[:-3] if filename.endswith(".md") else filename
    raw_title = name_no_ext.replace("_parsed", "").strip()
    title = raw_title.replace("_", " ").strip()

    # Ensure first line is "# Title"
    content_lines = md_content.lstrip().splitlines()
    if not content_lines or not content_lines[0].startswith("# "):
        md_content = f"# {title}\n\n" + md_content.lstrip()
    else:
        content_lines[0] = f"# {title}"
        md_content = "\n".join(content_lines)

    # Append hashtag if missing
    hashtag = "#whisper-stt-project"
    lines = md_content.rstrip().splitlines()
    if not any(line.strip() == hashtag for line in lines[-3:]):
        md_content = md_content.rstrip() + "\n\n" + hashtag + "\n"

    url = "https://api.hackmd.io/v1/notes"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    data = {"title": title, "content": md_content, "readPermission": "guest", "writePermission": "signed_in"}

    resp = requests.post(url, headers=headers, json=data)
    if resp.ok:
        note_id = resp.json().get("id")
        shared_url = f"https://hackmd.io/{note_id}"
        print(f"[uploader.py] Uploaded: {shared_url}")
        return {"title": title, "url": shared_url}
    else:
        print(f"[uploader.py][ERROR] Upload failed for {filename}: {resp.status_code} {resp.text}")
        return {}


def batch_upload_markdown_and_move(markdown_dir: Path, uploaded_dir: Path, hackmd_token: str) -> List[Dict[str, str]]:
    """
    For each “*.md” in markdown_dir:
        • Read file
        • upload → HackMD
        • If success, move md into uploaded_dir
    Return list of {"title": ..., "url": ...}.
    """
    load_dotenv()
    if not hackmd_token:
        hackmd_token = os.getenv("HACKMD_TOKEN", "")
    if not hackmd_token:
        print("[uploader.py][ERROR] HACKMD_TOKEN missing; skipping upload.")
        return []

    markdown_dir = Path(markdown_dir)
    uploaded_dir = Path(uploaded_dir)
    uploaded_dir.mkdir(parents=True, exist_ok=True)

    md_files = list(markdown_dir.glob("*.md"))
    print(f"[uploader.py] Found {len(md_files)} markdown files to upload.")

    shared_links = []
    for md_file in md_files:
        print(f"[uploader.py] ≫ Processing {md_file.name}")
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"[uploader.py][ERROR] Could not read {md_file.name}: {e}")
            continue

        result = _upload_to_hackmd(content, md_file.name, hackmd_token)
        if result:
            shared_links.append(result)
            dest = uploaded_dir / md_file.name
            try:
                shutil.move(str(md_file), str(dest))
                print(f"[uploader.py] Moved {md_file.name} → uploaded/")
            except Exception as e:
                print(f"[uploader.py][ERROR] Could not move {md_file.name}: {e}")

    return shared_links
