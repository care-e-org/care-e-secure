import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import nh3
from app import db, limiter
from app.models import AdminUser, HospitalPartner, SupplierPartner, PartnerAccount, PartnerTempCredential, SupplierOffering, HospitalSupplierSelection
from app.forms import HospitalRegistrationForm, SupplierRegistrationForm, LoginForm, PartnerLoginForm, PasswordChangeForm, SupplierOfferingForm
from app.partnering import approve_partner_application, issue_new_temporary_password, store_temp_credential

security_log = logging.getLogger('care_e.security')

bp = Blueprint('main', __name__)


def is_admin_user(user):
    return isinstance(user, AdminUser)


def require_admin():
    if not is_admin_user(current_user):
        flash('Admin access required.', 'danger')
        return False
    return True


def get_partner_source(account):
    if account.partner_type == 'hospital':
        return db.session.get(HospitalPartner, account.source_id)
    return db.session.get(SupplierPartner, account.source_id)


def get_supplier_accounts():
    return PartnerAccount.query.filter_by(partner_type='supplier', approved=True).order_by(PartnerAccount.created_at.desc()).all()


def get_hospital_selected_supplier_ids(hospital_account_id):
    selections = HospitalSupplierSelection.query.filter_by(hospital_account_id=hospital_account_id).all()
    return {selection.supplier_account_id for selection in selections}

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
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=False)
            security_log.info('Admin login succeeded for user=%s ip=%s', form.username.data, request.remote_addr)
            return redirect(url_for('main.dashboard'))
        security_log.warning('Failed admin login attempt user=%s ip=%s', form.username.data, request.remote_addr)
        flash('Invalid credentials.', 'danger')
    return render_template('admin_login.html', form=form)


@bp.route('/partner/login', methods=['GET', 'POST'])
@limiter.limit("8 per minute")
def partner_login():
    form = PartnerLoginForm()
    if form.validate_on_submit():
        user = PartnerAccount.query.filter_by(username=form.username.data).first()
        if user and user.approved and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=False)
            if user.must_change_password:
                return redirect(url_for('main.partner_change_password'))
            return redirect(url_for('main.partner_dashboard'))
        flash('Approved partner credentials required.', 'danger')
    return render_template('partner_login.html', form=form)

@bp.route('/admin/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/partner/logout', methods=['POST'])
@login_required
def partner_logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/landing/admin')
@login_required
def dashboard():
    if not require_admin():
        return redirect(url_for('main.partner_dashboard'))

    h_page = request.args.get('h_page', 1, type=int)
    s_page = request.args.get('s_page', 1, type=int)
    hospital_apps = HospitalPartner.query.order_by(HospitalPartner.submitted_at.desc()).paginate(page=h_page, per_page=20, error_out=False)
    supplier_apps = SupplierPartner.query.order_by(SupplierPartner.submitted_at.desc()).paginate(page=s_page, per_page=20, error_out=False)
    total_hospitals = HospitalPartner.query.count()
    total_suppliers = SupplierPartner.query.count()

    hospital_credentials = {}
    supplier_credentials = {}

    hospital_ids = [app.id for app in hospital_apps.items]
    supplier_ids = [app.id for app in supplier_apps.items]

    hospital_accounts = PartnerAccount.query.filter(PartnerAccount.partner_type == 'hospital', PartnerAccount.source_id.in_(hospital_ids)).all() if hospital_ids else []
    supplier_accounts = PartnerAccount.query.filter(PartnerAccount.partner_type == 'supplier', PartnerAccount.source_id.in_(supplier_ids)).all() if supplier_ids else []

    for account in hospital_accounts:
        cred = PartnerTempCredential.query.filter_by(partner_account_id=account.id).first()
        hospital_credentials[account.source_id] = {
            'username': account.username,
            'temp_password': cred.temp_password_plain if cred else None,
            'must_change_password': account.must_change_password,
        }

    for account in supplier_accounts:
        cred = PartnerTempCredential.query.filter_by(partner_account_id=account.id).first()
        supplier_credentials[account.source_id] = {
            'username': account.username,
            'temp_password': cred.temp_password_plain if cred else None,
            'must_change_password': account.must_change_password,
        }

    all_accounts = PartnerAccount.query.filter_by(approved=True).order_by(PartnerAccount.created_at.desc()).all()
    hospital_names = {item.id: item.facility_name for item in HospitalPartner.query.filter(HospitalPartner.id.in_([a.source_id for a in all_accounts if a.partner_type == 'hospital'])).all()} if all_accounts else {}
    supplier_names = {item.id: item.facility_name for item in SupplierPartner.query.filter(SupplierPartner.id.in_([a.source_id for a in all_accounts if a.partner_type == 'supplier'])).all()} if all_accounts else {}

    credential_vault = []
    for account in all_accounts:
        cred = PartnerTempCredential.query.filter_by(partner_account_id=account.id).first()
        facility_name = hospital_names.get(account.source_id) if account.partner_type == 'hospital' else supplier_names.get(account.source_id)
        credential_vault.append({
            'partner_type': account.partner_type,
            'facility_name': facility_name or 'Unknown',
            'username': account.username,
            'temp_password': cred.temp_password_plain if cred else '',
            'must_change_password': account.must_change_password,
            'source_id': account.source_id,
        })

    return render_template(
        'admin_dashboard.html',
        hospital_apps=hospital_apps,
        supplier_apps=supplier_apps,
        total_hospitals=total_hospitals,
        total_suppliers=total_suppliers,
        hospital_credentials=hospital_credentials,
        supplier_credentials=supplier_credentials,
        credential_vault=credential_vault,
    )


