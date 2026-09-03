import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


def send_email(recipient_email, subject, body):
    """
    Send an email using the configured SMTP server.
    """

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")

    if not smtp_host:
        raise ValueError("SMTP_HOST is not configured")

    if not smtp_username:
        raise ValueError("SMTP_USERNAME is not configured")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD is not configured")

    if not sender_email:
        raise ValueError("SENDER_EMAIL is not configured")

    message = EmailMessage()

    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:

        server.starttls()

        server.login(
            smtp_username,
            smtp_password
        )

        server.send_message(message)

    return True

from database.database import create_email_log, update_email_log


def send_notice_email(
    notice_id,
    faculty_id,
    recipient_email,
    subject,
    body
):
    """
    Send a notice email and record the result in email_logs.
    """

    log_id = create_email_log(
        notice_id,
        faculty_id,
        recipient_email,
        subject
    )

    try:

        send_email(
            recipient_email,
            subject,
            body
        )

        update_email_log(
            log_id,
            "Sent"
        )

        return True

    except Exception as error:

        update_email_log(
            log_id,
            "Failed",
            str(error)
        )

        return False