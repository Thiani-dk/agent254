# agent254/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .extensions import db, bcrypt
from .models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Basic validation for empty fields
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            # Re-render the form to show the error and potentially keep other fields populated
            return render_template('login_register.html', form_type='register', 
                                   username=username, email=email)

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('login_register.html', form_type='register', 
                                   email=email) # Keep email if valid

        # Check if email already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login or use a different email.', 'error')
            return render_template('login_register.html', form_type='register', 
                                   username=username) # Keep username if valid

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback() # Rollback the transaction on error
            flash(f'Error creating account: {e}', 'error')
            current_app.logger.error(f"Error creating user: {e}") # Log the error
            return render_template('login_register.html', form_type='register', 
                                   username=username, email=email)

    return render_template('login_register.html', form_type='register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            # Redirect to 'next' URL if available, otherwise to home
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'error')
            # Re-render the form to show the error and keep the email populated
            return render_template('login_register.html', form_type='login', email=email)

    return render_template('login_register.html', form_type='login')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))