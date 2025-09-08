import os


class Config:
    # Core security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-change-me')

    # Database configuration
    # Default to local SQLite if not provided
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///pythonic.db')

    # Disable track modifications overhead (recommended)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Limit upload size to 8 MB for editor image uploads
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    # Mail config
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('EMAIL_USER', '')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('EMAIL_USER', ''))
