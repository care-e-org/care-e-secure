from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import bleach
from app import db
from app.models import AdminUser, HospitalPartner, SupplierPartner
from app.forms import HospitalRegistrationForm, SupplierRegistrationForm, LoginForm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('landing.html')

@bp.route('/register/hospital', methods=['GET', 'POST'])
def register_hospital():
    form = HospitalRegistrationForm()
    if form.validate_on_submit():
        safe_notes = bleach.clean(form.notes.data) if form.notes.data else ""
        new_partner = HospitalPartner(
            facility_name=form.facility_name.data,
            organization_type=form.organization_type.data,
            contact_person=form.contact_person.data,
            contact_email=form.contact_email.data,
            contact_phone=form.contact_phone.data,
            pickup_location=form.pickup_location.data,
            priority_level=form.priority_level.data,
            notes=safe_notes
        )
        db.session.add(new_partner)
        db.session.commit()
        flash('Hospital registration submitted securely. Our team will contact you shortly.', 'success')
        return redirect(url_for('main.index'))
    return render_template('register_hospital.html', form=form)

@bp.route('/register/supplier', methods=['GET', 'POST'])
def register_supplier():
    form = SupplierRegistrationForm()
    if form.validate_on_submit():
        safe_notes = bleach.clean(form.notes.data) if form.notes.data else ""
        new_partner = SupplierPartner(
            facility_name=form.facility_name.data,
            organization_type=form.organization_type.data,
            contact_person=form.contact_person.data,
            contact_email=form.contact_email.data,
            contact_phone=form.contact_phone.data,
            operating_zone=form.operating_zone.data,
            cold_storage_capacity=form.cold_storage_capacity.data,
            temperature_capability=form.temperature_capability.data,
            priority_level=form.priority_level.data,
            notes=safe_notes
        )
        db.session.add(new_partner)
        db.session.commit()
        flash('Supplier application submitted securely. Our team will review your capabilities.', 'success')
        return redirect(url_for('main.index'))
    return render_template('register_supplier.html', form=form)

@bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('admin_login.html', form=form)

@bp.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/landing/admin')
@login_required
def dashboard():
    hospital_apps = HospitalPartner.query.order_by(HospitalPartner.submitted_at.desc()).all()
    supplier_apps = SupplierPartner.query.order_by(SupplierPartner.submitted_at.desc()).all()
    return render_template('admin_dashboard.html', hospital_apps=hospital_apps, supplier_apps=supplier_apps)
