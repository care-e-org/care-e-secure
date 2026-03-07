import os
from app import create_app, db
from app.models import AdminUser
from werkzeug.security import generate_password_hash

app = create_app()

# This forces the database to build the moment Gunicorn loads the app
with app.app_context():
    db.create_all()
    
    # Check if your admin account exists, if not, create it
    if not AdminUser.query.filter_by(username='suryarkd').first():
        admin_pass = os.environ.get('SECRET_KEY')
        if admin_pass:
            admin = AdminUser(username='suryarkd', password_hash=generate_password_hash(admin_pass))
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
