import os
from app import create_app, db
from app.models import AdminUser
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # 1. Build the tables safely
    db.create_all()
    
    # 2. Create the admin user if it doesn't exist
    if not AdminUser.query.filter_by(username='suryarkd').first():
        # Uses your Railway SECRET_KEY as the secure password
        admin_pass = os.environ.get('SECRET_KEY')
        admin = AdminUser(username='suryarkd', password_hash=generate_password_hash(admin_pass))
        db.session.add(admin)
        db.session.commit()
