from app import db
from datetime import datetime, timezone
from flask_login import UserMixin
from app import login_manager

class AdminUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

class HospitalPartner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(100), nullable=False)
    organization_type = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    pickup_location = db.Column(db.String(200), nullable=False)
    priority_level = db.Column(db.String(20), nullable=False, default="Standard")
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="Pending", index=True)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class SupplierPartner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(100), nullable=False)
    organization_type = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    operating_zone = db.Column(db.String(200), nullable=False)
    cold_storage_capacity = db.Column(db.String(50), nullable=False)
    temperature_capability = db.Column(db.String(50), nullable=False)
    priority_level = db.Column(db.String(20), nullable=False, default="Standard")
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="Pending", index=True)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))
