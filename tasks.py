# tasks.py

  # careful: the function is `send_otp_email`
# Typo above: should be `send_otp_email`—fix below
from email_utils import send_otp_email


def queue_send_email(recipient_email: str, otp_code: str, expiry_seconds: int):
    """
    This function is invoked by an RQ worker. It simply calls
    send_otp_email(...) synchronously. Because the main Flask request
    enqueued this job, the email will be sent in a background worker.
    """
    send_otp_email(recipient_email, otp_code, expiry_seconds)
