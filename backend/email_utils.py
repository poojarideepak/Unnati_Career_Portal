import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import BackgroundTasks
from config import settings

def send_email_async(subject: str, recipient: str, body: str):
    """
    Sends an email using the SMTP settings from config.py.
    This is designed to be run as a BackgroundTask in FastAPI.
    """
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        print(f"[MAIL] Skipping email to {recipient}: MAIL_USERNAME or MAIL_PASSWORD not set in .env")
        return

    try:
        message = MIMEMultipart()
        message["From"] = settings.MAIL_FROM or settings.MAIL_USERNAME
        message["To"] = recipient
        message["Subject"] = subject

        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(message)
            print(f"[MAIL] Email sent successfully to {recipient}")
            
    except Exception as e:
        print(f"[MAIL] Error sending email to {recipient}: {str(e)}")

def trigger_email(background_tasks: BackgroundTasks, subject: str, recipient: str, body: str):
    """Helper to add email task to background."""
    background_tasks.add_task(send_email_async, subject, recipient, body)
