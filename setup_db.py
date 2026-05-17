import os
from app import create_app, db
from app.models import AdminUser
from app.bootstrap import ensure_admin_account

app = create_app()
with app.app_context():
    # 1. Build the tables safely
    db.create_all()
    ensure_admin_account(db, AdminUser)
