# routes.py

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, current_app
)
import os, binascii
from models import db, Message
from aes_utils import generate_aes_key, encrypt_aes, decrypt_aes, derive_otp
from email_utils import send_otp_email
from datetime import datetime, timedelta
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__, template_folder="templates")
@main_bp.route("/")
def home():
    # Render a choice page with two buttons
    return render_template("home.html")
#
# 1) Chat-with-Friends: no automated email
#
@main_bp.route("/compose/friend", methods=["GET", "POST"])
@login_required
def compose_friend():
    if request.method == "POST":
        plaintext = request.form.get("plaintext", "").strip().encode("utf-8")
        expiry_seconds = int(request.form.get("expiry", "86400"))  # default 24h

        if not plaintext:
            flash("Message cannot be empty.", "error")
            return redirect(url_for("main.compose_friend"))

        # Generate AES key & encrypt
        key = generate_aes_key()
        iv, ciphertext = encrypt_aes(plaintext, key)

        # Derive OTP
        salt = current_app.config["OTP_SALT"].encode("utf-8")
        otp_code = derive_otp(key, salt)

        # Unique Message ID
        message_id = binascii.hexlify(os.urandom(8)).decode("utf-8")

        # Expiry timestamp
        expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)

        # Save in DB, auto_sent=False (friend flow)
        otp_hmac = derive_otp(key, salt)
        msg = Message(
            message_id=message_id,
            ciphertext=ciphertext,
            iv=iv,
            aes_key=key,
            otp_hash=otp_hmac,
            recipient_email=current_user.email,  # store the sender’s own email for reference
            auto_sent=False,
            expires_at=expires_at
        )
        db.session.add(msg)
        db.session.commit()

        # Render a “sent_friend” page where we display OTP + Message ID + retrieve link
        return render_template(
            "sent_friend.html",
            message_id=message_id,
            otp_code=otp_code,
            expiry_seconds=expiry_seconds
        )

    return render_template("compose_friend.html")


#
# 2) Chat-with-Colleagues: automated email
#
@main_bp.route("/compose/colleague", methods=["GET", "POST"])
@login_required
def compose_colleague():
    if request.method == "POST":
        plaintext = request.form.get("plaintext", "").strip().encode("utf-8")
        recipient_email = request.form.get("recipient_email", "").strip().lower()
        expiry_seconds = int(request.form.get("expiry", "86400"))

        if not plaintext or not recipient_email:
            flash("Message and recipient email are required.", "error")
            return redirect(url_for("main.compose_colleague"))

        # ─── Domain enforcement for colleagues ────────────────────────────────
        # Only auto-email if both sender and recipient share the @strathmore.edu domain
        sender = current_user.email.lower()
        if not (sender.endswith("@strathmore.edu") and recipient_email.endswith("@strathmore.edu")):
            flash("Colleague flow requires both emails end in @strathmore.edu.", "error")
            return redirect(url_for("main.compose_colleague"))
        # ─────────────────────────────────────────────────────────────────────

        # Generate AES key & encrypt
        key = generate_aes_key()
        iv, ciphertext = encrypt_aes(plaintext, key)

        # Derive OTP
        salt = current_app.config["OTP_SALT"].encode("utf-8")
        otp_code = derive_otp(key, salt)

        # Unique Message ID
        message_id = binascii.hexlify(os.urandom(8)).decode("utf-8")

        # Expiry timestamp
        expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)

        # Save in DB, auto_sent=True
        otp_hmac = derive_otp(key, salt)
        msg = Message(
            message_id=message_id,
            ciphertext=ciphertext,
            iv=iv,
            aes_key=key,
            otp_hash=otp_hmac,
            recipient_email=recipient_email,
            auto_sent=True,
            expires_at=expires_at
        )
        db.session.add(msg)
        db.session.commit()

        # Send OTP email synchronously
        # Send OTP via email
        success = send_otp_email(
            recipient_email,
            otp_code,
            expiry_seconds,
            sender_email=sender
        )
        
        if not send_success:
            flash("Failed to send OTP email. Please try again.", "error")
            # Roll back the DB entry so coworker cannot retrieve
            db.session.delete(msg)
            db.session.commit()
            return redirect(url_for("main.compose_colleague"))

        # Render “sent_colleague.html” confirming on-screen
        return render_template(
            "sent_colleague.html",
            message_id=message_id,
            otp_code=otp_code,
            expiry_seconds=expiry_seconds,
            recipient_email=recipient_email
        )

    return render_template("compose_colleague.html")


#
# 3) Common “Retrieve” page (for both flows)
#
@main_bp.route("/retrieve", methods=["GET", "POST"])
@login_required
def retrieve():
    if request.method == "POST":
        message_id = request.form.get("message_id", "").strip()
        otp_input = request.form.get("otp", "").strip()

        if not message_id or not otp_input:
            flash("Message ID and OTP are required.", "error")
            return redirect(url_for("main.retrieve"))

        msg = Message.query.filter_by(message_id=message_id).first()
        if not msg:
            flash("Invalid Message ID.", "error")
            return redirect(url_for("main.retrieve"))

        # If this was a colleague-flow, ensure the logged-in user is intended recipient
        if msg.auto_sent:
            if msg.recipient_email.lower() != current_user.email.lower():
                flash("You are not authorized to retrieve this message.", "error")
                return redirect(url_for("main.retrieve"))

        # Check expiry
        now = datetime.utcnow()
        if msg.expires_at and now > msg.expires_at:
            flash("This message has expired.", "error")
            db.session.delete(msg)
            db.session.commit()
            return redirect(url_for("main.retrieve"))

        # Verify OTP
        if otp_input != msg.otp_hash:
            flash("Incorrect OTP.", "error")
            return redirect(url_for("main.retrieve"))

        # Decrypt
        try:
            plaintext_bytes = decrypt_aes(msg.iv, msg.ciphertext, msg.aes_key)
        except Exception:
            flash("Failed to decrypt. Data may be corrupted.", "error")
            return redirect(url_for("main.retrieve"))

        # On successful retrieval, delete it so it cannot be used again
        db.session.delete(msg)
        db.session.commit()

        return render_template("result.html", plaintext=plaintext_bytes.decode("utf-8"))

    return render_template("retrieve.html")
