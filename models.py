# agent254/models.py
from .extensions import db, bcrypt
from datetime import datetime
from flask_login import UserMixin
import uuid
import hmac
import hashlib

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    # Added username to match the registration form in auth.py
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Renamed to password for consistency with auth.py
    password = db.Column(db.String(128), nullable=False)

    # Note: Flask-Login uses the 'password' attribute.
    # The original file had a mismatch between 'password' and 'password_hash'.
    # I've consolidated them to 'password' to work with your auth.py file.

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # This column stores the hashed OTP
    otp_hash = db.Column(db.String(128), nullable=False)
    
    # Encrypted data columns
    ciphertext = db.Column(db.Text, nullable=False)
    aes_key = db.Column(db.String(64), nullable=False) # Base64 of 32-byte key
    iv = db.Column(db.LargeBinary(16), nullable=False)
    
    # Metadata columns
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_read = db.Column(db.Boolean, default=False)
    
    # Columns for file attachments
    attachment_original_filename = db.Column(db.String(255), nullable=True)
    attachment_stored_path = db.Column(db.String(255), nullable=True)
    
    def set_otp(self, otp_code, salt_bytes):
        """Hashes the OTP code using HMAC-SHA256 for secure storage."""
        self.otp_hash = hmac.new(salt_bytes, otp_code.encode('utf-8'), hashlib.sha256).hexdigest()

    def check_otp(self, otp_code, salt_bytes):
        """Checks if the provided OTP matches the securely stored hash."""
        expected_hash = hmac.new(salt_bytes, otp_code.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(self.otp_hash, expected_hash)