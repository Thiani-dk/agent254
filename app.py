# app.py
from flask import Flask
from config import Config
from datetime import datetime
from flask_bcrypt import Bcrypt

# Instantiate Bcrypt here to be available for the app
bcrypt = Bcrypt()

from models import db, User
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------- INITIALIZE EXTENSIONS ----------
    db.init_app(app)
    bcrypt.init_app(app)

    # ---------- LOGIN MANAGER ----------
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "error"
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---------- GLOBAL CONTEXT ----------
    @app.context_processor
    def inject_globals():
        ctx = {"current_year": datetime.utcnow().year}
        
        # Unread badge counter for colleague flow
        from flask_login import current_user
        from models import Message
        if current_user.is_authenticated:
            unread_count = Message.query.filter(
                Message.recipient_email == current_user.email,
                Message.expires_at > datetime.utcnow()
            ).count()
            ctx["unread_count"] = unread_count
        else:
            ctx["unread_count"] = 0
            
        return ctx

    # ---------- BLUEPRINTS ----------
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes import main_bp
    app.register_blueprint(main_bp)

    return app