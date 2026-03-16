import os
from app import create_app, db
from app.models import AdminUser
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # 1. Build the tables safely
    db.create_all()

    # 2. Create the admin user if it doesn't exist.
    #    Read credentials from dedicated environment variables — never reuse
    #    SECRET_KEY as a password.
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_pass = os.environ.get('ADMIN_PASSWORD')
    if not admin_pass:
        raise RuntimeError("FATAL: ADMIN_PASSWORD environment variable is not set.")
    if not AdminUser.query.filter_by(username=admin_username).first():
        admin = AdminUser(
            username=admin_username,
            password_hash=generate_password_hash(admin_pass)
        )
        db.session.add(admin)
        db.session.commit()
