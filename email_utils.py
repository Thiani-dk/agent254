# email_utils.py
from datetime import datetime
import smtplib
from flask import current_app
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_otp_email(
    *,
    to_address: str,
    message_id: str,
    otp_code: str,
    expiry_seconds: int,
    sender: str = None,
    link: str = None,
    attachment_path: str = None
) -> bool:
    """
    Sends a formatted HTML email via SMTP using app config.
    """
    mail_server = current_app.config.get("MAIL_SERVER")
    mail_port = int(current_app.config.get("MAIL_PORT", 587))
    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_password = current_app.config.get("MAIL_PASSWORD")
    mail_use_tls = str(current_app.config.get("MAIL_USE_TLS")).lower() in ("1", "true", "yes")

    if not all([mail_server, mail_port, mail_username, mail_password]):
        current_app.logger.error("Email configuration is incomplete. Cannot send email.")
        return False

    msg = MIMEMultipart()
    msg["From"] = f"Agent254 Secure Messaging <{mail_username}>"
    msg["To"] = to_address
    msg["Subject"] = f"A Secure Message was sent to you from {sender}"
    if sender:
        msg["Reply-To"] = sender

    body = f"""
    Your OTP is: {otp_code}
    Message ID: {message_id}
    This OTP will expire in {expiry_seconds // 60} minutes.
    """
    msg.attach(MIMEText(body, "plain"))

    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                filename = os.path.basename(attachment_path)
                part.add_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
                msg.attach(part)
        except Exception as e:
            current_app.logger.error(f"Failed to attach file {attachment_path}: {e}")
            # Decide if you want to fail the entire email or send without attachment
            return False

    try:
        with smtplib.SMTP(mail_server, mail_port) as server:
            if mail_use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            # --- FIX: Send from the server's login email (mail_username) ---
            # The 'From' header is what the recipient sees. 'sender' is used for the mail envelope.
            # Using mail_username here prevents SMTP relay errors.
            server.sendmail(mail_username, to_address, msg.as_string())
            current_app.logger.info(f"OTP email sent to {to_address} with Message ID: {message_id}")
        return True
    except smtplib.SMTPException as e:
        current_app.logger.error(f"SMTP error sending email: {e}")
        return False
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred while sending email: {e}")
        return False