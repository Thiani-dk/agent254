# config.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from a .env file (in project root)
basedir = Path(__file__).resolve().parent
load_dotenv(basedir / ".env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_to_a_random_string")
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(basedir, "messages.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login
    # (no explicit config needed here; just will initialize LoginManager in app.py)

    # SMTP / Email configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ("true", "1", "yes")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")  # your SMTP username (e.g. app-specific Gmail address)
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")  # your SMTP password or app-password

    # OTP salt
    OTP_SALT = os.environ.get("OTP_SALT", "change_this_to_a_random_salt")
