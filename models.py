# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash

# Single shared SQLAlchemy instance
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, raw_password: str):
        # generate_password_hash returns a bytes object; decode to utf-8
        self.password_hash = generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(64), unique=True, nullable=False)
    ciphertext = db.Column(db.LargeBinary, nullable=False)
    iv = db.Column(db.LargeBinary(16), nullable=False)
    aes_key = db.Column(db.LargeBinary(32), nullable=False)   # raw AES key
    otp_hash = db.Column(db.String(64), nullable=False)       # HMAC–SHA256 hex
    recipient_email = db.Column(db.String(120), nullable=False)
    auto_sent = db.Column(db.Boolean, default=False)          # True → “colleague” flow
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Message {self.message_id}>"
