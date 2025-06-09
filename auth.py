# auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("auth.register"))

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful—please log in.", "success")
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
            return redirect(next_page or url_for("main.compose"))
        flash("Invalid credentials.", "error")
        return redirect(url_for("auth.login"))

    return render_template("login_register.html", form_type="login")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
