"""
tools/email_tool.py
--------------------
Email Tool — Callable interface for sending emails.
Uses Gmail API via Google OAuth credentials.

EmailAgent uses this tool to:
- Send drafted emails
- Validate email addresses
- Check sent status
"""

import os
import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ---------------------------
# EmailTool Class
# ---------------------------
class EmailTool:
    """
    Callable interface for Gmail email operations.

    Setup Required (.env):
        GMAIL_SENDER_EMAIL = your-email@gmail.com
        GMAIL_APP_PASSWORD  = your-16-char-app-password

    How to get Gmail App Password:
        1. Go to Google Account → Security
        2. Enable 2-Step Verification
        3. Go to App Passwords
        4. Generate password for "Mail"
        5. Copy the 16-character password to .env

    Usage:
        tool = EmailTool()
        result = tool.send_email(
            to="client@example.com",
            subject="Meeting Follow-up",
            body="Hi, please find the summary..."
        )
    """

    def __init__(self):
        self.sender_email = os.getenv("GMAIL_SENDER_EMAIL")
        self.app_password  = os.getenv("GMAIL_APP_PASSWORD")
        self.tool_name     = "EmailTool"

        if not self.sender_email or not self.app_password:
            logger.warning(
                "[EmailTool] Gmail credentials not found in .env. "
                "Email sending will run in DRY RUN mode."
            )

        logger.info("[EmailTool] Initialized.")

    # ---------------------------
    # Validate Email Address
    # ---------------------------
    def validate_email(self, email: str) -> bool:
        """
        Basic email format validation.

        Args:
            email : Email address string

        Returns:
            bool : True if valid format, False if not

        Usage:
            is_valid = tool.validate_email("user@example.com")
        """
        import re
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        is_valid = bool(re.match(pattern, email))

        if not is_valid:
            logger.warning(f"[EmailTool] Invalid email format: {email}")

        return is_valid

    # ---------------------------
    # Build Email Message
    # ---------------------------
    def _build_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None
    ) -> MIMEMultipart:
        """
        Builds a MIME email message object.

        Args:
            to      : Recipient email address
            subject : Email subject line
            body    : Email body (plain text or HTML)
            cc      : Optional CC email address

        Returns:
            MIMEMultipart : Ready-to-send email object
        """
        message = MIMEMultipart("alternative")
        message["From"]    = self.sender_email
        message["To"]      = to
        message["Subject"] = subject

        if cc:
            message["Cc"] = cc

        # Attach body as plain text
        text_part = MIMEText(body, "plain")
        message.attach(text_part)

        return message

    # ---------------------------
    # SEND EMAIL
    # ---------------------------
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None
    ) -> dict:
        """
        Sends an email via Gmail SMTP.

        Args:
            to      : Recipient email (e.g. "client@example.com")
            subject : Email subject line
            body    : Email body text
            cc      : Optional CC address

        Returns:
            dict : {
                "status"  : "sent" | "dry_run" | "failed",
                "to"      : recipient,
                "subject" : subject,
                "message" : status description
            }

        Usage:
            result = tool.send_email(
                to="manager@company.com",
                subject="Action Items from Today's Meeting",
                body="Hi team, please find action items below..."
            )
        """
        import smtplib

        # Validate recipient
        if not self.validate_email(to):
            return {
                "status": "failed",
                "to": to,
                "subject": subject,
                "message": f"Invalid email address: {to}"
            }

        # Dry run if no credentials
        if not self.sender_email or not self.app_password:
            logger.info(f"[EmailTool] DRY RUN — Would send to: {to} | Subject: {subject}")
            return {
                "status": "dry_run",
                "to": to,
                "subject": subject,
                "message": "Email not sent (no credentials). Dry run mode."
            }

        # Build and send
        try:
            message = self._build_message(to, subject, body, cc)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, to, message.as_string())

            logger.info(f"[EmailTool] Email sent to: {to} | Subject: {subject}")
            return {
                "status": "sent",
                "to": to,
                "subject": subject,
                "message": f"Email successfully sent to {to}"
            }

        except Exception as e:
            error = f"Failed to send email: {str(e)}"
            logger.error(f"[EmailTool] {error}")
            return {
                "status": "failed",
                "to": to,
                "subject": subject,
                "message": error
            }

    # ---------------------------
    # SEND BULK EMAILS
    # ---------------------------
    def send_bulk(self, recipients: list, subject: str, body: str) -> list:
        """
        Sends the same email to multiple recipients.

        Args:
            recipients : List of email addresses
            subject    : Same subject for all
            body       : Same body for all

        Returns:
            list : List of result dicts (one per recipient)

        Usage:
            results = tool.send_bulk(
                recipients=["a@x.com", "b@x.com"],
                subject="Team Update",
                body="Please review the attached agenda..."
            )
        """
        results = []
        for recipient in recipients:
            result = self.send_email(
                to=recipient,
                subject=subject,
                body=body
            )
            results.append(result)

        sent_count = sum(1 for r in results if r["status"] == "sent")
        logger.info(f"[EmailTool] Bulk send: {sent_count}/{len(recipients)} sent.")
        return results

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self) -> str:
        mode = "live" if self.sender_email else "dry_run"
        return f"EmailTool(sender={self.sender_email}, mode={mode})"