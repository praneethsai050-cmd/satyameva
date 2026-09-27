"""
Demo data seeder.

    python seed.py           # create demo accounts + credentials
    python seed.py --reset   # wipe the database first

Generates real certificate images with Pillow so the document preview and the
digital stamping pipeline have something genuine to work on — the portal is
much easier to judge when the pages are not empty.
"""
import argparse
import os
import sys
from datetime import timedelta
from io import BytesIO

from PIL import Image, ImageDraw

from app import create_app
from extensions import db, utcnow
from models.document import Doc
from models.institution import Institution
from models.student import Student
from models.user import ROLE_ADMIN, ROLE_ISSUER, ROLE_STUDENT, ROLE_VERIFIER, User
from models.verification_log import (
    RESULT_EXPIRED, RESULT_NOT_FOUND, RESULT_VALID, VerificationLog,
)
from security import hash_password
from services.credential_service import issue_credential
# Reuse the stamp service's font resolution and fitting so the sample artwork
# matches the look of the generated verification pages.
from services.stamp_service import _fit_font, _font

DEMO_PASSWORD = 'satyameva123'


# ─── Sample certificate artwork ───────────────────────────────────────────────
def make_certificate_image(title, student_name, roll, program, institution,
                           issued_on, extra_lines=()) -> bytes:
    """Draw a plausible-looking certificate so previews are not placeholders."""
    W, H = 1400, 990
    img = Image.new('RGB', (W, H), (253, 252, 248))
    draw = ImageDraw.Draw(img)

    # Ornamental double border.
    draw.rectangle([18, 18, W - 18, H - 18], outline=(150, 130, 70), width=6)
    draw.rectangle([34, 34, W - 34, H - 34], outline=(196, 178, 120), width=2)

    f_inst = _font(44, bold=True)
    f_kicker = _font(22)
    f_body = _font(26)
    f_name = _font(52, bold=True)
    f_small = _font(21)

    def centered(text, y, font, fill):
        left, _, right, _ = draw.textbbox((0, 0), text, font=font)
        draw.text(((W - (right - left)) / 2, y), text, font=font, fill=fill)

    centered(institution.upper(), 78, f_inst, (28, 34, 82))
    centered('Estd. 1962  ·  Government of India  ·  UGC Recognised', 136, f_kicker,
             (120, 124, 150))
    draw.line([(300, 178), (W - 300, 178)], fill=(196, 178, 120), width=3)

    # Long degree names have to shrink rather than run off the page.
    f_title = _fit_font(draw, title.upper(), W - 200, start=60, bold=True, minimum=26)
    centered(title.upper(), 226, f_title, (150, 130, 70))
    centered('This is to certify that', 330, f_body, (70, 74, 98))
    centered(student_name, 378, f_name, (28, 34, 82))
    centered(f'Roll Number {roll}', 452, f_body, (70, 74, 98))
    centered(f'has successfully completed {program}', 500, f_body, (70, 74, 98))

    y = 560
    for line in extra_lines:
        centered(line, y, f_body, (70, 74, 98))
        y += 44

    centered(f'Issued on {issued_on.strftime("%d %B %Y")}', y + 30, f_small, (120, 124, 150))

    # Signature blocks.
    for x, label in ((250, 'Controller of Examinations'), (W - 250 - 320, 'Registrar')):
        draw.line([(x, H - 170), (x + 320, H - 170)], fill=(90, 94, 120), width=2)
        draw.text((x + 40, H - 158), label, font=f_small, fill=(90, 94, 120))

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


# ─── Seeding ──────────────────────────────────────────────────────────────────
def make_user(username, email, role, organization=None):
    existing = User.query.filter_by(username=username).first()
    if existing:
        return existing
    salt, digest, iterations = hash_password(DEMO_PASSWORD)
    user = User(username=username, email=email, role=role, organization=organization,
                password_salt=salt, password_hash=digest, password_iterations=iterations)
    db.session.add(user)
    db.session.flush()
    return user


