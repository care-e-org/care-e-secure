import os
import re
import secrets
import string
from datetime import datetime, timezone

from werkzeug.security import generate_password_hash


def slugify(value):
    value = value.lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or 'partner'


def build_partner_username(partner_type, source_id, facility_name):
    prefix = 'HOSP' if partner_type == 'hospital' else 'SUP'
    return f'{prefix}-{source_id:04d}-{slugify(facility_name)}'


def generate_temporary_password():
    default_password = os.environ.get('DEFAULT_PARTNER_TEMP_PASSWORD')
    if default_password:
        return default_password
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(12))


def store_temp_credential(db, temp_model, account_id, temp_password):
    record = temp_model.query.filter_by(partner_account_id=account_id).first()
    if not record:
        record = temp_model(partner_account_id=account_id, temp_password_plain=temp_password)
        db.session.add(record)
    else:
        record.temp_password_plain = temp_password
        record.issued_at = datetime.now(timezone.utc)
    return record


def issue_new_temporary_password(db, account, temp_model):
    temp_password = generate_temporary_password()
    account.password_hash = generate_password_hash(temp_password)
    account.must_change_password = True
    account.approved = True
    store_temp_credential(db, temp_model, account.id, temp_password)
    return temp_password


def approve_partner_application(db, partner_model, account_model, partner_type, source_id):
    partner = db.session.get(partner_model, source_id)
    if not partner:
        return None, None, None

    # If the partner record is already marked approved but the account is missing,
    # create the account and issue a temporary password so the admin can retrieve it.
    if partner.status == 'Approved':
        account = account_model.query.filter_by(partner_type=partner_type, source_id=source_id).first()
        if account:
            return partner, account, None

        # Account missing despite partner being approved: create account and return temp password.
        username = build_partner_username(partner_type, partner.id, partner.facility_name)
        temp_password = generate_temporary_password()
        account = account_model(
            partner_type=partner_type,
            source_id=partner.id,
            username=username,
            password_hash=generate_password_hash(temp_password),
            approved=True,
            must_change_password=True,
        )
        db.session.add(account)
        db.session.commit()
        return partner, account, temp_password

    partner.status = 'Approved'
    username = build_partner_username(partner_type, partner.id, partner.facility_name)
    temp_password = generate_temporary_password()
    account = account_model(
        partner_type=partner_type,
        source_id=partner.id,
        username=username,
        password_hash=generate_password_hash(temp_password),
        approved=True,
        must_change_password=True,
    )
    db.session.add(account)
    db.session.commit()
    return partner, account, temp_password