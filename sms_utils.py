# agent254/sms_utils.py
import africastalking
from flask import current_app

def init_africastalking_sdk():
    """Initializes the AfricasTalking SDK from app config."""
    username = current_app.config.get('AFRICASTALKING_USERNAME')
    api_key = current_app.config.get('AFRICASTALKING_API_KEY')
    
    if not username or not api_key:
        current_app.logger.warning("AfricasTalking credentials not found. SMS functionality will be disabled.")
        return

    try:
        africastalking.initialize(username, api_key)
        current_app.logger.info("AfricasTalking SDK initialized successfully.")
    except Exception as e:
        current_app.logger.error(f"Failed to initialize AfricasTalking SDK: {e}")

def send_otp_sms(recipient_phone_number: str, otp: str, message_id: str):
    """Sends an OTP and Message ID via SMS using AfricasTalking."""
    if not current_app.config.get('AFRICASTALKING_USERNAME'):
         current_app.logger.error("Cannot send SMS: AfricasTalking SDK not initialized.")
         return False
         
    try:
        sms = africastalking.SMS
        sender_id = current_app.config.get('AFRICASTALKING_SENDER_ID') or None

        base_url = current_app.config.get('BASE_URL', '')
        retrieve_link = f"{base_url}/retrieve"

        message_body = (
            f"Your Agent254 OTP is: {otp}. "
            f"Message ID: {message_id}. "
            f"Use link to retrieve: {retrieve_link}"
        )

        # The send method expects a list of numbers
        response = sms.send(message_body, [recipient_phone_number], sender_id)
        
        current_app.logger.info(f"SMS sent successfully to {recipient_phone_number}: {response}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS to {recipient_phone_number}: {e}")
        return False

