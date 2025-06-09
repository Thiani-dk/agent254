# email_utils.py

import smtplib
from email.mime.text import MIMEText
from flask import current_app

def send_otp_email(recipient: str, otp_code: str, expiry_seconds: int) -> bool:
    """
    Sends the OTP to the recipient via SMTP.
    Expects these env configs in Flask:
      MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_USE_TLS
    """
    mail_server = current_app.config.get("MAIL_SERVER")
    mail_port   = current_app.config.get("MAIL_PORT")
    mail_user   = current_app.config.get("MAIL_USERNAME")
    mail_pass   = current_app.config.get("MAIL_PASSWORD")
    use_tls     = current_app.config.get("MAIL_USE_TLS", True)

    subject = "Your Agent254 OTP Code"
    body = (
        f"Hello,\n\n"
        f"Your OTP for decrypting a message is:\n\n"
        f"    {otp_code}\n\n"
        f"This code expires in {expiry_seconds} seconds and can only be used once.\n\n"
        f"- Agent254 Secure Messaging"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = mail_user
    msg["To"] = recipient

    try:
        server = smtplib.SMTP(mail_server, mail_port)
        if use_tls:
            server.starttls()
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, [recipient], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email OTP: {e}")
        return False
