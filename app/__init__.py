from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()

login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

# Tell Talisman that the Bootstrap CDN is safe!
csp = {
    'default-src': [
        '\'self\'',
    ],
    'style-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net'
    ],
    'script-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net'
    ]
}

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    # Pass the custom CSP whitelist to Talisman
    talisman.init_app(app, force_https=False, content_security_policy=csp)  

    with app.app_context():
        from app import models
        from app.routes import bp as main_bp
        app.register_blueprint(main_bp)
        
    return app
