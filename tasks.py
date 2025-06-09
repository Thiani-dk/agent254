# tasks.py

from email_utils import send_otp_email

def queue_send_email(recipient_email, otp_code, expiry_seconds):
    # Called by RQ worker
    send_otp_email(recipient_email, otp_code, expiry_seconds)