def seed(reset: bool = False):
    app = create_app()

    with app.app_context():
        if reset:
            db.drop_all()
            db.create_all()
            from blockchain import ensure_genesis_block
            ensure_genesis_block()
            print('· database reset')

        if Doc.query.count() and not reset:
            print('Demo data already present. Re-run with --reset to rebuild.')
            return

        # ---- Institutions (Jaypee Group) ----
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

        inst_map = {}
        for c in campuses:
            inst = Institution.query.filter_by(short_code=c['short_code']).first()
            if not inst:
                inst = Institution(
                    name=c['name'],
                    short_code=c['short_code'],
                    domain=c['domain'],
                    address=c['address'],
                    is_approved=True,
                    approved_at=utcnow(),
                )
                db.session.add(inst)
                db.session.flush()
                print(f"· institution {c['short_code']} ({c['name']}) created")
            inst_map[c['short_code']] = inst

        jiit_inst = inst_map['JIIT']

        # ---- Admin account ----
        admin = make_user('satyameva.admin', 'admin@satyameva.edu', ROLE_ADMIN)
        admin.institution_id = jiit_inst.id
        db.session.flush()
        print(f'· admin    satyameva.admin / {DEMO_PASSWORD}')

        # ---- Accounts ----
        issuer = make_user('jiit.registrar', 'registrar@jiit.ac.in', ROLE_ISSUER,
                           organization='Jaypee Institute of Information Technology')
        issuer.institution_id = jiit_inst.id
        for inst in inst_map.values():
            inst.approved_by_id = admin.id
        make_user('infosys.hr', 'hr@infosys.com', ROLE_VERIFIER, organization='Infosys Ltd.')

        student_user = make_user('aarav.sharma', 'aarav.sharma@student.jiit.ac.in', ROLE_STUDENT)
        peer_user = make_user('priya.nair', 'priya.nair@student.jiit.ac.in', ROLE_STUDENT)

        institution = 'Jaypee Institute of Information Technology'

        student = Student.query.filter_by(user_id=student_user.id).first() or Student(
            user_id=student_user.id, full_name='Aarav Sharma', roll_number='22103045',
            department='Computer Science & Engineering', program='B.Tech CSE',
            batch='2022-2026', institution=institution,
        )
        peer = Student.query.filter_by(user_id=peer_user.id).first() or Student(
            user_id=peer_user.id, full_name='Priya Nair', roll_number='22103112',
            department='Electronics & Communication', program='B.Tech ECE',
            batch='2022-2026', institution=institution,
        )
        db.session.add_all([student, peer])
        db.session.commit()

        now = utcnow()

        # ---- Credentials, spanning every status the UI renders ----
        # (doc_type, title, days_ago_issued, validity_days, extra certificate lines)
        plan = [
            ('DEGREE', 'Bachelor of Technology in Computer Science', 40, 3650,
             ['with First Class Distinction', 'CGPA 8.94 / 10.0'],
             {'cgpa': '8.94', 'division': 'First Class Distinction', 'year': '2026'}),
            ('MARKSHEET', 'Consolidated Marksheet — Semesters I to VIII', 38, 3650,
             ['Aggregate 89.4%', 'All 48 courses cleared'],
             {'aggregate': '89.4', 'semesters': '8'}),
            ('INTERNSHIP', 'Summer Internship Certificate — Backend Engineering', 300, 730,
             ['8 weeks · Bengaluru', 'Performance rating: Outstanding'],
             {'duration_weeks': '8', 'rating': 'Outstanding'}),
            # Expires in ~12 days -> lands in the "Expiring Soon" bucket.
            ('BONAFIDE', 'Bonafide Student Certificate', 78, 90,
             ['Enrolled as a bonafide full-time student'], {'purpose': 'Visa application'}),
            # Already past its window -> "Expired".
            ('TC', 'Transfer Certificate', 260, 180,
             ['Conduct: Satisfactory', 'No dues outstanding'], {'conduct': 'Satisfactory'}),
            ('MIGRATION', 'Migration Certificate', 30, 365,
             ['Permitted to migrate to any recognised university'], {}),
        ]

        created: list[Doc] = []
        for doc_type, title, days_ago, validity, lines, extra in plan:
            issued_on = now - timedelta(days=days_ago)
            image = make_certificate_image(
                title=title, student_name=student.full_name, roll=student.roll_number,
                program=student.program, institution=institution,
                issued_on=issued_on, extra_lines=lines,
            )
            doc = issue_credential(
                student, issuer, doc_type, title,
                file_bytes=image,
                file_name=f'{doc_type.lower()}_{student.roll_number}.png',
                file_mime='image/png',
                validity_days=validity,
                issued_on=issued_on,
                extra=extra,
            )
            created.append(doc)
            print(f'  · block #{doc.block_index:>2}  {doc_type:<11} {doc.status:<9} '
                  f'{doc.doc_hash[:16]}…')

        # One revoked credential on the peer account, so the fraud path is visible
        # without polluting the primary demo student's dashboard.
        peer_doc = issue_credential(
            peer, issuer, 'DEGREE', 'Bachelor of Technology in Electronics',
            file_bytes=make_certificate_image(
                'Bachelor of Technology in Electronics', peer.full_name, peer.roll_number,
                peer.program, institution, now - timedelta(days=50), ['CGPA 8.10 / 10.0'],
            ),
            file_name=f'degree_{peer.roll_number}.png', file_mime='image/png',
            issued_on=now - timedelta(days=50), extra={'cgpa': '8.10'},
        )
        peer_doc.revoked = True
        peer_doc.revoked_reason = 'Flagged during a post-issuance academic audit.'

        # ---- Verification history ----
        degree, marksheet = created[0], created[1]
        expired_tc = created[4]

        history = [
            (degree, 'Infosys Ltd. · Talent Acquisition', RESULT_VALID, 2, 'QR'),
            (degree, 'TCS · Background Verification', RESULT_VALID, 6, 'HASH'),
            (degree, 'Anonymous verifier', RESULT_VALID, 14, 'QR'),
            (marksheet, 'University of Toronto · Admissions', RESULT_VALID, 9, 'HASH'),
            (marksheet, 'Anonymous verifier', RESULT_VALID, 21, 'QR'),
            (expired_tc, 'Delhi Public School · Admissions', RESULT_EXPIRED, 3, 'HASH'),
        ]

        verifier_user = make_user('infosys.hr', 'hr@infosys.com', ROLE_VERIFIER, organization='Infosys Ltd.')

        for doc, label, result, days_ago, method in history:
            v_id = verifier_user.id if 'Infosys' in label else None
            db.session.add(VerificationLog(
                doc_id=doc.id, verifier_id=v_id, verifier_label=label, queried_hash=doc.doc_hash,
                timestamp=now - timedelta(days=days_ago, hours=days_ago * 2 % 11),
                ipv4='103.21.58.14', ipv6='2405:201:a00c:18a2::c0de',
                user_agent='Mozilla/5.0 (demo verifier)', method=method, result=result,
            ))
            if result == RESULT_VALID:
                doc.verification_count = (doc.verification_count or 0) + 1
                if doc.last_verified_at is None or doc.last_verified_at < now - timedelta(days=days_ago):
                    doc.last_verified_at = now - timedelta(days=days_ago)

                # Seed notification for student
                from models.notification import Notification
                db.session.add(Notification(
                    student_id=doc.student_id,
                    doc_id=doc.id,
                    title=f'{doc.type_label} Verified',
                    message=f'Your {doc.title} was successfully verified by {label}.',
                    category='success',
                    verifier_label=label,
                    created_at=now - timedelta(days=days_ago, hours=days_ago * 2 % 11),
                ))

        # A failed lookup, so the log does not look suspiciously clean.
        db.session.add(VerificationLog(
            doc_id=None, verifier_id=None, verifier_label='Unknown (forged hash)',
            queried_hash='f' * 64, timestamp=now - timedelta(days=5),
            ipv4='45.116.203.7', method='HASH', result=RESULT_NOT_FOUND,
        ))

        db.session.commit()

        from blockchain import chain_length, validate_chain
        ok, message = validate_chain()

        print()
        print('  Demo data ready.')
        print(f'  Chain: {chain_length()} blocks — {message}')
        print()
        print('  Sign in at  http://127.0.0.1:5000/login')
        print(f'    admin     satyameva.admin / {DEMO_PASSWORD}  (global admin)')
        print(f'    student   aarav.sharma   / {DEMO_PASSWORD}   (6 credentials)')
        print(f'    student   priya.nair     / {DEMO_PASSWORD}   (1 revoked credential)')
        print(f'    issuer    jiit.registrar / {DEMO_PASSWORD}')
        print(f'    verifier  infosys.hr     / {DEMO_PASSWORD}')
        if not ok:
            print('  ! chain validation failed', file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialize Satyameva database.')
    parser.add_argument('--reset', action='store_true',
                        help='drop and recreate all tables first')
    parser.add_argument('--demo', action='store_true',
                        help='seed demo accounts and dummy documents')
    args = parser.parse_args()

    if args.demo:
        seed(reset=args.reset)
    else:
        from init_db import init_production_db
        init_production_db()
