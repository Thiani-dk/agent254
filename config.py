# config.py

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_to_a_random_string")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "messages.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP Settings (all come from environment variables below)
    MAIL_SERVER   = os.environ.get("MAIL_SERVER")       # e.g. "smtp.sendgrid.net"
    MAIL_PORT     = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")     # e.g. "apikey" for SendGrid
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")     # your actual API key or SMTP password
    MAIL_USE_TLS  = os.environ.get("MAIL_USE_TLS", "True") == "True"

    OTP_SALT = os.environ.get("OTP_SALT", "change_this_to_a_random_salt")
