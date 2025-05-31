import logging
from pathlib import Path
import google.generativeai as genai

from .config import GEMINI_API_KEY, PARSED_DIR, MARKDOWN_DIR, PROMPT_PATH
genai.configure(api_key=GEMINI_API_KEY)

def _prompt() -> str:
    return Path(PROMPT_PATH).read_text(encoding="utf-8").strip()

def summarize_all() -> list[str]:
    prompt = _prompt()
    model  = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
    completed = []

    for parsed in PARSED_DIR.glob("*.txt"):
        stem   = parsed.stem.replace("_parsed", "")
        speech = parsed.read_text(encoding="utf-8").strip()
        logging.info("👓 Summarising %s …", parsed.name)
        resp = model.generate_content(prompt + "\n\n" + speech,
                                      generation_config={"temperature": 0.5})
        md_path = MARKDOWN_DIR / f"{stem}.md"
        md_path.write_text(resp.text, encoding="utf-8")
        logging.info("Saved summary → %s", md_path.name)
        completed.append(stem)

    return completed
