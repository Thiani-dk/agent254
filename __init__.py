# agent254/__init__.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt # Assuming you are using Flask-Bcrypt

# Initialize extensions outside of create_app
# They are initialized here without an app instance,
# and will be bound to the app later in create_app using .init_app(app)
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Configure login manager
login_manager.login_view = 'auth.login' # Assuming 'auth' blueprint for login
login_manager.login_message_category = 'info'

# This function will be defined in app.py
# You don't usually define create_app in __init__.py if you have a separate app.py
# If you *do* define create_app here, then the db, login_manager, bcrypt
# would be initialized within that function, and then imported from __init__.py
# For your current structure, where app.py has create_app, keep it like this:
# from .app import create_app # If you were importing create_app from app.py into __init__.py, which is less common.
