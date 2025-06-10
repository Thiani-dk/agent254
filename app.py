# app.py

from flask import Flask
from flask_login import LoginManager, current_user
from config import Config
from datetime import datetime
from models import db, User, Message

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Context processor: inject current_year and unread_count (only for auto_sent=True)
    @app.context_processor
    def inject_globals():
        now = datetime.utcnow()
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = (
                Message.query
                .filter_by(recipient_email=current_user.email, auto_sent=True)
                .filter(Message.expires_at > now)
                .count()
            )
        return {
            "current_year": now.year,
            "unread_count": unread_count
        }

    # Register blueprints
    from auth import auth_bp
    from routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

# expose module-level `app` for gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
