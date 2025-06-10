# email_utils.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app
from datetime import datetime

def send_otp_email(recipient_email: str, otp_code: str, expiry_seconds: int, sender_email: str = None):
    """
    Sends an OTP email synchronously. Returns True on success, False on failure.
    The email body will include:
      • Sender’s email
      • “Retrieve” link
      • Message ID & OTP
      • Expiry period
    """
    try:
        app = current_app._get_current_object()
        mail_server = app.config["MAIL_SERVER"]
        mail_port = app.config["MAIL_PORT"]
        mail_username = app.config["MAIL_USERNAME"]
        mail_password = app.config["MAIL_PASSWORD"]
        use_tls = app.config["MAIL_USE_TLS"]

        # Determine “from” address
        from_addr = mail_username
        if sender_email:
            # If we want to explicitly show “sender” in body, we include it in message text.
            # But actual SMTP from‐address must be mail_username (for authentication).
            pass

        # Compose message
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = recipient_email
        msg["Subject"] = "Agent254: Your One-Time Password (OTP) & Retrieve Link"

        retrieve_link = f"{app.config.get('BASE_URL', '')}/retrieve"
        #   If you deploy under some domain, set BASE_URL in environment (e.g. https://agent254.yourdomain.com)

        body = f"""
Hello,

You have received a secure message through Agent254.

Sender’s email: {sender_email or 'Unknown Sender'}

To decrypt the message:
  1. Visit: {retrieve_link}
  2. Enter the following:

     • Message ID: <YOUR MESSAGE ID HERE—you’ll receive that separately>  
     • OTP: {otp_code}

The OTP and Message ID do not appear in this email (they were sent separately by your colleague).
If you do not have the Message ID, ask your sender to forward it.

OTP expires in {expiry_seconds} seconds (until {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} + {expiry_seconds} s).

Thank you,
Agent254 Bot
"""
        msg.attach(MIMEText(body, "plain"))

        # Connect to SMTP
        server = smtplib.SMTP(mail_server, mail_port, timeout=10)
        if use_tls:
            server.starttls()
        server.login(mail_username, mail_password)
        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        # Log failure
        print(f"[email_utils] Failed to send OTP email: {e}")
        return False
