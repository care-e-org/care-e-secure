import click
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress

db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()
csrf = CSRFProtect()
compress = Compress()

login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

# The Ultimate B2B CSP Whitelist
csp = {
    'default-src': ['\'self\''],
    'style-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'https://cdn.jsdelivr.net',
        'https://fonts.googleapis.com',
        'https://cdnjs.cloudflare.com'
    ],
    'font-src': [
        '\'self\'',
        'https://fonts.gstatic.com',
        'https://cdn.jsdelivr.net',
        'https://cdnjs.cloudflare.com'
    ],
    'script-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net'
    ],
    'img-src': [
        '\'self\'',
        'data:'  # Allows inline SVGs if Copilot used them for icons
    ]
}

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    
    # Apply the expanded shield
    talisman.init_app(
        app,
        force_https=not app.debug,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src']
    )

    with app.app_context():
        from app import models
        from app.routes import bp as main_bp
        app.register_blueprint(main_bp)

    @app.cli.command('init-db')
    @click.option('--force', is_flag=True, help='Drop and recreate all tables.')
    def init_db(force):
        """Initialize the database tables."""
        with app.app_context():
            if force:
                db.drop_all()
            db.create_all()
            click.echo('Database initialized.')

    return app
