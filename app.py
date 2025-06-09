# app.py

from flask import Flask
from config import Config
from datetime import datetime

from models import db, User, Message
from flask_login import LoginManager, current_user

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize the single db instance with the app
    db.init_app(app)

    # Configure LoginManager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_current_year_and_unread():
        data = {"current_year": datetime.utcnow().year}
        # If user is authenticated, count unread messages for them
        if current_user.is_authenticated:
            count = Message.query.filter_by(recipient_email=current_user.email).count()
        else:
            count = 0
        data["unread_count"] = count
        return data

    # Register blueprints
    from auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from routes import main_bp
    app.register_blueprint(main_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
