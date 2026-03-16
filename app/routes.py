import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import nh3
from app import db, limiter
from app.models import AdminUser, HospitalPartner, SupplierPartner
from app.forms import HospitalRegistrationForm, SupplierRegistrationForm, LoginForm

security_log = logging.getLogger('care_e.security')

bp = Blueprint('main', __name__)

# Dummy hash used to perform a constant-time comparison when the username does
# not exist, preventing timing-based username enumeration.
_DUMMY_HASH = generate_password_hash('dummy-sentinel-value')

@bp.route('/')
def index():
    return render_template('landing.html', partner_count='X')

@bp.route('/register/hospital', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register_hospital():
    form = HospitalRegistrationForm()
    if form.validate_on_submit():
        safe_notes = nh3.clean(form.notes.data) if form.notes.data else ""
        new_partner = HospitalPartner(
            facility_name=nh3.clean(form.facility_name.data),
            organization_type=form.organization_type.data,
            contact_person=nh3.clean(form.contact_person.data),
            contact_email=nh3.clean(form.contact_email.data),
            contact_phone=nh3.clean(form.contact_phone.data),
            pickup_location=nh3.clean(form.pickup_location.data),
            notes=safe_notes
        )
        db.session.add(new_partner)
        db.session.commit()
        flash('Hospital registration submitted securely. Our team will contact you shortly.', 'success')
        return redirect(url_for('main.index'))
    return render_template('register_hospital.html', form=form)

@bp.route('/register/supplier', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register_supplier():
    form = SupplierRegistrationForm()
    if form.validate_on_submit():
        safe_notes = nh3.clean(form.notes.data) if form.notes.data else ""
        new_partner = SupplierPartner(
            facility_name=nh3.clean(form.facility_name.data),
            organization_type=form.organization_type.data,
            contact_person=nh3.clean(form.contact_person.data),
            contact_email=nh3.clean(form.contact_email.data),
            contact_phone=nh3.clean(form.contact_phone.data),
            operating_zone=nh3.clean(form.operating_zone.data),
            cold_storage_capacity=form.cold_storage_capacity.data,
            temperature_capability=form.temperature_capability.data,
            notes=safe_notes
        )
        db.session.add(new_partner)
        db.session.commit()
        flash('Supplier application submitted securely. Our team will review your capabilities.', 'success')
        return redirect(url_for('main.index'))
    return render_template('register_supplier.html', form=form)

@bp.route('/admin/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        password_hash = user.password_hash if user else _DUMMY_HASH
        password_ok = check_password_hash(password_hash, form.password.data)
        if user and password_ok:
            login_user(user, remember=False)
            security_log.info('Admin login succeeded for user=%s ip=%s', form.username.data, request.remote_addr)
            return redirect(url_for('main.dashboard'))
        security_log.warning('Failed admin login attempt user=%s ip=%s', form.username.data, request.remote_addr)
        flash('Invalid credentials.', 'danger')
    return render_template('admin_login.html', form=form)

@bp.route('/admin/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/landing/admin')
@login_required
def dashboard():
    h_page = request.args.get('h_page', 1, type=int)
    s_page = request.args.get('s_page', 1, type=int)
    hospital_apps = HospitalPartner.query.order_by(HospitalPartner.submitted_at.desc()).paginate(page=h_page, per_page=20, error_out=False)
    supplier_apps = SupplierPartner.query.order_by(SupplierPartner.submitted_at.desc()).paginate(page=s_page, per_page=20, error_out=False)
    total_hospitals = HospitalPartner.query.count()
    total_suppliers = SupplierPartner.query.count()
    return render_template('admin_dashboard.html', hospital_apps=hospital_apps, supplier_apps=supplier_apps, total_hospitals=total_hospitals, total_suppliers=total_suppliers)

@bp.route('/admin/hospital/<int:app_id>/delete', methods=['POST'])
@login_required
def delete_hospital(app_id):
    record = db.session.get(HospitalPartner, app_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        flash('Hospital application deleted.', 'success')
    else:
        flash('Application not found.', 'danger')
    return redirect(url_for('main.dashboard'))

@bp.route('/admin/supplier/<int:app_id>/delete', methods=['POST'])
@login_required
def delete_supplier(app_id):
    record = db.session.get(SupplierPartner, app_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        flash('Supplier application deleted.', 'success')
    else:
        flash('Application not found.', 'danger')
    return redirect(url_for('main.dashboard'))
