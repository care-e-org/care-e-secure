import os
from app import create_app, db
from app.models import AdminUser
from app.bootstrap import ensure_admin_account

app = create_app()

# This forces the database to build the moment Gunicorn loads the app
with app.app_context():
    db.create_all()
    ensure_admin_account(db, AdminUser)

if __name__ == '__main__':
    app.run(debug=True)
