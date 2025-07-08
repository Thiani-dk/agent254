# agent254/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    OTP_SALT = os.getenv('OTP_SALT')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'messages.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:5000')

    # Mail Server Configurations
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # --- NEW: AfricasTalking SMS API Credentials ---
    AFRICASTALKING_USERNAME = os.getenv("AFRICASTALKING_USERNAME")
    AFRICASTALKING_API_KEY = os.getenv("AFRICASTALKING_API_KEY")
    AFRICASTALKING_SENDER_ID = os.getenv("AFRICASTALKING_SENDER_ID") # Can be blank
