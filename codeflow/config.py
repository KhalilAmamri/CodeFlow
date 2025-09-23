import os


class Config:
    # Core security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-change-me')

    # Database configuration
    # Prefer SQLALCHEMY_DATABASE_URI; fall back to Render/Dokku style DATABASE_URL; else local SQLite
    _db_url = os.getenv('SQLALCHEMY_DATABASE_URI') or os.getenv('DATABASE_URL')
    # Normalize old postgres:// scheme to postgresql:// for SQLAlchemy
    if _db_url and _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    # Default to a file in the instance folder for local dev
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///instance/codeflow.db'

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
