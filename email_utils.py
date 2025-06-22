# email_utils.py
from datetime import datetime

import smtplib
from email.message import EmailMessage
import os
from flask import current_app

def send_otp_email(
    *,
    to_address: str,
    message_id: str,
    otp_code: str,
    expiry_seconds: int,
    sender: str = None,
    link: str = None
) -> bool:
    """
    Sends a formatted HTML email via SMTP (credentials from env).
    """
    cfg = {
        "host": os.getenv("MAIL_SERVER"),
        "port": int(os.getenv("MAIL_PORT", 587)),
        "username": os.getenv("MAIL_USERNAME"),
        "password": os.getenv("MAIL_PASSWORD"),
        "use_tls": os.getenv("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes"),
    }

    if not all([cfg["host"], cfg["port"], cfg["username"], cfg["password"]]):
        current_app.logger.error("Email configuration is incomplete. Cannot send email.")
        return False

    msg = EmailMessage()
    msg["From"] = f"Agent254 Secure Messaging <{cfg['username']}>"
    msg["To"] = to_address
    msg["Subject"] = f"A Secure Message was sent to you from {sender}"
    if sender:
        msg["Reply-To"] = sender

    # Create the beautiful HTML body
    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Message Notification</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f7f6; color: #333;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td align="center">
                <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                    <tr>
                        <td align="center" style="padding: 20px; background-color: #0d6efd; color: #ffffff;">
                            <h1 style="margin: 0; font-size: 24px;">Agent254</h1>
                            <p style="margin: 5px 0 0; font-size: 16px;">Secure Message Notification</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px;">
                            <h2 style="font-size: 20px; color: #333;">You've Received a Secure Message</h2>
                            <p style="font-size: 16px; line-height: 1.6;">
                                You have received a secure, encrypted message from <strong>{sender or 'an Agent254 user'}</strong>.
                                For your security, the message content is never sent via email.
                            </p>
                            <p style="font-size: 16px; line-height: 1.6;">
                                To view your message, you will need the following credentials:
                            </p>
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 20px 0; border: 1px dashed #cccccc; padding: 15px; border-radius: 5px;">
                                <tr>
                                    <td style="font-size: 16px;"><strong>Message ID:</strong></td>
                                    <td style="font-size: 16px; font-family: 'Courier New', Courier, monospace; background-color: #f0f0f0; padding: 5px 10px; border-radius: 4px;">{message_id}</td>
                                </tr>
                                <tr><td style="height: 10px;"></td></tr>
                                <tr>
                                    <td style="font-size: 16px;"><strong>One-Time Password (OTP):</strong></td>
                                    <td style="font-size: 16px; font-family: 'Courier New', Courier, monospace; background-color: #f0f0f0; padding: 5px 10px; border-radius: 4px;">{otp_code}</td>
                                </tr>
                            </table>
                            <p align="center" style="margin: 30px 0;">
                                <a href="{link}" target="_blank" style="background-color: #0d6efd; color: #ffffff; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">Decrypt & View Message</a>
                            </p>
                            <p style="font-size: 14px; color: #888; text-align: center;">
                                This link and OTP will expire in approximately {expiry_seconds // 60} minutes.
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 20px; text-align: center; background-color: #f4f7f6; font-size: 12px; color: #888;">
                            <p style="margin: 0;">If you were not expecting this message, please disregard this email.</p>
                            <p style="margin: 5px 0 0;">&copy; {datetime.now().year} Agent254. All Rights Reserved.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    msg.set_content("A secure message has been sent to you. Please use an HTML-compatible email client to view the instructions.")
    msg.add_alternative(html_body, subtype="html")

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