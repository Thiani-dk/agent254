# email_utils.py
import os
import smtplib
from datetime import datetime
from flask import current_app
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_otp_email(
    *,
    to_address: str,
    message_id: str,
    otp_code: str,
    expiry_seconds: int,
    sender: str = None,
    link: str = None,
    attachment_path: str = None  # New argument for the attachment
) -> bool:
    """
    Sends a formatted HTML email with an optional zipped attachment.
    """
    cfg = {
        "host": os.getenv("MAIL_SERVER"), "port": int(os.getenv("MAIL_PORT", 587)),
        "username": os.getenv("MAIL_USERNAME"), "password": os.getenv("MAIL_PASSWORD"),
        "use_tls": os.getenv("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes"),
    }

    if not all([cfg["host"], cfg["port"], cfg["username"], cfg["password"]]):
        current_app.logger.error("Email configuration is incomplete. Cannot send email.")
        return False

    # Use MIMEMultipart to handle text, HTML, and attachments
    msg = MIMEMultipart()
    msg["From"] = f"Agent254 Secure Messaging <{cfg['username']}>"
    msg["To"] = to_address
    msg["Subject"] = f"A Secure Message was sent to you from {sender}"
    if sender:
        msg["Reply-To"] = sender

    # The same HTML body as before
    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Secure Message Notification</title></head>
<body style="font-family: sans-serif; margin: 20px; background-color: #f4f7f6; color: #333;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0"><tr><td align="center">
    <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 8px;">
        <tr><td align="center" style="padding: 20px; background-color: #0d6efd; color: #ffffff;">
            <h1 style="margin: 0;">Agent254</h1>
        </td></tr>
        <tr><td style="padding: 30px;">
            <h2 style="font-size: 20px;">You've Received a Secure Message</h2>
            <p style="font-size: 16px;">You have a secure message from <strong>{sender or 'an Agent254 user'}</strong>.</p>
            <table width="100%" border="0" style="margin: 20px 0; border: 1px dashed #ccc; padding: 15px;">
                <tr><td><strong>Message ID:</strong></td><td style="font-family: monospace;">{message_id}</td></tr>
                <tr><td style="height: 10px;"></td></tr>
                <tr><td><strong>OTP:</strong></td><td style="font-family: monospace;">{otp_code}</td></tr>
            </table>
            <p align="center" style="margin: 30px 0;">
                <a href="{link}" target="_blank" style="background-color: #0d6efd; color: #ffffff; padding: 12px 25px; text-decoration: none; border-radius: 5px;">Decrypt & View Message</a>
            </p>
        </td></tr>
        <tr><td style="padding: 20px; text-align: center; background-color: #f4f7f6; font-size: 12px; color: #888;">
            <p style="margin: 0;">&copy; {datetime.now().year} Agent254. All Rights Reserved.</p>
        </td></tr>
    </table>
    </td></tr></table>
</body>
</html>
    """
    msg.attach(MIMEText(html_body, "html"))

    # --- FEATURE: ATTACHMENT HANDLING ---
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as f:
                # Create the attachment part
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            # Add header to make it an attachment
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)
            current_app.logger.info(f"Attaching file: {attachment_path}")
        except Exception as e:
            current_app.logger.error(f"Failed to attach file {attachment_path}: {e}")
            # Continue without attachment if it fails
    
    try:
        with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
            if cfg["use_tls"]:
                server.starttls()
            server.login(cfg["username"], cfg["password"])
            server.send_message(msg)
        current_app.logger.info(f"OTP email sent successfully to {to_address}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to_address}: {e}")
        return False