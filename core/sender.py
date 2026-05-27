"""
Email Sender - Gmail SMTP with scheduling, throttling, and tracking
"""

import smtplib
import ssl
import time
import random
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)

SEND_LOG_FILE = Path("data/send_log.json")


class EmailSender:
    """
    Sends cold emails via Gmail SMTP with:
    - Human-like delays between sends
    - Daily send limits
    - Send logging / tracking
    - Retry logic
    """

    def __init__(self, gmail_address: str, gmail_app_password: str,
                 daily_limit: int = 50,
                 min_delay: float = 45.0,
                 max_delay: float = 120.0,
                 log_callback: Callable = None):
        self.gmail_address = gmail_address
        self.gmail_app_password = gmail_app_password
        self.daily_limit = daily_limit
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.log_callback = log_callback or (lambda msg, level="info": None)
        self.send_log = self._load_send_log()

    def _log(self, msg: str, level: str = "info"):
        logger.info(msg)
        self.log_callback(msg, level)

    def _load_send_log(self) -> dict:
        SEND_LOG_FILE.parent.mkdir(exist_ok=True)
        if SEND_LOG_FILE.exists():
            try:
                return json.loads(SEND_LOG_FILE.read_text())
            except:
                pass
        return {"sends": [], "total": 0}

    def _save_send_log(self):
        SEND_LOG_FILE.write_text(json.dumps(self.send_log, indent=2))

    def _sent_today(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        return sum(1 for s in self.send_log["sends"] if s.get("date", "").startswith(today))

    def _create_connection(self):
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
        server.login(self.gmail_address, self.gmail_app_password)
        return server

    def send_email(self, to_email: str, subject: str, body: str,
                   lead_name: str = "") -> bool:
        """Send a single email"""
        if self._sent_today() >= self.daily_limit:
            self._log(f"⚠️ Daily limit of {self.daily_limit} emails reached. Stopping.", "warning")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.gmail_address
            msg["To"] = to_email
            msg["X-Mailer"] = "Thunderbird 115.0"  # Look like real email client

            # Plain text part
            msg.attach(MIMEText(body, "plain"))

            with self._create_connection() as server:
                server.sendmail(self.gmail_address, to_email, msg.as_string())

            # Log the send
            self.send_log["sends"].append({
                "to": to_email,
                "lead": lead_name,
                "subject": subject,
                "date": datetime.now().isoformat(),
                "status": "sent"
            })
            self.send_log["total"] += 1
            self._save_send_log()

            self._log(f"✅ Email sent to {to_email} ({lead_name})", "success")
            return True

        except smtplib.SMTPAuthenticationError:
            self._log("❌ Gmail authentication failed. Check your App Password.", "error")
            return False
        except smtplib.SMTPRecipientsRefused:
            self._log(f"❌ Email rejected for {to_email}", "error")
            return False
        except Exception as e:
            self._log(f"❌ Send failed for {to_email}: {e}", "error")
            return False

    def send_batch(self, leads: list, progress_callback: Callable = None,
                   stop_flag_fn: Callable = None) -> dict:
        """
        Send emails to a batch of leads with human-like delays.
        Returns stats dict.
        """
        stats = {"sent": 0, "skipped": 0, "failed": 0, "stopped": False}

        sendable = [l for l in leads if l.email and l.status == "new"]
        self._log(f"📤 Starting batch send: {len(sendable)} leads", "info")

        for i, lead in enumerate(sendable):
            if stop_flag_fn and stop_flag_fn():
                stats["stopped"] = True
                self._log("🛑 Batch send stopped by user.", "warning")
                break

            if self._sent_today() >= self.daily_limit:
                self._log(f"⚠️ Daily limit reached after {stats['sent']} sends.", "warning")
                break

            if not lead.ai_email_draft:
                stats["skipped"] += 1
                continue

            # Parse subject and body from AI draft
            draft = lead.ai_email_draft
            subject = f"Quick question about {lead.name}"
            body = draft

            if draft.startswith("Subject:"):
                lines = draft.split("\n", 2)
                subject = lines[0].replace("Subject:", "").strip()
                body = "\n".join(lines[2:]).strip() if len(lines) > 2 else draft

            success = self.send_email(lead.email, subject, body, lead.name)

            if success:
                lead.status = "emailed"
                stats["sent"] += 1
            else:
                stats["failed"] += 1

            if progress_callback:
                progress_callback(i + 1, len(sendable), lead, stats)

            # Human-like random delay between emails
            if i < len(sendable) - 1:
                delay = random.uniform(self.min_delay, self.max_delay)
                self._log(f"⏳ Waiting {delay:.0f}s before next send...", "info")
                time.sleep(delay)

        self._log(
            f"📊 Batch complete: {stats['sent']} sent, {stats['failed']} failed, {stats['skipped']} skipped",
            "success"
        )
        return stats

    def test_connection(self) -> tuple[bool, str]:
        """Test Gmail credentials"""
        try:
            with self._create_connection():
                return True, "✅ Gmail connection successful!"
        except smtplib.SMTPAuthenticationError:
            return False, "❌ Authentication failed. Make sure you're using a Gmail App Password, not your regular password."
        except Exception as e:
            return False, f"❌ Connection failed: {e}"
