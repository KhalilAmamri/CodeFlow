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

# ============================================================================
# FLASK APPLICATION INSTANCE CREATION
# ============================================================================

# Create the main Flask application instance
# __name__ represents the current Python module name
app = Flask(__name__)


# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

# Secret key for session management and CSRF protection
# This should be stored as an environment variable in production
app.config['SECRET_KEY'] = 'e08fe17fe27ffc7009aba6a264a886ea81a5b5bd17f1fc97b9554c89c1464588'

# Database configuration
# SQLite database file location relative to application root
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pythonic.db'

# Enable SQLAlchemy modification tracking for Flask-Migrate
# This allows automatic detection of model changes
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Limit upload size to 8 MB for editor image uploads
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


# ============================================================================
# EXTENSION INITIALIZATION AND CONFIGURATION
# ============================================================================

# Initialize SQLAlchemy database instance
# This provides ORM functionality and database connection management
db = SQLAlchemy(app)

# Initialize Bcrypt for password hashing
# Provides secure password encryption and verification
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
login_manager.login_view = 'login'

# Set the message category for login-related flash messages
# Provides consistent styling for authentication feedback
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')
mail = Mail(app)



# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

# Import and register application routes
# This must be imported after app creation to avoid circular imports
# Routes module contains all the view functions and URL mappings
from pythonic import routes