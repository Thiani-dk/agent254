# app.py
from flask import Flask
from .extensions import db, bcrypt, login_manager, mail
from .routes import main_bp
from .auth import auth_bp
from .config import Config
from .models import User
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    migrate = Migrate(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app

# This line is crucial for Flask-CLI commands like `flask db`
app = create_app()