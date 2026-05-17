from app import db
from datetime import datetime, timezone
from flask_login import UserMixin
from app import login_manager

class AdminUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    def get_id(self):
        return f'admin:{self.id}'


class PartnerAccount(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    partner_type = db.Column(db.String(20), nullable=False, index=True)
    source_id = db.Column(db.Integer, nullable=False, index=True)
    username = db.Column(db.String(96), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    approved = db.Column(db.Boolean, nullable=False, default=False, index=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def get_id(self):
        return f'partner:{self.id}'


class PartnerTempCredential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partner_account_id = db.Column(db.Integer, db.ForeignKey('partner_account.id'), nullable=False, unique=True, index=True)
    temp_password_plain = db.Column(db.String(128), nullable=False)
    issued_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

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


class SupplierOffering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_account_id = db.Column(db.Integer, db.ForeignKey('partner_account.id'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    availability = db.Column(db.String(50), nullable=False, default='Available')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class HospitalSupplierSelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_account_id = db.Column(db.Integer, db.ForeignKey('partner_account.id'), nullable=False, index=True)
    supplier_account_id = db.Column(db.Integer, db.ForeignKey('partner_account.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        db.UniqueConstraint('hospital_account_id', 'supplier_account_id', name='uq_hospital_supplier_selection'),
    )

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
    if not user_id:
        return None
    try:
        kind, raw_id = user_id.split(':', 1)
        item_id = int(raw_id)
    except (ValueError, AttributeError):
        return None

    if kind == 'admin':
        return db.session.get(AdminUser, item_id)
    if kind == 'partner':
        return db.session.get(PartnerAccount, item_id)
    return None
