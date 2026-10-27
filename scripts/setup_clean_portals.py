"""
setup_clean_portals.py
Reconfigures Satyameva Aegis with the 4 designated production roles:
1. Superadmin (superadmin / Satyameva@2026)
2. University Issuer (juit.registrar / Juit@2026)
3. Student Portal / Wallet (praneeth / Praneeth@2026) @ JUIT (2026-2030, DOB: 01092008)
4. Corporate Verifier (verifier / Verifier@2026)
Purges all old dummy/demo accounts and re-mines the PoW blockchain ledger cleanly.
"""

import os
import sys
from datetime import timedelta
from io import BytesIO
from PIL import Image, ImageDraw

sys.path.append(r"C:\Users\hp\OneDrive\Desktop\Satyameva")

from app import create_app
from extensions import db, utcnow
from models.document import Doc
from models.institution import Institution
from models.student import Student
from models.user import ROLE_ADMIN, ROLE_ISSUER, ROLE_STUDENT, ROLE_VERIFIER, User
from models.verification_log import RESULT_VALID, RESULT_EXPIRED, VerificationLog
from security import hash_password
from services.credential_service import issue_credential
from services.stamp_service import _fit_font, _font
import blockchain


def make_certificate_image(title, student_name, roll, program, institution,
                           issued_on, extra_lines=()) -> bytes:
    W, H = 1400, 990
    img = Image.new('RGB', (W, H), (253, 252, 248))
    draw = ImageDraw.Draw(img)

    # Ornamental double border
    draw.rectangle([18, 18, W - 18, H - 18], outline=(150, 130, 70), width=6)
    draw.rectangle([34, 34, W - 34, H - 34], outline=(196, 178, 120), width=2)

    f_inst = _font(42, bold=True)
    f_kicker = _font(22)
    f_body = _font(26)
    f_name = _font(52, bold=True)
    f_small = _font(21)

    def centered(text, y, font, fill):
        left, _, right, _ = draw.textbbox((0, 0), text, font=font)
        draw.text(((W - (right - left)) / 2, y), text, font=font, fill=fill)

    centered(institution.upper(), 76, f_inst, (28, 34, 82))
    centered('Estd. 2002  ·  Government of Himachal Pradesh  ·  UGC Recognised', 134, f_kicker, (120, 124, 150))
    draw.line([(280, 176), (W - 280, 176)], fill=(196, 178, 120), width=3)

    f_title = _fit_font(draw, title.upper(), W - 200, start=56, bold=True, minimum=24)
    centered(title.upper(), 224, f_title, (150, 130, 70))
    centered('This is to certify that', 326, f_body, (70, 74, 98))
    centered(student_name, 374, f_name, (28, 34, 82))
    centered(f'Roll Number: {roll}', 448, f_body, (70, 74, 98))
    centered(f'has successfully completed {program}', 496, f_body, (70, 74, 98))

    y = 556
    for line in extra_lines:
        centered(line, y, f_body, (70, 74, 98))
        y += 44

    centered(f'Issued at Waknaghat on {issued_on.strftime("%d %B %Y")}', y + 30, f_small, (120, 124, 150))

    for x, label in ((240, 'Controller of Examinations'), (W - 240 - 320, 'Registrar')):
        draw.line([(x, H - 170), (x + 320, H - 170)], fill=(90, 94, 120), width=2)
        draw.text((x + 40, H - 158), label, font=f_small, fill=(90, 94, 120))

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def create_user(username, email, role, password, organization=None, institution_id=None, oauth_provider=None, oauth_sub=None):
    salt, digest, iterations = hash_password(password)
    user = User(
        username=username,
        email=email.lower(),
        role=role,
        organization=organization,
        institution_id=institution_id,
        password_salt=salt,
        password_hash=digest,
        password_iterations=iterations,
        oauth_provider=oauth_provider,
        oauth_sub=oauth_sub,
        is_active=True
    )
    db.session.add(user)
    db.session.flush()
    return user


