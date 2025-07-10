# agent254/app.py
import logging # Added for logging level
import africastalking # Corrected import for Africa's Talking SDK initialization
from dotenv import load_dotenv # Import load_dotenv
load_dotenv() # Call load_dotenv() at the very top to load .env variables

from flask import Flask
from .extensions import db, bcrypt, login_manager, mail
from .routes import main_bp
from .auth import auth_bp
from .config import Config
from .models import User
from flask_migrate import Migrate

import os

def init_sms_sdk(app: Flask):
    """
    Initializes the Africa's Talking SDK with credentials from Flask's config.
    This function is called once during app startup.
    """
    try:
        africastalking.initialize( # Corrected call
            username=app.config['AFRICASTALKING_USERNAME'],
            api_key=app.config['AFRICASTALKING_API_KEY']
        )
        app.logger.info("✅ Africa’s Talking SDK initialized successfully.")
    except KeyError as e:
        app.logger.error(f"❌ Africa's Talking credentials missing from config: {e}. SMS functionality will be limited.")
    except Exception as e:
        app.logger.error(f"❌ Failed to initialize Africa's Talking SDK: {e}")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set Flask logger level so info messages show up
    app.logger.setLevel(logging.INFO)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Initialize Africa's Talking SDK within the app context
    with app.app_context():
        init_sms_sdk(app)

    migrate = Migrate(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app

app = create_app()
