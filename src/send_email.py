"""
send_email.py
-------------
Builds and sends the final digest email over Gmail's SMTP server.

Why SMTP + a Gmail App Password instead of a transactional email API
(SendGrid, Mailgun, etc.): zero extra signup and zero extra cost - you
already have a Gmail account. The one requirement is that 2-Step
Verification must be ON for the sending account, and you generate an
"App Password" for this script to use - your normal Gmail password will
NOT work over SMTP. Setup steps are in README.md.
"""

import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

IST = timezone(timedelta(hours=5, minutes=30))


def _build_html(date_str, sections):
    parts = [
        "<html><body style='font-family:Arial,sans-serif;line-height:1.5;color:#222;'>",
        f"<h1 style='margin-bottom:0;'>Your World Digest</h1>",
        f"<p style='color:#666;margin-top:4px;'>{date_str} &middot; last 24 hours</p>",
    ]
    for category, body in sections.items():
        parts.append(
            f"<h2 style='border-bottom:1px solid #ccc;padding-bottom:4px;"
            f"margin-top:28px;'>{category}</h2>"
        )
        parts.append(f"<div style='white-space:pre-wrap;'>{body}</div>")
    parts.append("</body></html>")
    return "\n".join(parts)


def _build_plain(date_str, sections):
    lines = [f"YOUR WORLD DIGEST - {date_str}", "=" * 40, ""]
    for category, body in sections.items():
        lines.append(category.upper())
        lines.append("-" * len(category))
        lines.append(body)
        lines.append("")
    return "\n".join(lines)


def send_digest(sections):
    """
    sections: dict of {category_name: summary_text}
    Reads credentials from environment variables (set as GitHub Actions
    secrets in production, or a local .env file for testing):
      SENDER_EMAIL, SENDER_APP_PASSWORD, RECEIVER_EMAIL
    """
    sender = os.environ["SENDER_EMAIL"]
    app_password = os.environ["SENDER_APP_PASSWORD"]
    receiver = os.environ["RECEIVER_EMAIL"]

    now_ist = datetime.now(IST)
    date_str = now_ist.strftime("%A, %d %B %Y")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your World Digest - {date_str}"
    msg["From"] = sender
    msg["To"] = receiver

    # Attach plain text FIRST, then HTML - email clients render the last
    # (most-preferred) part they understand, so HTML wins in Gmail/Outlook
    # while plain-text-only clients still get something readable.
    msg.attach(MIMEText(_build_plain(date_str, sections), "plain"))
    msg.attach(MIMEText(_build_html(date_str, sections), "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, app_password)
        server.sendmail(sender, receiver, msg.as_string())

    print(f"[send_email] Digest sent to {receiver}")