def setup_portals(reset: bool = True):
    app = create_app()
    app.config['MAIL_SUPPRESS_SEND'] = True

    with app.app_context():
        if not reset and User.query.filter_by(username='superadmin').first() is not None:
            print("[INFO] Production portals are already initialized. Use --reset to re-seed from scratch.")
            return

        print("[1/5] Resetting database tables...")
        db.drop_all()
        db.create_all()

        # Clean JSON blockchain
        chain_json = os.path.join(app.instance_path, 'blockchain.json')
        if os.path.exists(chain_json):
            os.remove(chain_json)
        blockchain.ensure_genesis_block()
        print("[OK] Database and genesis block reset cleanly.")

        # ---- 1. Campuses ----
        print("[2/5] Initializing Jaypee Campuses...")
        juit = Institution(
            name='Jaypee University of Information Technology',
            short_code='JUIT',
            domain='juit.ac.in',
            address='Waknaghat, P.O. Dumehar, Kandaghat, Solan, Himachal Pradesh 173234',
            is_approved=True,
            approved_at=utcnow(),
        )
        jiit = Institution(
            name='Jaypee Institute of Information Technology',
            short_code='JIIT',
            domain='jiit.ac.in',
            address='A-10, Sector-62, Noida, Uttar Pradesh 201309',
            is_approved=True,
            approved_at=utcnow(),
        )
        juet = Institution(
            name='Jaypee University of Engineering and Technology',
            short_code='JUET',
            domain='juet.ac.in',
            address='A.B. Road, Raghogarh, Guna, Madhya Pradesh 473226',
            is_approved=True,
            approved_at=utcnow(),
        )
        db.session.add_all([juit, jiit, juet])
        db.session.flush()

        # ---- 2. The 4 Designated Roles ----
        print("[3/5] Creating the 4 Designated Roles...")

        # 1. Superadmin
        admin_user = create_user(
            username='superadmin',
            email='superadmin@satyameva.in',
            role=ROLE_ADMIN,
            password='Satyameva@2026',
            institution_id=juit.id
        )
        juit.approved_by_id = admin_user.id
        jiit.approved_by_id = admin_user.id
        juet.approved_by_id = admin_user.id

        # 2. University Issuer (JUIT Waknaghat Registrar)
        issuer_user = create_user(
            username='juit.registrar',
            email='registrar@juit.ac.in',
            role=ROLE_ISSUER,
            password='Juit@2026',
            organization='Jaypee University of Information Technology',
            institution_id=juit.id
        )

        # 3. Student Portal / Wallet (Praneeth Sai @ JUIT)
        student_user = create_user(
            username='praneeth',
            email='praneethsai050@gmail.com',
            role=ROLE_STUDENT,
            password='Praneeth@2026',
            organization='Jaypee University of Information Technology',
            institution_id=juit.id,
            oauth_provider='google',
            oauth_sub='112210141531666167855'
        )

        praneeth_student = Student(
            user_id=student_user.id,
            full_name='Praneeth Sai',
            roll_number='22103050',
            department='Computer Science & Engineering',
            program='B.Tech CSE',
            batch='2026-2030',
            institution='Jaypee University of Information Technology',
            dob='2008-09-01',
            email_verified=True,
            issuer_approved=True,
            issuer_approved_by_id=issuer_user.id,
            issuer_approved_at=utcnow(),
        )
        db.session.add(praneeth_student)

        # 4. Corporate Verifier
        verifier_user = create_user(
            username='verifier',
            email='verifier@corporate.in',
            role=ROLE_VERIFIER,
            password='Verifier@2026',
            organization='Corporate Background Verifications Ltd.'
        )

        db.session.commit()
        print("[OK] 4 core users and student record created successfully.")

        # ---- 3. Issue Official JUIT Credentials to Praneeth ----
        print("[4/5] Mining and issuing official JUIT credentials to Praneeth Sai...")
        now = utcnow()
        juit_name = 'Jaypee University of Information Technology'

        credentials_plan = [
            (
                'DEGREE',
                'Bachelor of Technology in Computer Science & Engineering',
                45,
                None,
                ['with First Class Honours & Distinction', 'Cumulative GPA: 9.42 / 10.0 · Batch 2026-2030'],
                {'cgpa': '9.42', 'division': 'First Class Honours & Distinction', 'batch': '2026-2030', 'roll_number': '22103050'}
            ),
            (
                'MARKSHEET',
                'Consolidated Grade Marksheet — Semesters I to VIII',
                40,
                None,
                ['Overall Academic Aggregate: 94.2%', 'All 160 Professional Engineering Credits Cleared'],
                {'aggregate': '94.2%', 'credits_completed': '160', 'semesters': '8'}
            ),
            (
                'CBSE_MARKSHEET',
                'Central Board of Secondary Education — Class XII Senior School Certificate Marksheet',
                800,
                None,
                ['All India Senior School Certificate Examination (AISSCE)', 'Aggregate: 96.4% · Distinction in all subjects'],
                {'board': 'Central Board of Secondary Education', 'examination': 'AISSCE Class XII', 'aggregate': '96.4%', 'roll_number': '22103050'}
            ),
            (
                'ICSE_MARKSHEET',
                'Indian Certificate of Secondary Education — Class X Certificate Marksheet',
                1500,
                None,
                ['Council for the Indian School Certificate Examinations (ICSE)', 'Aggregate: 95.8% · Science & Mathematics High Honors'],
                {'board': 'Council for the Indian School Certificate Examinations', 'examination': 'ICSE Class X', 'aggregate': '95.8%', 'roll_number': '22103050'}
            ),
            (
                'INTERNSHIP',
                'Summer Research & Blockchain Engineering Internship Certificate',
                120,
                None,
                ['Project Aegis Cryptographic Ledger Architecture · 10 Weeks', 'Performance Rating: Exemplary (O Grade)'],
                {'duration_weeks': '10', 'organization': 'Satyameva Labs', 'rating': 'Exemplary'}
            ),
            (
                'BONAFIDE',
                'Bonafide Student Certificate',
                30,
                None,
                ['Enrolled as a full-time regular bonafide undergraduate scholar', 'Department of Computer Science & Engineering'],
                {'purpose': 'Global Academic & Industry Verification'}
            ),
            (
                'TC',
                'Transfer Certificate',
                15,
                None,
                ['Character & Conduct: Exemplary', 'No Institutional Dues Outstanding · Clear Standing'],
                {'conduct': 'Exemplary', 'dues': 'Cleared'}
            ),
            (
                'MIGRATION',
                'Official Institutional Migration Certificate',
                10,
                None,
                ['Permitted to migrate to recognized national and global academic institutions', 'Seal of Registrar Affixed'],
                {'status': 'Clearance Granted'}
            ),
        ]

        created_docs = []
        for doc_type, title, days_ago, validity, lines, extra in credentials_plan:
            issued_on = now - timedelta(days=days_ago)
            cert_img = make_certificate_image(
                title=title,
                student_name=praneeth_student.full_name,
                roll=praneeth_student.roll_number,
                program=praneeth_student.program,
                institution=juit_name,
                issued_on=issued_on,
                extra_lines=lines,
            )
            doc = issue_credential(
                student=praneeth_student,
                issuer=issuer_user,
                doc_type=doc_type,
                title=title,
                file_bytes=cert_img,
                file_name=f"{doc_type.lower()}_{praneeth_student.roll_number}.png",
                file_mime="image/png",
                validity_days=validity,
                issued_on=issued_on,
                extra=extra,
            )
            created_docs.append(doc)
            print(f"  · Block #{doc.block_index:>2}: {doc_type:<11} {doc.doc_hash[:16]}... (Mining PoW Diff 4 OK)")

        # ---- 4. Verification History Telemetry ----
        print("[5/5] Adding realistic verification audit logs...")
        degree_doc, marksheet_doc = created_docs[0], created_docs[1]
        bonafide_doc = created_docs[3]

        history_events = [
            (degree_doc, 'TCS · Global Background Screening', RESULT_VALID, 2, 'QR'),
            (degree_doc, 'Infosys Ltd. · Academic Verification Desk', RESULT_VALID, 5, 'HASH'),
            (marksheet_doc, 'Wipro Technologies · Talent Screening', RESULT_VALID, 8, 'QR'),
            (bonafide_doc, 'Corporate Background Verifications Ltd.', RESULT_VALID, 12, 'QR'),
            (degree_doc, 'Anonymous Verifier (Public Portal)', RESULT_VALID, 15, 'QR'),
        ]

        for doc, verifier_org, result, days_ago, method in history_events:
            log = VerificationLog(
                doc_id=doc.id,
                verifier_id=verifier_user.id if 'Corporate' in verifier_org else None,
                verifier_label=verifier_org,
                queried_hash=doc.doc_hash,
                result=result,
                method=method,
                timestamp=now - timedelta(days=days_ago),
                ipv4='127.0.0.1',
                user_agent='Satyameva Aegis Verifier Agent / 2.0',
            )
            db.session.add(log)
            doc.verification_count = (doc.verification_count or 0) + 1
            doc.last_verified_at = now - timedelta(days=days_ago)

        db.session.commit()
        print("[OK] Verification telemetry committed.")

        print("\n" + "="*60)
        print("SATYAMEVA AEGIS -- CLEAN 4-ROLE CONFIGURATION COMPLETE")
        print("="*60)
        print("1. Superadmin Portal (/admin/):")
        print("   Username: superadmin")
        print("   Password: Satyameva@2026")
        print("   Email:    superadmin@satyameva.in\n")

        print("2. University Issuer Portal (/issuer/):")
        print("   Username: juit.registrar")
        print("   Password: Juit@2026")
        print("   Email:    registrar@juit.ac.in")
        print("   Campus:   Jaypee University of Information Technology (JUIT)\n")

        print("3. Student Portal & Wallet (/student/dashboard):")
        print("   Username: praneeth  (also supports roll '22103050' or email)")
        print("   Password: Praneeth@2026")
        print("   Email:    praneethsai050@gmail.com (Google OAuth Linked)")
        print("   Name:     Praneeth Sai")
        print("   Roll:     22103050")
        print("   Program:  B.Tech CSE (Batch 2026-2030)")
        print("   DOB:      01/09/2008 (AES-256 PDF Password: 01092008)")
        print("   Campus:   Jaypee University of Information Technology (JUIT)\n")

        print("4. Corporate Verifier Portal (/verifier/dashboard & /verify):")
        print("   Username: verifier")
        print("   Password: Verifier@2026")
        print("   Email:    verifier@corporate.in")
        print("   Org:      Corporate Background Verifications Ltd.\n")
        print("="*60)


if __name__ == '__main__':
    setup_portals()
