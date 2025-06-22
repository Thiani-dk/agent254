# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Use a separate bcrypt instance for the application logic if needed,
# or just use the functions directly.
from app import bcrypt

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw).decode('utf-8')
        
    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

class ColleagueEmail(db.Model):
    __tablename__ = "colleague_emails"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(64), unique=True, nullable=False)
    ciphertext = db.Column(db.LargeBinary, nullable=False)
    iv = db.Column(db.LargeBinary(16), nullable=False)
    
    # --- VULNERABILITY NOTE ---
    # Storing the raw AES key, even in a database, is a major security risk.
    # If the database is compromised, all messages can be decrypted.
    # In a production system, this key should itself be encrypted using a master key
    # (a pattern called "envelope encryption"). For this project, we accept the risk
    # but acknowledge it's not industry-standard practice.
    aes_key = db.Column(db.LargeBinary(32), nullable=False)
    
    # --- SECURITY IMPROVEMENT ---
    # Store a HASH of the OTP, not the plaintext OTP.
    otp_hash = db.Column(db.String(128), nullable=False)

    recipient_email = db.Column(db.String(120), nullable=True) # Null for friend flow
    auto_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def set_otp(self, otp_plaintext: str):
        """Hashes the OTP before storing."""
        self.otp_hash = bcrypt.generate_password_hash(otp_plaintext).decode('utf-8')

    def check_otp(self, otp_plaintext: str) -> bool:
        """Checks a plaintext OTP against the stored hash."""
        return bcrypt.check_password_hash(self.otp_hash, otp_plaintext)