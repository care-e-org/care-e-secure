#!/usr/bin/env python3
"""Seed the database with two pending hospitals and two pending suppliers for manual approval testing."""
from datetime import datetime, timezone
import sys
from pathlib import Path

# Ensure project root is on sys.path when running from scripts/ folder
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import db
from app.models import HospitalPartner, SupplierPartner
from app import create_app


# Create app and push application context for DB operations
app = create_app()


def make_hospital(name_suffix):
    h = HospitalPartner(
        facility_name=f'TEST HOSP {name_suffix}',
        organization_type='Public',
        contact_person='Test Admin',
        contact_email=f'test_hosp_{name_suffix}@example.com',
        contact_phone='0000000000',
        pickup_location='Test Location',
        notes='Seeded for approval testing',
        status='Pending',
        submitted_at=datetime.now(timezone.utc),
    )
    db.session.add(h)
    db.session.flush()
    return h


def make_supplier(name_suffix):
    s = SupplierPartner(
        facility_name=f'TEST SUP {name_suffix}',
        organization_type='Private',
        contact_person='Test Supplier',
        contact_email=f'test_sup_{name_suffix}@example.com',
        contact_phone='1111111111',
        operating_zone='Zone A',
        cold_storage_capacity='100kg',
        temperature_capability='Cold',
        notes='Seeded for approval testing',
        status='Pending',
        submitted_at=datetime.now(timezone.utc),
    )
    db.session.add(s)
    db.session.flush()
    return s


def main():
    print('Seeding 2 hospitals and 2 suppliers with status=Pending...')
    with app.app_context():
        h1 = make_hospital('A')
        h2 = make_hospital('B')
        s1 = make_supplier('A')
        s2 = make_supplier('B')
        db.session.commit()
        print('Seeded:')
        print(f'  Hospital A id={h1.id} name={h1.facility_name}')
        print(f'  Hospital B id={h2.id} name={h2.facility_name}')
        print(f'  Supplier A id={s1.id} name={s1.facility_name}')
        print(f'  Supplier B id={s2.id} name={s2.facility_name}')
    print('\nOpen the admin dashboard and approve these IDs to generate accounts and temp passwords.')


if __name__ == '__main__':
    main()
