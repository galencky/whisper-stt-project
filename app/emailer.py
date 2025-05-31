import logging, ssl, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path
from typing import List, Dict

from .config import EMAIL_USER, EMAIL_PASS, EMAIL_TO

def send_email(shared_links: List[Dict[str, str]], log_path: Path) -> None:
    """Attach run.log and list of shared links (if any)."""
    if not (EMAIL_USER and EMAIL_PASS and EMAIL_TO):
        logging.warning("Email creds not set – skipping e-mail.")
        return

    subject = "📝 Whisper-STT batch completed"
    body    = ["Hello,",
               "",
               "Your batch has finished. See run.log attached.",
               "",
               "Links:"]
    for link in shared_links:
        body.append(f"- {link['title']}: {link['url']}")
    body = "\n".join(body)

    msg = MIMEMultipart()
    msg["From"], msg["To"] = EMAIL_USER, EMAIL_TO
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # attach log
    with log_path.open("r", encoding="utf-8") as fp:
        att = MIMEText(fp.read(), "plain", "utf-8")
        att.add_header("Content-Disposition", "attachment",
                       filename=Header("run.log", "utf-8").encode())
        msg.attach(att)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        s.login(EMAIL_USER, EMAIL_PASS)
        s.send_message(msg)
    logging.info("📧 E-mail sent to %s", EMAIL_TO)