@bp.route('/admin/hospital/<int:app_id>/approve', methods=['POST'])
@login_required
def approve_hospital(app_id):
    if not require_admin():
        return redirect(url_for('main.partner_dashboard'))

    partner, account, temp_password = approve_partner_application(db, HospitalPartner, PartnerAccount, 'hospital', app_id)
    if not partner:
        flash('Hospital application not found.', 'danger')
    else:
        if temp_password:
            store_temp_credential(db, PartnerTempCredential, account.id, temp_password)
            db.session.commit()
            flash(f'Hospital approved. Username: {account.username} Temporary password: {temp_password}', 'success')
        else:
            existing_cred = PartnerTempCredential.query.filter_by(partner_account_id=account.id).first() if account else None
            if existing_cred:
                flash(f'Hospital already approved. Username: {account.username} Temporary password: {existing_cred.temp_password_plain}', 'info')
            else:
                flash(f'Hospital already approved. Username: {account.username}. Use Reset Temp Password to generate a new one.', 'info')
    return redirect(url_for('main.dashboard'))


@bp.route('/admin/supplier/<int:app_id>/approve', methods=['POST'])
@login_required
def approve_supplier(app_id):
    if not require_admin():
        return redirect(url_for('main.partner_dashboard'))

    partner, account, temp_password = approve_partner_application(db, SupplierPartner, PartnerAccount, 'supplier', app_id)
    if not partner:
        flash('Supplier application not found.', 'danger')
    else:
        if temp_password:
            store_temp_credential(db, PartnerTempCredential, account.id, temp_password)
            db.session.commit()
            flash(f'Supplier approved. Username: {account.username} Temporary password: {temp_password}', 'success')
        else:
            existing_cred = PartnerTempCredential.query.filter_by(partner_account_id=account.id).first() if account else None
            if existing_cred:
                flash(f'Supplier already approved. Username: {account.username} Temporary password: {existing_cred.temp_password_plain}', 'info')
            else:
                flash(f'Supplier already approved. Username: {account.username}. Use Reset Temp Password to generate a new one.', 'info')
    return redirect(url_for('main.dashboard'))


@bp.route('/admin/hospital/<int:app_id>/reset-temp-password', methods=['POST'])
@login_required
def reset_hospital_temp_password(app_id):
    if not require_admin():
        return redirect(url_for('main.partner_dashboard'))

    account = PartnerAccount.query.filter_by(partner_type='hospital', source_id=app_id, approved=True).first()
    if not account:
        flash('No approved hospital account found. Approve first.', 'danger')
        return redirect(url_for('main.dashboard'))

    temp_password = issue_new_temporary_password(db, account, PartnerTempCredential)
    db.session.commit()
    flash(f'New hospital temporary credentials: Username: {account.username} Temporary password: {temp_password}', 'success')
    return redirect(url_for('main.dashboard'))


@bp.route('/admin/supplier/<int:app_id>/reset-temp-password', methods=['POST'])
@login_required
def reset_supplier_temp_password(app_id):
    if not require_admin():
        return redirect(url_for('main.partner_dashboard'))

    account = PartnerAccount.query.filter_by(partner_type='supplier', source_id=app_id, approved=True).first()
    if not account:
        flash('No approved supplier account found. Approve first.', 'danger')
        return redirect(url_for('main.dashboard'))

    temp_password = issue_new_temporary_password(db, account, PartnerTempCredential)
    db.session.commit()
    flash(f'New supplier temporary credentials: Username: {account.username} Temporary password: {temp_password}', 'success')
    return redirect(url_for('main.dashboard'))


