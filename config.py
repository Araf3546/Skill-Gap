import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'postgresql://skillgap_user:password@localhost/skillgap_dev'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key-change')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    UPLOAD_FOLDER = 'data/uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    REDIS_URL = os.environ.get('REDIS_URL')
    # Encryption key (Day 13 generates this)
    FERNET_KEY = os.environ.get('FERNET_KEY')
    
    SESSION_COOKIE_HTTPONLY = True   # JS can't read session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF mitigation
    SESSION_COOKIE_SECURE = True     # HTTPS only (set False for local http testing)
    PERMANENT_SESSION_LIFETIME = 3600