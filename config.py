import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Loads your Secret Key from .env or fails loudly
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("FATAL: SECRET_KEY environment variable is not set.")
    
    # Cloud Database Detection
    database_url = os.environ.get('DATABASE_URL')
    
    # Fix for SQLAlchemy/Railway Postgres naming
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = database_url or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'care_e.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Hardened Security Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 1800
