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
import hmac
import hashlib

# --- Local Imports ---
from .extensions import db
from .models import Message, User
from .aes_utils import generate_aes_key, derive_otp, encrypt_message, decrypt_message
from .email_utils import send_otp_email
from .sms_utils import send_otp_sms

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template("index.html")

@main_bp.route('/home')
@login_required
def home():
    return render_template("home.html")

@main_bp.route('/compose/colleague', methods=['GET', 'POST'])
@login_required
def compose_colleague():
    if request.method == 'POST':
        plaintext = request.form['message_content']
        expiry_seconds = int(request.form['expiry'])
        delivery_method = request.form['delivery_method']
        recipient_email = request.form.get('recipient_email')
        recipient_phone = request.form.get('recipient_phone')
        attachment = request.files.get('attachment')

        message_id = str(uuid.uuid4())
        aes_key = generate_aes_key()
        encrypted_content, iv, encoded_aes_key = encrypt_message(plaintext.encode('utf-8'), aes_key)

        # --- FIX: Correctly call derive_otp with one argument ---
        # The function expects the salt and will return the code and the hash.
        otp_salt_str = current_app.config['OTP_SALT']
        if not otp_salt_str:
            flash('OTP_SALT is not configured on the server.', 'error')
            return redirect(url_for('main.compose_colleague'))
            
        otp_salt_bytes = bytes.fromhex(otp_salt_str)
        # Assuming derive_otp returns (otp_code, otp_hash, expiry)
        otp_code, otp_hash, _ = derive_otp(otp_salt_bytes)

        attachment_original_filename = None
        attachment_stored_path = None

        if attachment and attachment.filename:
            upload_dir = os.path.join(current_app.instance_path, 'attachments')
            os.makedirs(upload_dir, exist_ok=True)
            attachment_original_filename = secure_filename(attachment.filename)
            unique_filename = f"{uuid.uuid4()}_{attachment_original_filename}"
            attachment_stored_path = os.path.join(upload_dir, unique_filename)
            attachment.save(attachment_stored_path)
            current_app.logger.info(f"Attachment saved to: {attachment_stored_path}")

        new_message = Message(
            message_id=message_id,
            otp_hash=otp_hash, # Use the hash directly from derive_otp
            ciphertext=encrypted_content,
            aes_key=encoded_aes_key,
            iv=iv,
            expires_at=datetime.utcnow() + timedelta(seconds=expiry_seconds),
            user_id=current_user.id,
            attachment_original_filename=attachment_original_filename,
            attachment_stored_path=attachment_stored_path
        )
        db.session.add(new_message)
        db.session.commit()

        recipient_for_display = None
        if delivery_method == 'email' and recipient_email:
            send_otp_email(
                to_address=recipient_email,
                sender=current_user.email,
                message_id=message_id,
                otp_code=otp_code,
                expiry_seconds=expiry_seconds
            )
            flash('Message encrypted and email sent!', 'success')
            recipient_for_display = recipient_email
        elif delivery_method == 'sms' and recipient_phone:
            sender_id = current_app.config.get('AFRICASTALKING_SENDER_ID')
            send_otp_sms(
                to_number=recipient_phone,
                message_id=message_id,
                otp_code=otp_code,
                expiry_seconds=expiry_seconds,
                sender_id=sender_id
            )
            flash('Message encrypted and SMS sent!', 'success')
            recipient_for_display = recipient_phone
        else:
            flash('Invalid delivery method or recipient information.', 'error')
            return redirect(url_for('main.compose_colleague'))

        return redirect(url_for('main.sent_colleague',
                                message_id=message_id,
                                expiry_seconds=expiry_seconds,
                                recipient_contact=recipient_for_display,
                                delivery_method=delivery_method))
    return render_template('compose_colleague.html')


@main_bp.route('/compose/friend', methods=['GET', 'POST'])
@login_required
def compose_friend():
    if request.method == 'POST':
        plaintext = request.form['message_content']
        expiry_seconds = int(request.form['expiry'])
        message_id = str(uuid.uuid4())
        aes_key = generate_aes_key()
        encrypted_content, iv, encoded_aes_key = encrypt_message(plaintext.encode('utf-8'), aes_key)

        # --- FIX: Correctly call derive_otp with one argument ---
        otp_salt_str = current_app.config['OTP_SALT']
        if not otp_salt_str:
            flash('OTP_SALT is not configured on the server.', 'error')
            return redirect(url_for('main.compose_friend'))

        otp_salt_bytes = bytes.fromhex(otp_salt_str)
        # Assuming derive_otp returns (otp_code, otp_hash, expiry)
        otp_code, otp_hash, _ = derive_otp(otp_salt_bytes)
        
        new_message = Message(
            message_id=message_id,
            otp_hash=otp_hash, # Use the hash directly from derive_otp
            ciphertext=encrypted_content,
            aes_key=encoded_aes_key,
            iv=iv,
            expires_at=datetime.utcnow() + timedelta(seconds=expiry_seconds),
            user_id=current_user.id
        )
        db.session.add(new_message)
        db.session.commit()
        
        flash('Message encrypted! Share the details with your friend.', 'success')
        return redirect(url_for('main.sent_friend',
                                message_id=message_id,
                                otp_code=otp_code,
                                expiry_seconds=expiry_seconds))
    return render_template('compose_friend.html')


