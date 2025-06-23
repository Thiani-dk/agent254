# auth.py
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        # --- FEATURE: PASSWORD CONTROLS ---

        # 1. Check if passwords match
        if password != password2:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for("auth.register"))

        # 2. Check for complexity
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for("auth.register"))
        if not re.search(r"[a-z]", password):
            flash("Password must contain at least one lowercase letter.", "error")
            return redirect(url_for("auth.register"))
        if not re.search(r"[A-Z]", password):
            flash("Password must contain at least one uppercase letter.", "error")
            return redirect(url_for("auth.register"))
        if not re.search(r"\d", password):
            flash("Password must contain at least one number.", "error")
            return redirect(url_for("auth.register"))
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash("Password must contain at least one special character.", "error")
            return redirect(url_for("auth.register"))
        
        # 3. Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email address is already registered.", "error")
            return redirect(url_for("auth.register"))

        # --- END OF PASSWORD CONTROLS ---

        # All checks passed, create user
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("login_register.html", form_type="register")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.home"))
            
        flash("Invalid email or password.", "error")
        return redirect(url_for("auth.login"))

    return render_template("login_register.html", form_type="login")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))