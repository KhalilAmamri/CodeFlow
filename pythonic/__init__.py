# ============================================================================
# FLASK APPLICATION FACTORY AND CONFIGURATION
# ============================================================================
# This module serves as the application factory, initializing the Flask app,
# configuring extensions, and setting up the application context for the
# Pythonic learning platform.

# Flask core framework import for web application creation
from flask import Flask

# Database ORM integration for SQL database operations
from flask_sqlalchemy import SQLAlchemy

# Password hashing and security for user authentication
from flask_bcrypt import Bcrypt

# User session management and authentication state
from flask_login import LoginManager

# Database migration management for schema evolution
from flask_migrate import Migrate

# Modal dialog functionality for enhanced user interface
from flask_modals import Modal

# Email functionality for password reset
from flask_mail import Mail

# Environment variable for email credentials
import os
# Config import for environment variables
from pythonic.config import Config

# ============================================================================
# FLASK APPLICATION INSTANCE CREATION
# ============================================================================

# Create the main Flask application instance
# __name__ represents the current Python module name
app = Flask(__name__)

app.config.from_object(Config)

# Initialize SQLAlchemy database instance
# This provides ORM functionality and database connection management
db = SQLAlchemy(app)

# Initialize Bcrypt for password hashing and encryption
bcrypt = Bcrypt(app)

# Initialize Flask-Migrate for database migrations
# Enables database schema versioning and evolution
migrate = Migrate(app, db)

# Initialize Flask-Login for user authentication
# Manages user sessions and authentication state
login_manager = LoginManager(app)

# Initialize Flask-Modals for dynamic modal dialogs
# Enhances user interface with popup functionality
modals = Modal(app)


# ============================================================================
# FLASK-LOGIN CONFIGURATION
# ============================================================================

# Set the login view endpoint for unauthenticated users
# Redirects users to login page when accessing protected routes
login_manager.login_view = 'users.login'

# Set the message category for login-related flash messages
# Provides consistent styling for authentication feedback
login_manager.login_message_category = 'info'
mail = Mail(app)



# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

from pythonic.main.routes import main
from pythonic.courses.routes import courses_bp
from pythonic.lessons.routes import lessons
from pythonic.users.routes import users

app.register_blueprint(main)
app.register_blueprint(courses_bp)
app.register_blueprint(lessons)
app.register_blueprint(users)
