"""
Flask Application Factory

This module initializes the Flask app, configures extensions,
and sets up the application context for the Pythonic learning platform.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_modals import Modal
from flask_mail import Mail
import os

from pythonic.config import Config

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate(db)
login_manager = LoginManager()
modals = Modal()
mail = Mail()

# Configure Flask-Login
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


def create_app():
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    modals.init_app(app)
    mail.init_app(app)
    
    # Import and register blueprints
    from pythonic.main.routes import main
    from pythonic.courses.routes import courses_bp
    from pythonic.lessons.routes import lessons
    from pythonic.users.routes import users

    app.register_blueprint(main)
    app.register_blueprint(courses_bp)
    app.register_blueprint(lessons)
    app.register_blueprint(users)

    return app