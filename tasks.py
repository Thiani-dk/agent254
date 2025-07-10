# agent254/tasks.py
from flask import current_app
from .email_utils import send_otp_email
from .sms_utils import send_otp_sms

def queue_send_email(to_address: str, sender: str, message_id: str, otp_code: str, expiry_seconds: int, attachment_path: str = None):
    """This function is invoked by an RQ worker to send an email."""
    # The app context is necessary for url_for and current_app.config
    with current_app.app_context():
        send_otp_email(
            to_address=to_address,
            sender=sender,
            message_id=message_id,
            otp_code=otp_code,
            expiry_seconds=expiry_seconds,
            attachment_path=attachment_path
        )

def queue_send_sms(to_number: str, message_id: str, otp_code: str, expiry_seconds: int):
    """This function is invoked by an RQ worker to send an SMS."""
    # The app context is necessary for url_for and current_app.config
    with current_app.app_context():
        send_otp_sms(
            to_number=to_number,
            message_id=message_id,
            otp_code=otp_code,
            sender_id=current_app.config.get('AFRICASTALKING_SENDER_ID'),
            expiry_seconds=expiry_seconds
        )