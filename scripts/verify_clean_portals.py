import sys
sys.path.append(r"C:\Users\hp\OneDrive\Desktop\Satyameva")
from app import create_app
from extensions import db
from models.user import User
from models.student import Student
from models.document import Doc
from models.institution import Institution
from models.block import Block
import blockchain

app = create_app()
with app.app_context():
    print("=== USERS ===")
    for u in User.query.all():
        print(f"User #{u.id}: {u.username:<16} | role={u.role:<10} | email={u.email}")
    assert User.query.count() == 4, f"Expected 4 users, got {User.query.count()}"

    print("\n=== STUDENTS ===")
    for s in Student.query.all():
        print(f"Student #{s.id}: {s.full_name} | roll={s.roll_number} | inst={s.institution} | batch={s.batch} | dob={s.dob}")
    assert Student.query.count() == 1, f"Expected 1 student, got {Student.query.count()}"

    print("\n=== CREDENTIALS ===")
    for d in Doc.query.all():
        print(f"Doc #{d.id}: {d.doc_type:<10} | title={d.title[:35]:<35} | block={d.block_index}")
    assert Doc.query.count() == 6, f"Expected 6 docs, got {Doc.query.count()}"

    print("\n=== BLOCKCHAIN VALIDATION ===")
    is_valid, reason = blockchain.validate_chain()
    print(f"Blockchain Valid: {is_valid} (Reason: {reason})")
    assert is_valid, "Blockchain validation failed!"

    # Test login for all 4 roles via test client
    print("\n=== AUTHENTICATION TESTS ===")
    client = app.test_client()
    test_cases = [
        ('superadmin', 'Satyameva@2026', '/admin/'),
        ('juit.registrar', 'Juit@2026', '/issuer/'),
        ('praneeth', 'Praneeth@2026', '/student/dashboard'),
        ('22103050', 'Praneeth@2026', '/student/dashboard'),
        ('praneethsai050', 'Praneeth@2026', '/student/dashboard'),
        ('verifier', 'Verifier@2026', '/verifier/dashboard'),
    ]

    for ident, pw, expected_url in test_cases:
        client.get('/logout')
        res = client.post('/login', data={'identifier': ident, 'password': pw}, follow_redirects=False)
        loc = res.headers.get("Location", "none")
        print(f"Login with '{ident}': status={res.status_code}, redirect={loc}")
        assert res.status_code == 302, f"Login failed for {ident}"
        assert expected_url in loc, f"Expected redirect to {expected_url}, got {loc}"

print("\nALL VERIFICATIONS PASSED 100%!")
