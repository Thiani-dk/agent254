# app.py

from flask import Flask
from config import Config
from datetime import datetime

# Import the single shared SQLAlchemy instance defined in models.py
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register that single db instance to this Flask app
    db.init_app(app)

    @app.context_processor
    def inject_current_year():
        return {"current_year": datetime.utcnow().year}

    # Now that db.init_app(app) has been called, import and register your routes
    from routes import main_bp
    app.register_blueprint(main_bp)

    return app

# Expose a module‐level `app` so that Gunicorn can find it
app = create_app()

if __name__ == "__main__":
    # When you run `python app.py`, this will run Flask’s built‐in server.
    app.run(debug=True)
