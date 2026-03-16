import os
import logging
from app import create_app, db
from app.models import AdminUser
from werkzeug.security import generate_password_hash

app = create_app()

# This forces the database to build the moment Gunicorn loads the app
with app.app_context():
    db.create_all()

    # Create the admin account on first boot if it does not already exist.
    # Credentials are read exclusively from environment variables so that no
    # secrets are ever hard-coded in source code.
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_pass = os.environ.get('ADMIN_PASSWORD')
    if not admin_pass:
        logging.getLogger('care_e').warning(
            'ADMIN_PASSWORD env var is not set — skipping admin user creation.'
        )
    elif not AdminUser.query.filter_by(username=admin_username).first():
        admin = AdminUser(
            username=admin_username,
            password_hash=generate_password_hash(admin_pass)
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug)
