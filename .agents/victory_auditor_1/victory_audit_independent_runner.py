"""
Independent Victory Auditor Execution Runner
Satyameva Credentialing System — Bulk Issuance Feature Verification

This script executes a completely independent audit harness covering:
- AC1: All-or-Nothing CSV validation & missing column handling (0 docs, 0 blocks)
- AC2: 3-row valid batch execution (creates 3 Docs, mines 3 sequential blocks, links PoW)
- AC3: Student dashboard, document detail, stamped PDF certificate, and public verification
- AC4: Sample template.csv served and validated
- R1: Bulk Issue UI elements, file upload accept=".csv", and sample template links
"""
import hashlib
import io
import json
import os
import random
import shutil
import string
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import config
from app import create_app
from blockchain import blockchain_instance, validate_chain
from extensions import db
from models.block import Block
from models.document import DOC_TYPES, STATUS_VALID, Doc
from models.student import Student
from models.user import ROLE_ISSUER, ROLE_STUDENT, ROLE_VERIFIER, User
from security import hash_password, make_qr_token


class IndependentVictoryAuditTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix='victory_audit_')
        self.temp_db_path = os.path.join(self.temp_dir, 'audit_satyameva.db')
        self.temp_chain_path = os.path.join(self.temp_dir, 'audit_blockchain.json')

        self.old_db_url = os.environ.get('DATABASE_URL')
        os.environ['DATABASE_URL'] = f'sqlite:///{self.temp_db_path}'

        self.old_base_uri = config.BaseConfig.SQLALCHEMY_DATABASE_URI
        self.old_dev_uri = config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI
        self.old_prod_uri = config.ProductionConfig.SQLALCHEMY_DATABASE_URI
        self.old_mail_suppress = config.BaseConfig.MAIL_SUPPRESS_SEND
        config.BaseConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.temp_db_path}'
        config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.temp_db_path}'
        config.ProductionConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.temp_db_path}'
        config.BaseConfig.MAIL_SUPPRESS_SEND = True
        config.DevelopmentConfig.MAIL_SUPPRESS_SEND = True
        config.ProductionConfig.MAIL_SUPPRESS_SEND = True

        self.orig_chain_file = blockchain_instance.storage_file
        self.orig_chain_diff = blockchain_instance.difficulty
        blockchain_instance.storage_file = self.temp_chain_path
        blockchain_instance.difficulty = 2

        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'MAIL_SUPPRESS_SEND': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.temp_db_path}',
            'POW_DIFFICULTY': 2,
        })

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()
        blockchain_instance.ensure_genesis_block()

        self.client = self.app.test_client()

        # Create test issuer
        salt, p_hash, iters = hash_password('AuditPass123!')
        self.issuer_user = User(
            username='audit.issuer',
            email='audit.issuer@audit-univ.ac.in',
            role=ROLE_ISSUER,
            organization='Audit State University',
            password_salt=salt,
            password_hash=p_hash,
            password_iterations=iters,
        )
        db.session.add(self.issuer_user)
        db.session.commit()

        # Login as issuer
        self.client.post('/login', data={'identifier': 'audit.issuer', 'password': 'AuditPass123!'})

    def tearDown(self):
        db.session.remove()
        try:
            db.drop_all()
        except Exception:
            pass
        try:
            db.engine.dispose()
        except Exception:
            pass
        self.app_context.pop()

        blockchain_instance.storage_file = self.orig_chain_file
        blockchain_instance.difficulty = self.orig_chain_diff

        config.BaseConfig.SQLALCHEMY_DATABASE_URI = self.old_base_uri
        config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI = self.old_dev_uri
        config.ProductionConfig.SQLALCHEMY_DATABASE_URI = self.old_prod_uri
        config.BaseConfig.MAIL_SUPPRESS_SEND = self.old_mail_suppress
        config.DevelopmentConfig.MAIL_SUPPRESS_SEND = self.old_mail_suppress
        config.ProductionConfig.MAIL_SUPPRESS_SEND = self.old_mail_suppress

        if self.old_db_url is not None:
            os.environ['DATABASE_URL'] = self.old_db_url
        else:
            os.environ.pop('DATABASE_URL', None)

        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def _upload_csv(self, csv_data: str | bytes, filename='batch.csv'):
        if isinstance(csv_data, str):
            raw = csv_data.encode('utf-8')
        else:
            raw = csv_data
        data = {
            'csv_file': (io.BytesIO(raw), filename),
        }
        return self.client.post('/issuer/bulk-issue', data=data, follow_redirects=False)

    # --------------------------------------------------------------------------
    # AC1: All-or-Nothing CSV Validation & Missing Required Columns
    # --------------------------------------------------------------------------
    def test_ac1_missing_required_columns_and_zero_records(self):
        """AC1: Submitting CSV with missing required columns immediately returns an error and creates 0 documents & 0 blocks."""
        docs_before = Doc.query.count()
        blocks_before = Block.query.count()

        # Case A: Missing roll_number
        r1 = self._upload_csv("doc_type,title\nDEGREE,B.Sc Physics\n")
        self.assertEqual(r1.status_code, 400)
        self.assertIn(b"Missing required CSV column", r1.data)
        self.assertEqual(Doc.query.count(), docs_before)
        self.assertEqual(Block.query.count(), blocks_before)

        # Case B: Missing doc_type
        r2 = self._upload_csv("roll_number,title\n99901,B.Sc Physics\n")
        self.assertEqual(r2.status_code, 400)
        self.assertIn(b"Missing required CSV column", r2.data)
        self.assertEqual(Doc.query.count(), docs_before)
        self.assertEqual(Block.query.count(), blocks_before)

        # Case C: Missing title
        r3 = self._upload_csv("roll_number,doc_type\n99901,DEGREE\n")
        self.assertEqual(r3.status_code, 400)
        self.assertIn(b"Missing required CSV column", r3.data)
        self.assertEqual(Doc.query.count(), docs_before)
        self.assertEqual(Block.query.count(), blocks_before)

    def test_ac1_all_or_nothing_atomic_rollback_on_single_invalid_row(self):
        """AC1: If ANY row fails validation (e.g. invalid doc_type or missing field), the entire batch fails with 0 docs/blocks."""
        docs_before = Doc.query.count()
        blocks_before = Block.query.count()

        csv_content = (
            "roll_number,student_name,doc_type,title\n"
            "202601,Aarav,DEGREE,B.Tech CSE\n"
            "202602,Diya,MARKSHEET,Grade Card\n"
            "202603,Rohan,INVALID_TYPE,Certificate\n"  # Invalid doc_type in row 3!
            "202604,Kabir,BONAFIDE,Bonafide\n"
        )
        resp = self._upload_csv(csv_content)
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b"Invalid doc_type", resp.data)
        self.assertIn(b"INVALID_TYPE", resp.data)
        self.assertEqual(Doc.query.count(), docs_before, "Partial docs were created on invalid batch!")
        self.assertEqual(Block.query.count(), blocks_before, "Partial blocks were mined on invalid batch!")

    # --------------------------------------------------------------------------
    # AC2: Valid 3-Row Batch Creates Exactly 3 Docs and Mines 3 Blocks
    # --------------------------------------------------------------------------
    def test_ac2_valid_3_row_batch_creates_3_docs_and_mines_3_blocks(self):
        """AC2: Submitting a valid CSV with 3 rows successfully creates exactly 3 new Doc records and mines 3 new blocks."""
        docs_before = Doc.query.count()
        blocks_before = Block.query.count()
        last_block_before = Block.query.order_by(Block.index.desc()).first()
        prev_hash = last_block_before.hash if last_block_before else '0'*64
        prev_proof = last_block_before.proof if last_block_before else 1

        rnd = ''.join(random.choices(string.digits, k=5))
        r1, r2, r3 = f"AUD_{rnd}_1", f"AUD_{rnd}_2", f"AUD_{rnd}_3"

        csv_content = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            f"{r1},Student Alpha,DEGREE,Bachelor of Technology in Robotics,3650\n"
            f"{r2},Student Beta,MARKSHEET,Consolidated Semester Marksheet,3650\n"
            f"{r3},Student Gamma,INTERNSHIP,AI Research Internship,730\n"
        )

        resp = self._upload_csv(csv_content)
        self.assertEqual(resp.status_code, 302)
        loc = resp.headers.get('Location', '')
        self.assertTrue('/issuer' in loc or '/dashboard' in loc, f"Unexpected redirect target: {loc}")

        docs_after = Doc.query.count()
        blocks_after = Block.query.count()

        self.assertEqual(docs_after, docs_before + 3, "Exactly 3 Doc records must be created")
        self.assertEqual(blocks_after, blocks_before + 3, "Exactly 3 Block records must be mined")

        # Verify documents
        created_docs = Doc.query.order_by(Doc.id.desc()).limit(3).all()[::-1]
        self.assertEqual(len(created_docs), 3)

        for d in created_docs:
            self.assertIsNone(d.file_data, "Bulk issued document must be text-only (file_data is None)")
            self.assertIsNotNone(d.doc_hash, "doc_hash must be computed")
            self.assertEqual(len(d.doc_hash), 64, "doc_hash must be 64-char SHA-256")
            self.assertIsNotNone(d.block_index, "block_index must be assigned")

        # Verify blocks and blockchain continuity
        created_blocks = Block.query.order_by(Block.index.desc()).limit(3).all()[::-1]
        self.assertEqual(len(created_blocks), 3)

        expected_prev_hash = prev_hash
        current_prev_proof = prev_proof
        for b in created_blocks:
            self.assertEqual(b.previous_hash, expected_prev_hash, "Block chain link broken")
            # Verify PoW target on mined proof
            pow_guess = hashlib.sha256(f'{current_prev_proof}{b.proof}{b.index}'.encode('utf-8')).hexdigest()
            self.assertTrue(pow_guess.startswith('0000'), f"PoW guess does not meet difficulty target: {pow_guess}")
            expected_prev_hash = b.hash
            current_prev_proof = b.proof

        # Verify overall chain integrity
        chain_ok, chain_msg = validate_chain()
        self.assertTrue(chain_ok, f"Blockchain integrity failed: {chain_msg}")

    # --------------------------------------------------------------------------
    # AC3: Text-Only Credential Multi-View Safe Rendering
    # --------------------------------------------------------------------------
    def test_ac3_text_only_credential_dashboard_and_public_verify_resilience(self):
        """AC3: Generated text-only credentials can be viewed on student dashboard and public verify page without crashing."""
        rnd = ''.join(random.choices(string.digits, k=5))
        roll = f"ROLL_{rnd}"
        sname = f"Audit Student {rnd}"

        csv_content = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            f"{roll},{sname},DEGREE,Bachelor of Science in Mathematics,3650\n"
        )
        resp = self._upload_csv(csv_content)
        self.assertEqual(resp.status_code, 302)

        doc = Doc.query.filter_by(title='Bachelor of Science in Mathematics').order_by(Doc.id.desc()).first()
        self.assertIsNotNone(doc)
        student = Student.query.filter_by(roll_number=roll).first()
        self.assertIsNotNone(student)
        student_user = db.session.get(User, student.user_id)

        # 1. Sign out issuer, sign in as Student
        self.client.get('/logout')
        r_log = self.client.post('/login', data={'identifier': student_user.username, 'password': 'satyameva123'}, follow_redirects=True)
        self.assertEqual(r_log.status_code, 200)

        # 2. Student Portal Dashboard View
        r_dash = self.client.get('/student/dashboard')
        self.assertEqual(r_dash.status_code, 200, "Student dashboard crashed on text-only credential")
        self.assertIn(b"Bachelor of Science in Mathematics", r_dash.data)
        self.assertIn(b"DEGREE", r_dash.data)

        # 3. Student Document Detail View
        r_det = self.client.get(f'/student/document/{doc.id}')
        self.assertEqual(r_det.status_code, 200, "Document detail crashed on text-only credential")
        self.assertIn(doc.doc_hash.encode('utf-8'), r_det.data)
        self.assertIn(b"Blockchain record", r_det.data)

        # 4. Download Stamped Certificate PDF
        r_pdf = self.client.get(f'/student/document/{doc.id}/download')
        self.assertEqual(r_pdf.status_code, 200, "PDF download crashed on text-only credential")
        self.assertTrue(r_pdf.data.startswith(b'%PDF'), "PDF download did not return valid PDF header")

        # 5. Public Verify Permanent URL (Anonymous client)
        self.client.get('/logout')
        r_pub = self.client.get(f'/v/{doc.doc_hash}')
        self.assertEqual(r_pub.status_code, 200, "Public verify page crashed on text-only credential")
        self.assertIn(b"Authentic credential", r_pub.data)
        self.assertIn(roll.encode('utf-8'), r_pub.data)

        # 6. Public Verify Dynamic QR Token URL
        token, _ = make_qr_token(doc.doc_hash, self.app.config['SECRET_KEY'], ttl=60)
        r_qr = self.client.get(f'/v/{doc.doc_hash}?t={token}')
        self.assertEqual(r_qr.status_code, 200, "Live QR verification crashed on text-only credential")
        self.assertIn(b"Live QR scan", r_qr.data)
        self.assertIn(b"Authentic credential", r_qr.data)

    # --------------------------------------------------------------------------
    # AC4: Sample template.csv Served with Proper Headers
    # --------------------------------------------------------------------------
    def test_ac4_sample_template_csv_served_with_proper_headers(self):
        """AC4: Sample template.csv is correctly served and contains the proper headers."""
        resp = self.client.get('/issuer/sample-csv')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp.headers.get('Content-Type', ''))

        csv_text = resp.data.decode('utf-8')
        lines = [l.strip() for l in csv_text.splitlines() if l.strip()]
        header = [c.strip().lower() for c in lines[0].split(',')]

        self.assertIn('roll_number', header)
        self.assertIn('doc_type', header)
        self.assertIn('title', header)
        self.assertGreater(len(lines), 1, "Template CSV must contain sample data rows")

    # --------------------------------------------------------------------------
    # R1: Bulk Issue UI Elements & Accessibility
    # --------------------------------------------------------------------------
    def test_r1_bulk_issue_ui_page_elements(self):
        """R1: Verify Bulk Issue page contains CSV file upload input restricted to .csv and template download link."""
        resp = self.client.get('/issuer/bulk-issue')
        self.assertEqual(resp.status_code, 200)
        html = resp.data.decode('utf-8')
        self.assertIn('enctype="multipart/form-data"', html)
        self.assertIn('name="csv_file"', html)
        self.assertIn('accept=".csv"', html)
        self.assertTrue('/issuer/sample-csv' in html or '/issuer/template.csv' in html)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(IndependentVictoryAuditTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
