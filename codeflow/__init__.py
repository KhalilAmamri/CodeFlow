"""
Flask Application Factory

This module initializes the Flask app, configures extensions,
and sets up the application context for the CodeFlow learning platform.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
# flask_modals is incompatible with Flask 3.x in many cases.
# Import it optionally and provide a safe fallback when it's not available.
try:
    from flask_modals import Modal  # type: ignore
    _HAS_FLASK_MODALS = True
except Exception:
    Modal = None
    _HAS_FLASK_MODALS = False
from flask_mail import Mail
import os
from flask_admin import Admin

from codeflow.config import Config

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()
modals = Modal()
mail = Mail()
admin = Admin()

# Configure Flask-Login
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


def create_app():
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(Config)
    from codeflow.admin_bp.routes import MyAdminIndexView, MyModelView
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    modals.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app, index_view=MyAdminIndexView())
    # Import and register blueprints
    from codeflow.main.routes import main
    from codeflow.courses.routes import courses_bp
    from codeflow.lessons.routes import lessons
    from codeflow.users.routes import users
    from codeflow.errors.handlers import errors
    from codeflow.admin_bp.routes import admin_bp
    app.register_blueprint(main)
    app.register_blueprint(courses_bp)
    app.register_blueprint(lessons)
    app.register_blueprint(users)
    app.register_blueprint(errors)
    app.register_blueprint(admin_bp)
    return app