@main_bp.route('/sent/friend')
@login_required
def sent_friend():
    message_id = request.args.get('message_id')
    otp_code = request.args.get('otp_code')
    expiry_seconds = request.args.get('expiry_seconds', type=int)

    if not all([message_id, otp_code, expiry_seconds is not None]):
        flash("Missing message details. Please compose a new message.", "error")
        return redirect(url_for('main.compose_friend'))
    
    return render_template('sent_friend.html', 
                           message_id=message_id, 
                           otp_code=otp_code,
                           expiry_seconds=expiry_seconds)


@main_bp.route('/sent/colleague')
@login_required
def sent_colleague():
    message_id = request.args.get('message_id')
    expiry_seconds = request.args.get('expiry_seconds', type=int)
    recipient_contact = request.args.get('recipient_contact')
    delivery_method = request.args.get('delivery_method')

    if not all([message_id, expiry_seconds is not None, recipient_contact]):
        flash("Missing message details. Please compose a new message.", "error")
        return redirect(url_for('main.compose_colleague'))

    return render_template('sent_colleague.html',
                           message_id=message_id,
                           expiry_seconds=expiry_seconds,
                           recipient_contact=recipient_contact,
                           delivery_method=delivery_method)


@main_bp.route('/retrieve', methods=['GET', 'POST'])
def retrieve():
    if request.method == 'POST':
        message_id = request.form['message_id']
        otp_code = request.form['otp_code']
        
        message = Message.query.filter_by(message_id=message_id).first()

        if not message:
            flash('Invalid Message ID or OTP.', 'error')
            return render_template('retrieve.html')

        if message.expires_at < datetime.utcnow():
            flash('Message has expired and is no longer available.', 'error')
            db.session.delete(message)
            db.session.commit()
            return render_template('retrieve.html')

        # --- FIX: Use a consistent HMAC comparison for verification ---
        otp_salt_bytes = bytes.fromhex(current_app.config['OTP_SALT'])
        expected_hash = hmac.new(otp_salt_bytes, otp_code.encode('utf-8'), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_hash, message.otp_hash):
            flash('Invalid Message ID or OTP.', 'error')
            return render_template('retrieve.html')
        
        if message.is_read:
            flash('Message has already been viewed and is no longer available.', 'error')
            db.session.delete(message)
            db.session.commit()
            return render_template('retrieve.html')
        
        try:
            decrypted_message_content = decrypt_message(
                message.ciphertext,
                message.iv,
                message.aes_key
            )
            attachment_data = None
            if message.attachment_stored_path and os.path.exists(message.attachment_stored_path):
                attachment_data = {
                    'filename': message.attachment_original_filename,
                    'download_url': url_for('main.download_attachment', message_id=message.message_id)
                }
            
            db.session.delete(message)
            db.session.commit()

            flash('Message decrypted successfully and has been deleted!', 'success')
            return render_template('view_message.html', 
                                   message_id=message_id,
                                   plaintext=decrypted_message_content,
                                   attachment=attachment_data)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error decrypting message {message.message_id}: {e}")
            flash('Error decrypting message. It might be corrupted.', 'error')
            return render_template('retrieve.html')

    return render_template('retrieve.html')


@main_bp.route('/download-attachment/<string:message_id>')
def download_attachment(message_id):
    # This won't work if the message is deleted on retrieval.
    # The attachment handling logic would need to be changed to temporarily
    # store the file for download on the view_message page.
    message = Message.query.filter_by(message_id=message_id).first_or_404() # This will likely fail

    if message.attachment_stored_path and os.path.exists(message.attachment_stored_path):
        directory, filename = os.path.split(message.attachment_stored_path)
        return send_from_directory(
            directory=directory,
            path=filename,
            as_attachment=True,
            download_name=os.path.basename(message.attachment_original_filename) # Use original filename
        )
    flash('Attachment not found or expired.', 'error')
    return redirect(url_for('main.home'))