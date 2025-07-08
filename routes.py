# agent254/routes.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    current_app, send_from_directory
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
import zipfile
import tempfile
import shutil
from datetime import datetime, timedelta

# --- Local Imports ---
from .extensions import db
from .models import Message, User
from .aes_utils import generate_aes_key, derive_otp, encrypt_message, decrypt_message
from .email_utils import send_otp_email
from .sms_utils import send_otp_sms

main_bp = Blueprint('main', __name__)

# --- Add Home and other basic routes if they are not elsewhere ---
@main_bp.route('/')
def index():
    return render_template("index.html") # Or redirect to login/home

@main_bp.route('/home')
@login_required
def home():
    return render_template("home.html") # Your main dashboard after login

# This is your main message composition logic
@main_bp.route('/compose/colleague', methods=['GET', 'POST'])
@login_required
def compose_colleague():
    if request.method == 'POST':
        temp_dir = None
        try:
            # --- Get Form Data ---
            delivery_method = request.form.get('delivery_method')
            recipient_contact = (request.form.get('recipient_email') if delivery_method == 'email' 
                                 else request.form.get('recipient_phone', '')).strip().lower()
            plaintext = request.form.get('plaintext', '').strip()
            expiry_seconds = int(request.form.get('expiry', '3600')) # Default 1 hour
            attachment = request.files.get('attachment')

            # --- Validation ---
            if not all([delivery_method, recipient_contact, plaintext]):
                flash('Please fill out all required fields.', 'warning')
                return redirect(url_for('main.compose_colleague'))
            
            salt_bytes = current_app.config["OTP_SALT"].encode("utf-8")

            # --- Encryption and OTP ---
            aes_key = generate_aes_key() # Binary key
            otp_code = derive_otp(aes_key, salt_bytes)
            encoded_ciphertext, iv, encoded_aes_key = encrypt_message(plaintext.encode('utf-8'), aes_key)

            # --- Handle Attachment ---
            attachment_zip_path = None
            original_filename = None
            if attachment and attachment.filename:
                original_filename = secure_filename(attachment.filename)
                temp_dir = tempfile.mkdtemp()
                saved_filepath = os.path.join(temp_dir, original_filename)
                attachment.save(saved_filepath)
                
                zip_filename = f"{os.path.splitext(original_filename)[0]}.zip"
                attachment_zip_path = os.path.join(temp_dir, zip_filename)
                with zipfile.ZipFile(attachment_zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
                    z.write(saved_filepath, original_filename)

            # --- Create Database Record ---
            new_message = Message(
                ciphertext=encoded_ciphertext,
                iv=iv,
                aes_key=encoded_aes_key,
                expires_at=datetime.utcnow() + timedelta(seconds=expiry_seconds),
                user_id=current_user.id
            )
            new_message.set_otp(otp_code, salt_bytes)
            db.session.add(new_message)
            db.session.flush() # Flush to get the new_message.id

            # --- Conditional Delivery ---
            delivery_successful = False
            if delivery_method == 'email':
                delivery_successful = send_otp_email(
                    to_address=recipient_contact,
                    message_id=new_message.message_id,
                    otp_code=otp_code,
                    expiry_seconds=expiry_seconds,
                    sender=current_user.email,
                    attachment_path=attachment_zip_path
                )
            elif delivery_method == 'sms':
                delivery_successful = send_otp_sms(
                    recipient_phone_number=recipient_contact,
                    otp=otp_code,
                    message_id=new_message.message_id
                )

            # --- Finalize Transaction ---
            if delivery_successful:
                db.session.commit()
                flash(f'Encrypted message sent successfully via {delivery_method.upper()}!', 'success')
                return redirect(url_for('main.home'))
            else:
                db.session.rollback() # Rollback if sending failed
                flash(f'Failed to send message via {delivery_method}. Please check your configuration.', 'error')
                return redirect(url_for('main.compose_colleague'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Fatal error in compose_colleague: {e}")
            flash('An unexpected server error occurred. Please try again.', 'danger')
            return redirect(url_for('main.compose_colleague'))
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    return render_template('compose_colleague.html')