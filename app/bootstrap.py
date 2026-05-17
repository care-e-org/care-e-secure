import os

from werkzeug.security import generate_password_hash


def ensure_admin_account(db, admin_model):
    username = os.environ.get('ADMIN_USERNAME', 'CARE-E_ADMIN')
    admin = admin_model.query.filter_by(username=username).first()
    if admin:
        return False

    password_hash = os.environ.get('ADMIN_PASSWORD_HASH')
    if not password_hash:
        admin_password = os.environ.get('ADMIN_PASSWORD') or os.environ.get('SECRET_KEY')
        if admin_password:
            password_hash = generate_password_hash(admin_password)

    if not password_hash:
        return False

    db.session.add(admin_model(username=username, password_hash=password_hash))
    db.session.commit()
    return True