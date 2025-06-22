import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY      = os.getenv("SECRET_KEY", "dev-key")
    OTP_SALT        = os.getenv("OTP_SALT", "change-this-salt")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///messages.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Comma-separated list, e.g. "strathmore.edu,acme.com"
    ALLOWED_ORGS = {d.strip() for d in os.getenv("ALLOWED_ORGS", "").split(",") if d.strip()}

    # SMTP settings...
    MAIL_SERVER   = os.getenv("MAIL_SERVER", "")
    MAIL_PORT     = int(os.getenv("MAIL_PORT", 0))
    MAIL_USE_TLS  = os.getenv("MAIL_USE_TLS", "false").lower() in ("1","true")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    BASE_URL      = os.getenv("BASE_URL", "http://localhost:5000")
