import os
from dotenv import load_dotenv

# Load the hidden variables from .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # 1. Core Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = os.environ.get('FLASK_ENV') != 'production'
    
    # 2. Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'care_e.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. Payload Limits (1MB limit for 4GB RAM safety)
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024 

    # 4. Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 1800
