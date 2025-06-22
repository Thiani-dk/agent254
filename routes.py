# routes.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, current_app
)
import os, binascii
from models import db, Message, ColleagueEmail
from aes_utils import generate_aes_key, encrypt_aes, decrypt_aes, derive_otp
from email_utils import send_otp_email
from datetime import datetime, timedelta
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")

#
# CHAT WITH FRIENDS
#
@main_bp.route("/compose/friend", methods=["GET", "POST"])
@login_required
def compose_friend():
    if request.method == "POST":
        plaintext = request.form.get("plaintext", "").strip().encode("utf-8")
        try:
            expiry_seconds = int(request.form.get("expiry", "86400"))
        except (ValueError, TypeError):
            expiry_seconds = 86400

        if not plaintext:
            flash("Message cannot be empty.", "error")
            return redirect(url_for("main.compose_friend"))

        key = generate_aes_key()
        iv, ciphertext = encrypt_aes(plaintext, key)
        salt = current_app.config["OTP_SALT"].encode("utf-8")
        otp_code = derive_otp(key, salt)
        message_id = binascii.hexlify(os.urandom(16)).decode("utf-8")

        new_message = Message(
            message_id=message_id,
            ciphertext=ciphertext,
            iv=iv,
            aes_key=key,
            auto_sent=False,
            expires_at=datetime.utcnow() + timedelta(seconds=expiry_seconds),
        )
        # Securely set the OTP hash
        new_message.set_otp(otp_code)

        db.session.add(new_message)
        db.session.commit()

        return render_template(
            "sent_friend.html",
            message_id=message_id,
            otp_code=otp_code,
            expiry_seconds=expiry_seconds,
        )

    return render_template("compose_friend.html")

#
# CHAT WITH COLLEAGUES
#
@main_bp.route("/compose/colleague", methods=["GET", "POST"])
@login_required
def compose_colleague():
    if request.method == "POST":
        plaintext = request.form.get("plaintext", "").strip().encode("utf-8")
        recipient_email = request.form.get("recipient_email", "").strip().lower()
        try:
            expiry_seconds = int(request.form.get("expiry", "86400"))
        except (ValueError, TypeError):
            expiry_seconds = 86400
            
        if not plaintext or not recipient_email:
            flash("Message and recipient email are required.", "error")
            return redirect(url_for("main.compose_colleague"))

        # --- BUG FIX: Domain Authorization ---
        # Ensure 'strathmore.edu' is always allowed for the demo, 
        # in addition to any domains specified in the .env file.
        domain = recipient_email.split("@")[-1]
        allowed_domains_from_env = current_app.config.get("ALLOWED_ORGS", set())
        # Add the default domain for the demo
        allowed_domains = allowed_domains_from_env.union({'strathmore.edu'})
        
        is_explicitly_allowed = ColleagueEmail.query.filter_by(email=recipient_email).first()

        if not is_explicitly_allowed and domain not in allowed_domains:
            flash(f"Messages to the '{domain}' domain are not permitted.", "error")
            return redirect(url_for("main.compose_colleague"))

        key = generate_aes_key()
        iv, ciphertext = encrypt_aes(plaintext, key)
        salt = current_app.config["OTP_SALT"].encode("utf-8")
        otp_code = derive_otp(key, salt)
        message_id = binascii.hexlify(os.urandom(16)).decode("utf-8")

        new_message = Message(
            message_id=message_id,
            ciphertext=ciphertext,
            iv=iv,
            aes_key=key,
            recipient_email=recipient_email,
            auto_sent=True,
            expires_at=datetime.utcnow() + timedelta(seconds=expiry_seconds),
        )
        # Securely set the OTP hash
        new_message.set_otp(otp_code)

        db.session.add(new_message)
        
        # Send Email
        email_sent = send_otp_email(
            to_address=recipient_email,
            message_id=message_id,
            otp_code=otp_code,
            expiry_seconds=expiry_seconds,
            sender=current_user.email,
            link=url_for("main.retrieve", _external=True),
        )

        if not email_sent:
            db.session.rollback()
            flash("Failed to send OTP email. Please check server configuration and try again.", "error")
            return redirect(url_for("main.compose_colleague"))

        db.session.commit()
        flash(f"Successfully sent encrypted message to {recipient_email}.", "success")
        return render_template(
            "sent_colleague.html",
            message_id=message_id,
            expiry_seconds=expiry_seconds,
            recipient_email=recipient_email
        )

    return render_template("compose_colleague.html")

#
# RETRIEVE MESSAGE (SHARED)
#
@main_bp.route("/retrieve", methods=["GET", "POST"])
@login_required
def retrieve():
    if request.method == "POST":
        message_id = request.form.get("message_id", "").strip()
        # Force OTP input to uppercase to match generation
        otp_input = request.form.get("otp", "").strip().upper()

        if not message_id or not otp_input:
            flash("Message ID and OTP are required.", "error")
            return redirect(url_for("main.retrieve"))

        msg = Message.query.filter_by(message_id=message_id).first()

        if not msg:
            flash("Invalid Message ID.", "error")
            return redirect(url_for("main.retrieve"))

        # Authorization check for colleague-sent messages
        if msg.auto_sent and msg.recipient_email.lower() != current_user.email.lower():
            flash("You are not authorized to retrieve this message.", "error")
            return redirect(url_for("main.retrieve"))
        
        if datetime.utcnow() > msg.expires_at:
            flash("This message has expired and been deleted.", "error")
            db.session.delete(msg)
            db.session.commit()
            return redirect(url_for("main.retrieve"))

        # Check the provided OTP against the stored hash
        if not msg.check_otp(otp_input):
            flash("Incorrect OTP.", "error")
            return redirect(url_for("main.retrieve"))

        try:
            plaintext_bytes = decrypt_aes(msg.iv, msg.ciphertext, msg.aes_key)
            plaintext = plaintext_bytes.decode("utf-8")
        except Exception:
            flash("Failed to decrypt message. The data may be corrupted.", "error")
            # Don't delete corrupted messages automatically, might need inspection
            return redirect(url_for("main.retrieve"))
        
        # Decryption successful, now delete the message
        db.session.delete(msg)
        db.session.commit()

        return render_template("result.html", plaintext=plaintext)

    return render_template("retrieve.html")