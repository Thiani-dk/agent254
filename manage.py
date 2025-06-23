# manage.py
import os
from app import create_app, db # Assuming create_app is in app.py and db in models.py
from flask_migrate import Migrate
from models import User, ColleagueEmail, Message # Import your models here

app = create_app()
migrate = Migrate(app, db)

# This block allows you to run Flask-Migrate commands
# For example: flask db init, flask db migrate, flask db upgrade
if __name__ == '__main__':
    app.run()