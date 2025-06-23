import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY              = os.getenv("SECRET_KEY", "dev-key")
    OTP_SALT                = os.getenv("OTP_SALT", "change-this-salt")

    # IMPORTANT: Ensure DATABASE_URL is set on Render to your PostgreSQL URI.
    # Otherwise, it will fallback to SQLite, causing 'no such table' errors.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///messages.db") # Keep fallback for local dev if needed
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Recommended for external databases like PostgreSQL on Render
    SQLALCHEMY_POOL_RECYCLE = 3600  # Recycle connections after 1 hour (3600 seconds)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Test connections before use
    }

    # Comma-separated list, e.g. "strathmore.edu,acme.com"
    ALLOWED_ORGS = {d.strip() for d in os.getenv("ALLOWED_ORGS", "").split(",") if d.strip()}

    # SMTP settings...
    MAIL_SERVER   = os.getenv("MAIL_SERVER", "")
    MAIL_PORT     = int(os.getenv("MAIL_PORT", 0))
    MAIL_USE_TLS  = os.getenv("MAIL_USE_TLS", "false").lower() in ("1","true")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    BASE_URL      = os.getenv("BASE_URL", "http://localhost:5000")