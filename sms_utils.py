# agent254/sms_utils.py
import africastalking
from flask import current_app

def send_otp_sms(to_number, message_id, otp_code, expiry_seconds, sender_id=None):
    """
    Sends an OTP via SMS using the Africa's Talking gateway.
    Assumes Africa's Talking SDK has already been initialized in app.py.
    """
    try:
        sms = africastalking.SMS # Access the SMS service from the initialized SDK
        
        base_url = current_app.config.get('BASE_URL', 'http://127.0.0.1:5000')
        retrieval_url = f"{base_url}/retrieve"
        
        expiry_minutes = expiry_seconds // 60
        message = (
            f"You have a secure message.\n"
            f"Go to: {retrieval_url}\n"
            f"Message ID: {message_id}\n"
            f"OTP: {otp_code}\n"
            f"This code expires in {expiry_minutes} minutes."
        )

        recipients = [to_number]
        
        current_app.logger.info(f"📨 Attempting to send SMS to {to_number} (sender will be Africa's Talking default)")
        
        # KEY CHANGE: Omit the sender_id parameter from the sms.send call
        response = sms.send(message, recipients) 
        
        # Log the full response object from Africa's Talking
        current_app.logger.info("📬 Africa’s Talking SMS response: %s", response)
        
        return response

    except africastalking.Service.AfricasTalkingException as e:
        current_app.logger.error("❌ Failed to send SMS via Africa’s Talking: %s", e)
        raise e
    except Exception as e:
        current_app.logger.error("❌ An unexpected error occurred during SMS sending: %s", e)
        raise e
