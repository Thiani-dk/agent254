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

# RQ / Redis imports for background email sending
from redis import Redis
from rq import Queue
from tasks import queue_send_email  # task that simply calls send_otp_email()

# Initialize Redis connection and RQ queue
redis_conn = Redis()  # adjust parameters if your Redis is not on localhost:6379
q = Queue(connection=redis_conn)

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return redirect(url_for("main.compose"))

@main_bp.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    if request.method == "POST":
        plaintext = request.form.get("plaintext", "").strip().encode("utf-8")
        recipient_email = request.form.get("recipient_email", "").strip().lower()
        expiry_seconds = int(request.form.get("expiry", "86400"))  # default 24h

        if not plaintext or not recipient_email:
            flash("Message and recipient email are required.", "error")
            return redirect(url_for("main.compose"))

        # Generate AES key + encrypt
        key = generate_aes_key()
        iv, ciphertext = encrypt_aes(plaintext, key)

        # Derive OTP
        salt = current_app.config["OTP_SALT"].encode("utf-8")
        otp_code = derive_otp(key, salt)

        # Unique Message ID
        message_id = binascii.hexlify(os.urandom(8)).decode("utf-8")

        # Set expiry timestamp
        expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)

        # Store in DB
        otp_hmac = derive_otp(key, salt)
        msg = Message(
            message_id=message_id,
            ciphertext=ciphertext,
            iv=iv,
            aes_key=key,
            otp_hash=otp_hmac,
            recipient_email=recipient_email,
            expires_at=expires_at
        )
        db.session.add(msg)
        db.session.commit()

        # Enqueue OTP‐email sending to a background worker (RQ)
        q.enqueue(queue_send_email, recipient_email, otp_code, expiry_seconds)

        # Render sent.html with OTP and expiry info
        return render_template(
            "sent.html",
            message_id=message_id,
            otp_code=otp_code,
            expiry_seconds=expiry_seconds
        )

    return render_template("compose.html")


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

        # Ensure the logged-in user is the intended recipient
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

        # Delete after retrieval
        db.session.delete(msg)
        db.session.commit()

        return render_template("result.html", plaintext=plaintext_bytes.decode("utf-8"))

    return render_template("retrieve.html")
