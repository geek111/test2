import smtplib
from email.message import EmailMessage
from typing import Optional


def send_email(recipient: str, subject: str, body: str,
               smtp_server: str = 'localhost',
               smtp_port: int = 25,
               username: Optional[str] = None,
               password: Optional[str] = None) -> None:
    """Send a simple text email."""
    msg = EmailMessage()
    msg['From'] = username or 'price-tracker@example.com'
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port) as s:
        if username and password:
            s.starttls()
            s.login(username, password)
        s.send_message(msg)
