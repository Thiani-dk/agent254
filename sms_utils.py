# sms_utils.py

from flask import current_app

def send_otp_sms(to_number: str, otp_code: str) -> bool:
    """
    Stubbed OTP sender for development: logs the OTP instead of sending an actual SMS.
    """
    current_app.logger.info(f"[DEV OTP] To {to_number} → {otp_code}")
    return True
