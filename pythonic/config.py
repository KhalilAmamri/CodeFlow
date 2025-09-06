import os
class Config:

    SECRET_KEY = os.getenv('SECRET_KEY')

    # Database configuration
    # SQLite database file location relative to application root
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

    # Enable SQLAlchemy modification tracking for Flask-Migrate
    # This allows automatic detection of model changes
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Limit upload size to 8 MB for editor image uploads
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.getenv('EMAIL_USER')
