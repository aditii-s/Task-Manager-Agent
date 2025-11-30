# email_utils.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load .env file
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def send_email(to_email, subject, content):
    if not SENDGRID_API_KEY:
        print("❌ Missing SendGrid credentials.")
        return False
    if not to_email:
        return False  # skip if email not provided
    message = Mail(
        from_email="your_verified_email@example.com",  # verified sender
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code in (200, 202)
    except Exception as e:
        print("SendGrid Error:", e)
        return False
