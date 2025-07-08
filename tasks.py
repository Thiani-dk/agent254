# tasks.py
from .email_utils import send_otp_email
from flask import current_app

def queue_send_email(
    *,
    recipient_email: str,
    sender_email: str,
    message_id: str,
    otp_code: str,
    expiry_seconds: int
):
    """
    This function is invoked by an RQ worker. It calls send_otp_email
    to send the email in a background worker.
    """
    # This call now correctly matches the signature of the send_otp_email function
    send_otp_email(
        to_address=recipient_email,
        sender=sender_email,
        message_id=message_id,
        otp_code=otp_code,
        expiry_seconds=expiry_seconds
    )