@bp.route('/partner/change-password', methods=['GET', 'POST'])
@login_required
def partner_change_password():
    if getattr(current_user, 'partner_type', None) not in ('hospital', 'supplier'):
        flash('Partner access required.', 'danger')
        return redirect(url_for('main.login'))

    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('partner_change_password.html', form=form)
        current_user.password_hash = generate_password_hash(form.new_password.data)
        current_user.must_change_password = False
        temp_record = PartnerTempCredential.query.filter_by(partner_account_id=current_user.id).first()
        if temp_record:
            db.session.delete(temp_record)
        db.session.commit()
        flash('Password updated successfully.', 'success')
        return redirect(url_for('main.partner_dashboard'))
    return render_template('partner_change_password.html', form=form)


@bp.route('/partner/dashboard')
@login_required
def partner_dashboard():
    if getattr(current_user, 'partner_type', None) not in ('hospital', 'supplier'):
        flash('Partner access required.', 'danger')
        return redirect(url_for('main.login'))
    if current_user.must_change_password:
        return redirect(url_for('main.partner_change_password'))

    source = get_partner_source(current_user)
    if current_user.partner_type == 'hospital':
        approved_suppliers = get_supplier_accounts()
        selected_supplier_ids = get_hospital_selected_supplier_ids(current_user.id)
        # Only show offerings from suppliers the hospital has explicitly selected.
        selected_suppliers = [supplier for supplier in approved_suppliers if supplier.id in selected_supplier_ids]
        supplier_offerings = []
        if selected_supplier_ids:
            supplier_offerings = SupplierOffering.query.filter(SupplierOffering.supplier_account_id.in_(list(selected_supplier_ids))).order_by(SupplierOffering.created_at.desc()).all()
        return render_template('partner_dashboard.html', source=source, approved_suppliers=approved_suppliers, selected_suppliers=selected_suppliers, supplier_offerings=supplier_offerings, partner_type='hospital')

    offering_form = SupplierOfferingForm()
    own_offerings = SupplierOffering.query.filter_by(supplier_account_id=current_user.id).order_by(SupplierOffering.created_at.desc()).all()
    return render_template('partner_dashboard.html', source=source, offering_form=offering_form, own_offerings=own_offerings, partner_type='supplier')


@bp.route('/partner/suppliers/<int:supplier_account_id>/select', methods=['POST'])
@login_required
def select_supplier(supplier_account_id):
    if getattr(current_user, 'partner_type', None) != 'hospital':
        flash('Hospital access required.', 'danger')
        return redirect(url_for('main.partner_login'))

    supplier = db.session.get(PartnerAccount, supplier_account_id)
    if not supplier or supplier.partner_type != 'supplier' or not supplier.approved:
        flash('Supplier not available.', 'danger')
        return redirect(url_for('main.partner_dashboard'))

    existing = HospitalSupplierSelection.query.filter_by(hospital_account_id=current_user.id, supplier_account_id=supplier_account_id).first()
    if not existing:
        db.session.add(HospitalSupplierSelection(hospital_account_id=current_user.id, supplier_account_id=supplier_account_id))
        db.session.commit()
    flash('Supplier selected for your hospital dashboard.', 'success')
    return redirect(url_for('main.partner_dashboard'))


@bp.route('/partner/offerings/upload', methods=['POST'])
@login_required
def upload_offering():
    if getattr(current_user, 'partner_type', None) != 'supplier':
        flash('Supplier access required.', 'danger')
        return redirect(url_for('main.partner_login'))

    form = SupplierOfferingForm()
    if form.validate_on_submit():
        offering = SupplierOffering(
            supplier_account_id=current_user.id,
            title=nh3.clean(form.title.data),
            description=nh3.clean(form.description.data),
            quantity=nh3.clean(form.quantity.data),
            availability=form.availability.data,
        )
        db.session.add(offering)
        db.session.commit()
        flash('Supply uploaded successfully.', 'success')
    else:
        flash('Please correct the supply form.', 'danger')
    return redirect(url_for('main.partner_dashboard'))

@bp.route('/admin/hospital/<int:app_id>/delete', methods=['POST'])
@login_required
def delete_hospital(app_id):
    if not require_admin():
        return redirect(url_for('main.partner_dashboard'))

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
    if not require_admin():
        return redirect(url_for('main.partner_dashboard'))

    record = db.session.get(SupplierPartner, app_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        flash('Supplier application deleted.', 'success')
    else:
        flash('Application not found.', 'danger')
    return redirect(url_for('main.dashboard'))
