#!/usr/bin/env python3
"""
summarizer.py

Loads Gemini via google.generativeai, reads a system prompt from an external
"text file" (so you can re-upload/change it), applies that prompt to each parsed
text file in PARSED_DIR, and writes the resulting Markdown (.md) into
MARKDOWN_DIR.

Functions:
    summarize_all(parsed_dir: Path, markdown_dir: Path) -> None
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List

# ──────────────────────────────────────────────────────────────────────────────
# Instead of embedding SYSTEM_PROMPT here, we read it from an external file.
# By default, we look for "system_prompt.txt" in the same folder as this script.
PROMPT_FILENAME = "system_prompt.txt"
# ──────────────────────────────────────────────────────────────────────────────


def _configure_gemini():
    """
    Load .env (looking for GEMINI_API_KEY) and configure genai.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env!")
    genai.configure(api_key=api_key)


def _load_system_prompt() -> str:
    """
    Reads the system prompt from an external .txt file. By default, it expects
    a file named 'system_prompt.txt' in the same directory as this script.
    Raise an error if the file does not exist or cannot be read.
    """
    script_dir = Path(__file__).parent
    prompt_path = script_dir / PROMPT_FILENAME

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"[summarizer.py] System prompt file not found at: {prompt_path}"
        )

    try:
        prompt_text = prompt_path.read_text(encoding="utf-8")
    except Exception as e:
        raise IOError(f"[summarizer.py] Failed to read prompt file: {e}")

    return prompt_text


def _generate_summary(speech_text: str, system_prompt: str) -> str:
    """
    Call Gemini (gemini-2.5-flash-preview-05-20) with the combined prompt.
    """
    model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
    full_prompt = system_prompt.strip() + "\n\n" + speech_text.strip()
    try:
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.5),
            stream=False,
        )
        return response.text
    except Exception as e:
        print(f"[summarizer.py][ERROR] Gemini API error: {e}")
        return ""


def summarize_all(parsed_dir: Path, markdown_dir: Path) -> None:
    """
    For every “*.txt” in parsed_dir, generate a .md summary into markdown_dir,
    using the system prompt loaded from an external file.
    """
    _configure_gemini()

    # Load the system prompt from the external file each time
    try:
        system_prompt = _load_system_prompt()
    except Exception as e:
        print(e)
        return

    parsed_dir = Path(parsed_dir)
    markdown_dir = Path(markdown_dir)
    markdown_dir.mkdir(parents=True, exist_ok=True)

    txt_files = list(parsed_dir.glob("*.txt"))
    print(f"[summarizer.py] Found {len(txt_files)} .txt files in {parsed_dir}")

    for txt_path in txt_files:
        print(f"[summarizer.py] Processing: {txt_path.name}")
        try:
            speech_text = txt_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            print(f"[summarizer.py][ERROR] Could not read {txt_path}: {e}")
            continue

        if not speech_text:
            print(f"[summarizer.py][WARNING] {txt_path.name} is empty, skipping.")
            continue

        summary_md = _generate_summary(speech_text, system_prompt)
        if not summary_md:
            print(f"[summarizer.py][ERROR] Failed to summarize {txt_path.name}, skipping.")
            continue

        md_filename = txt_path.stem + ".md"
        out_path = markdown_dir / md_filename
        try:
            out_path.write_text(summary_md, encoding="utf-8")
            print(f"[summarizer.py] Saved summary → {md_filename}")
        except Exception as e:
            print(f"[summarizer.py][ERROR] Could not write {out_path}: {e}")
