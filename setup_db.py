import argparse
import os
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import AdminUser

DEFAULT_ADMIN_USERNAME = "CARE-E_ADMIN"
DEFAULT_ADMIN_PASSWORD = "CARE-E-2026"


def parse_args():
    parser = argparse.ArgumentParser(description="Initialize database and bootstrap admin user.")
    parser.add_argument("--username", default=os.environ.get("ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME))
    parser.add_argument("--password", default=os.environ.get("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD))
    return parser.parse_args()


def main():
    args = parse_args()
    app = create_app()
    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()
        admin = AdminUser.query.filter_by(username=args.username).first()
        if not admin:
            admin = AdminUser(
                username=args.username,
                password_hash=generate_password_hash(args.password),
            )
            db.session.add(admin)
        else:
            admin.password_hash = generate_password_hash(args.password)
        db.session.commit()
        print(f"Admin account ready: {args.username}")


if __name__ == "__main__":
    main()
