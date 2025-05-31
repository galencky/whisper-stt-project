#!/usr/bin/env python3
"""
emailer.py

Sends an email listing the HackMD shared links. If shared_links is empty,
nothing is sent. Otherwise, it reads environment variables EMAIL_USER,
EMAIL_PASS, EMAIL_TO. It will append a timestamp to a run.log file.

Functions:
    send_email(shared_links: List[Dict[str,str]], log_path: Path) -> None
"""

import os
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict

def send_email(shared_links: List[Dict[str, str]], log_path: Path) -> None:
    """
    Build and send an email listing each shared_link's title & URL. Append
    a summary line to log_path after sending.
    """
    if not shared_links:
        # Nothing to send
        return

    load_dotenv()
    email_user = os.getenv("EMAIL_USER", "")
    email_pass = os.getenv("EMAIL_PASS", "")
    email_to   = os.getenv("EMAIL_TO", "")

    if not (email_user and email_pass and email_to):
        print("[emailer.py][ERROR] EMAIL_USER or EMAIL_PASS or EMAIL_TO missing; cannot send email.")
        return

    subject = "📝 Your Uploaded HackMD Speech Summaries"
    # Build body lines
    body_lines = [
        "Hello,",
        "",
        "Your audio files have been transcribed with Whisper AI,",
        "and summaries have been posted to HackMD. Here are the links:",
        "",
    ]
    for link in shared_links:
        title = link.get("title", "")
        url = link.get("url", "")
        body_lines.append(f"- {title}: {url}")
    body_lines += [
        "",
        "These notes are public to anyone with the link.",
        "Feel free to reply if you have any questions.",
        "",
        "Best regards,",
        "Whisper-STT-Project Bot",
    ]
    body = "\n".join(body_lines)

    # Compose email
    msg = MIMEMultipart()
    msg["From"]    = email_user
    msg["To"]      = email_to
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
        print("[emailer.py] Email sent successfully.")
        # Append to log:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(f"[{ts}] Email sent with {len(shared_links)} link(s)\n")
    except Exception as e:
        print(f"[emailer.py][ERROR] Failed to send email: {e}")
