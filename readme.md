# 📝 Whisper Speech Summarizer & HackMD Uploader

A complete workflow for **batch-transcribing audio files**, **summarizing speech with Gemini Flash 2.5**, **publishing summaries to HackMD**, and **notifying users via email**.

---

## Features

- **Audio → Text**: Uses [OpenAI Whisper](https://github.com/openai/whisper) to transcribe audio files in your preferred language.
- **Timestamp Processing**: Cleans up Whisper's transcripts, segments into ~5 minute paragraphs, and saves to `.txt`.
- **Speech Summarization**: Sends the processed transcript to Google Gemini (Flash 2.5) for markdown summaries using a structured prompt.
- **HackMD Integration**: Publishes each summary to [HackMD](https://hackmd.io/) and retrieves shareable links.
- **Email Notification**: Automatically emails you all the HackMD summary links after upload.

---

## Folder Structure

```

whisper-stt-project/
│
├── inbox/          # Put audio files here (.wav, .mp3, etc.)
├── processed/      # Audio files are moved here after processing
├── transcripts/    # Raw Whisper transcripts (.txt)
├── parsed/         # Cleaned, 5-min-segmented transcript files
├── markdown/       # Gemini-generated markdown summaries
├── uploaded/       # Markdown files after HackMD upload
├── models/         # Whisper model files/cache
├── .env            # Your secrets (see below)
├── requirements.txt
├── README.md
└── your\_scripts.py

````

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
````

### 2. Prepare your `.env` file

Create a `.env` file in your project root with:

```env
GEMINI_API_KEY=your-google-gemini-api-key
HACKMD_TOKEN=your-hackmd-api-token
EMAIL_USER=your@email.com
EMAIL_PASS=your-email-password-or-app-password
EMAIL_TO=recipient@email.com
```

* **GEMINI\_API\_KEY**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey).
* **HACKMD\_TOKEN**: See [HackMD API Docs](https://hackmd.io/@hackmd-api/developer-docs).
* **EMAIL\_USER/PASS**: Use an [App Password](https://support.google.com/accounts/answer/185833) if using Gmail.
* **EMAIL\_TO**: Where to send the notification with HackMD links.

---

## Usage

### 1. Place audio files in `inbox/`

Supported: `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.webm`.

### 2. Run the scripts in order:

#### (A) **Transcribe audio and segment:**

* Transcribes all audio in `inbox/` to `transcripts/` with Whisper.
* Cleans and segments transcripts into `parsed/` (\~5min per paragraph).

#### (B) **Summarize with Gemini Flash 2.5:**

* Batch-sends all files in `parsed/` to Gemini, saving markdown summaries in `markdown/`.

#### (C) **Upload summaries to HackMD:**

* Publishes all markdowns in `markdown/` to HackMD, moves them to `uploaded/`, and collects public links.

#### (D) **Notify via Email:**

* Sends you an email listing all HackMD summary links.

*You can run these steps as a single script or as independent modules, depending on your workflow.*

---

## System Prompt for Gemini Summarization

This system uses a **precisely structured prompt** for Gemini to create consistent, high-quality summaries with markdown. The summary includes title, speaker, overview, key points, notable quotes, audience reaction, and conclusion.

---

## Example Output

* Clean transcripts:

  ```
  [00:00:00.000]
  ...first 5 min of speech in one paragraph...

  [00:05:01.234]
  ...next 5 min...
  ```
* Gemini summary in markdown (sample structure):

  ```markdown
  # Title of the Speech

  ### Speaker
  * **Name**: Dr. Example
  * **Affiliation/Role**: Example University
  * **Event**: Medical AI Conference
  * **Date**: 2025-05-28

  ### Overview
  The speech covered...

  ### Key Points
  - AI can transform medical documentation.
  - Patient privacy is crucial.

  ### Notable Quotes
  * "AI will not replace doctors, but doctors who use AI will replace those who don't."

  ### Audience Reaction
  Applause at key points.

  ### Conclusion
  The speaker emphasized collaboration...

  #whisper-stt-project
  ```

---

## Troubleshooting

* Make sure your `.env` file is correct and all required API keys/tokens are set.
* Whisper requires a compatible CUDA environment for GPU acceleration; otherwise, it defaults to CPU.
* Gemini API quota applies.
* HackMD uploads may fail if the token is invalid or rate limits are reached.

---

## Acknowledgments

* **OpenAI Whisper** for robust speech-to-text.
* **Google Gemini** for LLM-powered summaries.
* **HackMD** for easy markdown sharing.

---

## License

MIT

---

## Author

Built by [galencky](mailto:galen147258369@gmail.com) | Vibecoder
