"""
Production Database Initialization for Satyameva

Initializes a clean production environment:
1. Resets all database tables.
2. Ensures Genesis Block #0 on the cryptographic ledger.
3. Pre-approves the 3 official Jaypee institutions (JIIT Noida, JUIT Waknaghat, JUET Guna).
4. Creates the official Master Administrator account from .env (default: admin / Satyameva@2026).
5. Zero dummy users, zero fake credentials, zero fake verification logs.

Run with:
    python init_db.py
"""
import os
import sys

from app import create_app
from blockchain import ensure_genesis_block, validate_chain
from extensions import db, utcnow
from models.institution import Institution
from models.user import ROLE_ADMIN, User
from security import hash_password


def init_production_db():
    app = create_app()
    with app.app_context():
        print()
        print('====================================================')
        print('  Satyameva - Production Database Initialization   ')
        print('====================================================')

        # Drop all tables to guarantee zero leftover demo artifacts
        db.drop_all()
        db.create_all()
        print('  [x] All previous demo data & tables purged.')

        # 1. Initialize Genesis Block #0
        ensure_genesis_block()
        print('  [x] Cryptographic ledger initialized at Genesis Block #0.')

        # 2. Register Jaypee Group Institutions
        campuses = [
            {
                'short_code': 'JIIT',
                'name': 'Jaypee Institute of Information Technology',
                'domain': 'jiit.ac.in',
                'address': 'A-10, Sector-62, Noida, Uttar Pradesh 201309',
            },
            {
                'short_code': 'JUIT',
                'name': 'Jaypee University of Information Technology',
                'domain': 'juit.ac.in',
                'address': 'Waknaghat, P.O. Dumehar, Kandaghat, Solan, Himachal Pradesh 173234',
            },
            {
                'short_code': 'JUET',
                'name': 'Jaypee University of Engineering and Technology',
                'domain': 'juet.ac.in',
                'address': 'A.B. Road, Raghogarh, Guna, Madhya Pradesh 473226',
            },
        ]

        inst_records = []
        for c in campuses:
            inst = Institution(
                name=c['name'],
                short_code=c['short_code'],
                domain=c['domain'],
                address=c['address'],
                is_approved=True,
                approved_at=utcnow(),
            )
            db.session.add(inst)
            inst_records.append(inst)

        db.session.flush()
        print('  [x] Pre-approved official Jaypee institutions:')
        print('      - JIIT Noida (Sector-62 & 128)')
        print('      - JUIT Waknaghat (Solan, HP)')
        print('      - JUET Guna (MP)')

        # 3. Create Master Administrator Account
        admin_user = os.environ.get('ADMIN_USERNAME', 'admin').strip()
        admin_email = os.environ.get('ADMIN_EMAIL', 'hackathonsage@gmail.com').strip()
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'Satyameva@2026').strip()

        target_iterations = app.config.get('PASSWORD_ITERATIONS', 100000)
        salt, digest, iters = hash_password(admin_pass, target_iterations)

        admin = User(
            username=admin_user,
            email=admin_email,
            role=ROLE_ADMIN,
            organization='Satyameva National Academic Verification Authority',
            institution_id=inst_records[0].id,  # Associate with JIIT root
            password_salt=salt,
            password_hash=digest,
            password_iterations=iters,
        )
        db.session.add(admin)
        db.session.flush()

        # Link institution approvals to master admin
        for inst in inst_records:
            inst.approved_by_id = admin.id

        db.session.commit()
        print(f'  [x] Master Administrator created:')
        print(f'      Username: {admin_user}')
        print(f'      Email:    {admin_email}')
        print(f'      Role:     Global Super-Admin')

        ok, msg = validate_chain()
        print(f'  [x] Chain validation: {msg}')
        print('====================================================')
        print('  Production database is live and ready for real use.')
        print('====================================================\n')


if __name__ == '__main__':
    init_production_db()
