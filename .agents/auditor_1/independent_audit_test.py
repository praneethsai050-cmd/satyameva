"""
Forensic Auditor Empirical Verification Script.
Conducts independent, adversarial, randomized tests against the Bulk Issuance implementation.
"""
import io
import os
import random
import string
import sys
import tempfile
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from blockchain import blockchain_instance, validate_chain
from extensions import db
from models.block import Block
from models.document import DOC_TYPES, Doc
from models.student import Student
from models.user import ROLE_ISSUER, ROLE_STUDENT, User
from security import hash_password


def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def run_forensic_checks():
    print("======================================================================")
    print(" STARTING INDEPENDENT FORENSIC INTEGRITY AUDIT")
    print("======================================================================")
    
    results = {}
    
    # -------------------------------------------------------------------------
    # Check 1: Dynamic CSV Parsing with Randomized Fuzzing
    # -------------------------------------------------------------------------
    print("\n--- Check 1: Dynamic CSV Parsing & Variable Payload Integrity ---")
    temp_dir = tempfile.mkdtemp(prefix='audit_test_')
    temp_db = os.path.join(temp_dir, 'audit.db')
    temp_chain = os.path.join(temp_dir, 'audit_chain.json')
    
    os.environ['DATABASE_URL'] = f'sqlite:///{temp_db}'
    
    import config
    old_base_uri = config.BaseConfig.SQLALCHEMY_DATABASE_URI
    old_dev_uri = config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI
    old_prod_uri = config.ProductionConfig.SQLALCHEMY_DATABASE_URI
    config.BaseConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{temp_db}'
    config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{temp_db}'
    config.ProductionConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{temp_db}'
    
    orig_chain_file = blockchain_instance.storage_file
    orig_diff = blockchain_instance.difficulty
    blockchain_instance.storage_file = temp_chain
    blockchain_instance.difficulty = 2
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'MAIL_SUPPRESS_SEND': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{temp_db}',
        'POW_DIFFICULTY': 2,
    })
    
    with app.app_context():
        db.create_all()
        blockchain_instance.ensure_genesis_block()
        
        # Seed issuer
        salt, digest, iters = hash_password('pass123')
        issuer = User(username='forensic.issuer', email='issuer@audit.org', role=ROLE_ISSUER,
                      organization='Forensic Audit Board', password_salt=salt, password_hash=digest, password_iterations=iters)
        db.session.add(issuer)
        db.session.commit()
        
        client = app.test_client()
        client.post('/login', data={'identifier': 'forensic.issuer', 'password': 'pass123'})
        
        # Generate 10 randomized rows
        random_rows = []
        doc_type_keys = list(DOC_TYPES.keys())
        for i in range(10):
            roll = f"AUDIT-{generate_random_string(6)}"
            name = f"Student {generate_random_string(8)}"
            dtype = random.choice(doc_type_keys)
            title = f"Dynamic Credential {generate_random_string(12)}"
            days = random.randint(30, 3650)
            random_rows.append({'roll_number': roll, 'student_name': name, 'doc_type': dtype, 'title': title, 'validity_days': str(days)})
        
        csv_lines = ["roll_number,student_name,doc_type,title,validity_days"]
        for r in random_rows:
            csv_lines.append(f"{r['roll_number']},{r['student_name']},{r['doc_type']},{r['title']},{r['validity_days']}")
        csv_payload = "\n".join(csv_lines).encode('utf-8')
        
        resp = client.post('/issuer/bulk-issue', data={'csv_file': (io.BytesIO(csv_payload), 'fuzz.csv')}, follow_redirects=True)
        assert resp.status_code == 200, f"Status code: {resp.status_code}"
        
        # Verify all 10 dynamically created docs exist with matching exact properties
        docs = Doc.query.all()
        assert len(docs) == 10, f"Expected 10 docs, got {len(docs)}"
        for r in random_rows:
            matched_doc = Doc.query.filter_by(title=r['title']).first()
            assert matched_doc is not None, f"Dynamic title {r['title']} not found in DB"
            assert matched_doc.doc_type == r['doc_type'], f"Doc type mismatch"
            assert matched_doc.student.roll_number == r['roll_number'], f"Roll mismatch"
            assert matched_doc.student.full_name == r['student_name'], f"Name mismatch"
            assert matched_doc.file_data is None, f"Expected text-only doc (file_data is None)"
            assert len(matched_doc.doc_hash) == 64, f"Invalid hash length"
        
        print(" -> Dynamic CSV parsing verified with randomized payload: 10/10 matched exactly.")
        results['dynamic_csv_parsing'] = 'PASS'
        
        # ---------------------------------------------------------------------
        # Check 2: Proof-of-Work Mining Authenticity & Block Chain Verification
        # ---------------------------------------------------------------------
        print("\n--- Check 2: Proof-of-Work Cryptographic Authenticity ---")
        blocks = Block.query.order_by(Block.index.asc()).all()
        assert len(blocks) == 11, f"Expected Genesis + 10 = 11 blocks, got {len(blocks)}"
        
        for blk in blocks:
            if blk.index == 0:
                assert blk.previous_hash == '0' * 64
            else:
                prev_blk = blocks[blk.index - 1]
                assert blk.previous_hash == prev_blk.hash, f"Block #{blk.index} previous_hash mismatch"
                
                # Check Proof-of-Work target difficulty
                import hashlib
                guess = hashlib.sha256(f"{prev_blk.proof}{blk.proof}{blk.index}".encode('utf-8')).hexdigest()
                assert guess.startswith('0' * 2), f"Block #{blk.index} PoW guess '{guess}' does not meet difficulty 2"
                
                # Compute block hash matches stored hash
                expected_hash = blockchain_instance.compute_block_hash(
                    blk.index, blk.timestamp.isoformat(), blk.data, blk.proof, blk.previous_hash
                )
                assert blk.hash == expected_hash, f"Block #{blk.index} hash mismatch"
                
        ok, msg = validate_chain()
        assert ok, f"Blockchain validate_chain failed: {msg}"
        print(f" -> Proof-of-Work authenticity verified: All blocks genuinely mined with valid SHA-256 nonces.")
        results['pow_mining_authenticity'] = 'PASS'
        
        # ---------------------------------------------------------------------
        # Check 3: All-or-Nothing Atomicity & Zero Partial Issuance Under Mutation
        # ---------------------------------------------------------------------
        print("\n--- Check 3: All-or-Nothing Transaction Atomicity Under Fuzzing ---")
        init_docs = Doc.query.count()
        init_blocks = Block.query.count()
        
        # CSV with 10 rows where row 7 has an invalid doc type
        flawed_csv_lines = ["roll_number,student_name,doc_type,title,validity_days"]
        for idx in range(10):
            dtype = "DEGREE" if idx != 6 else "CORRUPT_TYPE_XYZ"
            flawed_csv_lines.append(f"ROLL-{idx},Student {idx},{dtype},Title {idx},365")
        
        resp_flawed = client.post('/issuer/bulk-issue', data={'csv_file': (io.BytesIO("\n".join(flawed_csv_lines).encode('utf-8')), 'flawed.csv')}, follow_redirects=True)
        assert resp_flawed.status_code in (200, 400)
        
        # Assert ZERO documents created, ZERO blocks mined
        assert Doc.query.count() == init_docs, f"Doc count changed! Was {init_docs}, now {Doc.query.count()}"
        assert Block.query.count() == init_blocks, f"Block count changed! Was {init_blocks}, now {Block.query.count()}"
        print(" -> All-or-Nothing atomicity verified: 0 documents created, 0 blocks mined on 1 invalid row out of 10.")
        results['all_or_nothing_atomicity'] = 'PASS'
        
        # ---------------------------------------------------------------------
        # Check 4: Text-Only Credential Resilience Across Portals
        # ---------------------------------------------------------------------
        print("\n--- Check 4: Text-Only Credential View & Verification Resilience ---")
        first_doc = docs[0]
        student_user = first_doc.student.user
        
        client.get('/logout')
        client.post('/login', data={'identifier': student_user.username, 'password': 'satyameva123'})
        
        # Dashboard
        r_dash = client.get('/student/dashboard')
        assert r_dash.status_code == 200, f"Student dashboard failed: {r_dash.status_code}"
        assert first_doc.title in r_dash.get_data(as_text=True)
        
        # Detail view
        r_det = client.get(f'/student/document/{first_doc.id}')
        assert r_det.status_code == 200, f"Student detail failed: {r_det.status_code}"
        
        # Download Stamped PDF
        r_pdf = client.get(f'/student/document/{first_doc.id}/download')
        assert r_pdf.status_code == 200, f"PDF generation failed: {r_pdf.status_code}"
        assert r_pdf.data.startswith(b'%PDF'), "PDF header invalid"
        
        client.get('/logout')
        
        # Public Verification
        r_pub = client.get(f'/v/{first_doc.doc_hash}')
        assert r_pub.status_code == 200, f"Public verify failed: {r_pub.status_code}"
        assert 'Authentic credential' in r_pub.get_data(as_text=True)
        assert first_doc.title in r_pub.get_data(as_text=True)
        print(" -> Text-only credential resilience verified across Student Dashboard, Detail View, PDF Stamping, and Public Verification.")
        results['text_only_resilience'] = 'PASS'
        
        # ---------------------------------------------------------------------
        # Check 5: Sample Template Availability & Format
        # ---------------------------------------------------------------------
        print("\n--- Check 5: Sample Template Endpoint & Header Verification ---")
        client.post('/login', data={'identifier': 'forensic.issuer', 'password': 'pass123'})
        r_tmpl = client.get('/issuer/sample-csv')
        assert r_tmpl.status_code == 200, f"Sample CSV endpoint returned {r_tmpl.status_code}"
        tmpl_text = r_tmpl.get_data(as_text=True)
        assert 'roll_number' in tmpl_text.lower()
        assert 'doc_type' in tmpl_text.lower()
        assert 'title' in tmpl_text.lower()
        print(" -> Sample template CSV verified: 200 OK with correct headers.")
        results['sample_template'] = 'PASS'

    # Cleanup
    config.BaseConfig.SQLALCHEMY_DATABASE_URI = old_base_uri
    config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI = old_dev_uri
    config.ProductionConfig.SQLALCHEMY_DATABASE_URI = old_prod_uri
    blockchain_instance.storage_file = orig_chain_file
    blockchain_instance.difficulty = orig_diff
    
    print("\n======================================================================")
    print(" ALL FORENSIC INTEGRITY CHECKS COMPLETED SUCCESSFULLY")
    print(f" Summary: {results}")
    print("======================================================================")
    return 0


if __name__ == '__main__':
    sys.exit(run_forensic_checks())
