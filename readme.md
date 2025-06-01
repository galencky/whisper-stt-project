# Whisper-STT Pipeline (Kaggle Edition)  
*End-to-end Speech-to-Text ✚ AI Summaries ✚ Publishing*

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](#license)

> **Author:** Kuan-Yuan Chen (M.D.)  
> **Email:** galen147258369@gmail.com  

---

## ✨ Features

| Stage | What it does | Key Tech |
|-------|--------------|----------|
| **1. Ingest** | Pulls new audio from a **Google Drive “Inbox” folder** into the Kaggle working directory | Google Drive API |
| **2. Transcribe** | Runs **OpenAI Whisper large-v3** (GPU-accelerated, cached) to produce word-level transcripts | `openai-whisper`, PyTorch |
| **3. Parse** | Re-buckets raw transcripts into **5-minute blocks** for cleaner context | Python regex / `datetime` |
| **4. Summarise** | Feeds parsed text + a **system prompt stored in Google Docs** to **Gemini 2.5 Flash** for instant Markdown summaries | Google Generative AI Python SDK |
| **5. Publish** | Uploads each summary to **HackMD** (public read, signed-in edit) and moves the source audio to an “Archive” folder in Drive | HackMD API, Google Drive API |
| **6. Notify** | E-mails you a list of HackMD links once all uploads succeed | Gmail SMTP |
| **7. House-keep** | Syncs processed files back to Drive and wipes the Kaggle workspace (but keeps the Whisper model cache) | Python `shutil`, Drive API |

---

## 🗂 Folder / ID Layout

| Google Drive ID | Purpose | Local mount (inside Kaggle) |
|-----------------|---------|-----------------------------|
| `1AKnppH…` | **Inbox** – audio awaiting transcription | `/kaggle/working/from_google_drive` |
| `1iuVCOQ…` | **Archive** – transcribed audio | *n/a* |
| `1zpXQm…` | **Processed** – `.txt`, `_parsed.txt`, `.md` | *n/a* |

```

Parent
├─ Inbox (to\_be\_transcribed)      ← download →  /from\_google\_drive
├─ Archive (transcribed)          ← audio moved here
└─ Processed
└─ <stem> /
│  <stem>.txt
│  <stem>\_parsed.txt
└─ <stem>.md

````

---

## ⚡ Quick-Start (3 mins)

1. **Fork → “Kaggle Notebook”**  
   *Runtime ▸ “Accelerator = GPU” is strongly recommended.*

2. **Enable required APIs** in your Google Cloud project  
   - Drive API  
   - Docs API  

3. **Create a `kaggle.json` Secrets bundle** (`Add-ons ▸ Secrets`)  
   | Key | Value |
   |-----|-------|
   | `GDRIVE_SERVICE` | *contents of your `service-account.json`* |
   | `GEMINI_API_KEY` | *your genAI key* |
   | `HACKMD_TOKEN` | *personal access token* |
   | `EMAIL_USER` / `EMAIL_PASS` / `EMAIL_TO` | *(optional)* |

4. **Fill in Drive folder IDs** (top of `README` or notebook)  
   ```python
   to_be_transcribed = "1AKnppH…"   # Inbox
   transcribed       = "1iuVCOQ…"   # Archive
````

5. **Upload audio** to the **Inbox** folder and hit **▶ Run All**.

   * Transcripts & summaries appear in `/kaggle/working/*`.
   * HackMD links land in your inbox (if e-mail enabled).

---

## 🏗 Detailed Pipeline Logic

```mermaid
flowchart TD
    A[Google Drive “Inbox”] -->|API download| B(/kaggle/working/from_google_drive)
    B --> C[Whisper large-v3] -->|.txt| D[/transcription]
    D --> E[Parser] -->|_parsed.txt| F[/parsed]
    F -->|Prompt + Gemini| G[Gemini Flash 2.5] -->|.md| H[/markdown]
    H -->|API upload| I[HackMD note]
    H -->|move| J[/uploaded]
    I --> K[Send e-mail summary]
    subgraph Drive sync
        H & D & F -->|API upload| L[Drive “Processed”/<stem>]
        B -->|move audio| M[Drive “Archive”]
    end
```

*Key implementation notes*

* **Model caching** – Whisper downloads once to `/kaggle/working/whisper_models` (persisted across runs).
* **Chunking** – regular expressions split transcripts every 5 minutes, giving Gemini \~3 k tokens per request for cost & speed.
* **System prompt** – stored centrally in Google Docs (`DOC_ID`) so editorial tweaks don’t require code changes.
* **HackMD hygiene** – titles auto-cleaned, single tag `#whisper-stt-project` appended, public-read links returned.
* **Idempotency** – each run checks for **`new_files` flag**; if false, the heavy steps are skipped.

---

## 🔧 Configuration Options

| Variable             | Default                          | Description                                                 |
| -------------------- | -------------------------------- | ----------------------------------------------------------- |
| `PREFERRED_LANGUAGE` | `"zh"`                           | Force Whisper transcription language (`None` = auto-detect) |
| `SYSTEM_PROMPT`      | *(Doc content)*                  | Prompt prepended to each Gemini call                        |
| `GENAI_MODEL`        | `gemini-2.5-flash-preview-05-20` | Tunable for quality vs. speed                               |
| `HAS_EMAIL`          | *env-driven*                     | If any e-mail secret is missing, mail step auto-skips       |

---

## 🩺 Troubleshooting

| Symptom                                      | Fix                                                                                  |
| -------------------------------------------- | ------------------------------------------------------------------------------------ |
| **`Failed to load Whisper`**                 | Ensure GPU is on; verify 16 GB+ RAM quota.                                           |
| **`HttpError 403` from Drive**               | The service-account email must have “viewer + uploader” access to the three folders. |
| **Gemini returns empty / `Invalid API key`** | Confirm `GEMINI_API_KEY` in Kaggle Secrets and billing status.                       |
| **HackMD 401**                               | Regenerate your token (`Settings ▸ API Token`).                                      |
| **Email not sent**                           | Gmail may block “less secure app” login — use an App Password.                       |

---

## 🤝 Contributing

1. Fork the repo & create a branch: `git checkout -b feat/my-feature`
2. Commit your changes: `git commit -m "Add my feature"`
3. Push & open a Pull Request. Issues & feature requests welcome!

---

## 📄 License

This project is licensed under the **MIT License** – see `LICENSE` for details.

---

> Built with ❤️ to turn *raw voice* into *actionable notes* in one click.

```
```
