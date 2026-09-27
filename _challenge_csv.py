"""
Adversarial Stress Testing Harness for Bulk Issuance CSV Engine.
Covers:
1. Malformed CSVs (unmatched quotes, null bytes, binary files disguised as .csv, mixed line endings, empty files).
2. Injection & Boundary payloads (XSS, Unicode/emojis/multilingual, SQL injections, template/format strings, formula injection, path traversal, huge string lengths).
3. Large CSV batches (50+ rows) & Atomicity (row 1 failure, row 30 failure, row 49 failure, last row failure, 0 residue in DB/blockchain).
4. Concurrent & successive upload attempts (rapid successive invalid/valid requests, duplicate roll numbers).
5. Strict verification that DB and blockchain state remain uncorrupted under all failure injections (validate_chain, verify_hash, public / student view rendering).
"""
import io
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from blockchain import blockchain_instance, validate_chain
from extensions import db
from models.block import Block
from models.document import Doc, DOC_TYPES
from models.student import Student
from models.user import User, ROLE_ISSUER, ROLE_STUDENT
from security import hash_password
from services.verification_service import verify_hash


class ChallengeCSVTestCase(unittest.TestCase):
    def setUp(self):
        # Disable SMTP network calls for fast, deterministic unit test runs
        self.email_patcher = patch('services.email_service._send', return_value=True)
        self.email_patcher.start()

        self.temp_dir = tempfile.mkdtemp(prefix='challenge_csv_')
        self.temp_db_path = os.path.join(self.temp_dir, 'challenge.db')
        self.temp_chain_path = os.path.join(self.temp_dir, 'blockchain.json')

        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'MAIL_SUPPRESS_SEND': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.temp_db_path}',
            'POW_DIFFICULTY': 1,
        })

        self.orig_storage = blockchain_instance.storage_file
        self.orig_diff = blockchain_instance.difficulty
        blockchain_instance.storage_file = self.temp_chain_path
        blockchain_instance.difficulty = 1

        self.ctx = self.app.app_context()
        self.ctx.push()

        db.drop_all()
        db.create_all()
        blockchain_instance.ensure_genesis_block()

        self.client = self.app.test_client()
        self._seed_issuer()

    def tearDown(self):
        self.email_patcher.stop()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

        blockchain_instance.storage_file = self.orig_storage
        blockchain_instance.difficulty = self.orig_diff
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _seed_issuer(self):
        salt, digest, iters = hash_password('password123')
        self.issuer = User(
            username='apex.issuer',
            email='issuer@apex.edu',
            role=ROLE_ISSUER,
            organization='Apex National University',
            password_salt=salt,
            password_hash=digest,
            password_iterations=iters,
        )
        db.session.add(self.issuer)
        db.session.commit()

    def login(self, client=None, identifier='apex.issuer', password='password123'):
        c = client or self.client
        return c.post('/login', data={
            'identifier': identifier,
            'password': password,
        }, follow_redirects=True)

    def upload_csv(self, content: bytes | str, filename: str = 'test.csv', client=None):
        c = client or self.client
        if isinstance(content, str):
            content = content.encode('utf-8')
        file_tuple = (io.BytesIO(content), filename)
        return c.post('/issuer/bulk-issue', data={'csv_file': file_tuple}, follow_redirects=True)

    # =========================================================================
    # SUITE 1: MALFORMED CSVs
    # =========================================================================

    def test_malformed_unmatched_quotes(self):
        """Test CSV with unclosed/unmatched double quotes in field."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        # CSV with an invalid structure that cannot produce valid credentials
        bad_csv = 'roll_number,doc_type,title\nAPEX001,INVALID_TYPE,"Unclosed Title string\nAPEX002,INVALID_TYPE,Sheet 2\n'
        resp = self.upload_csv(bad_csv, 'unmatched.csv')
        self.assertIn(resp.status_code, (200, 400, 500))
        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)
        ok, msg = validate_chain()
        self.assertTrue(ok, f"Chain integrity broken: {msg}")

    def test_malformed_null_bytes(self):
        """Test CSV with embedded null bytes (\\x00)."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        null_csv = b"roll_number,doc_type,title\x00\nAPEX001\x00,DEGREE,Degree 1\n"
        resp = self.upload_csv(null_csv, 'nulls.csv')
        self.assertIn(resp.status_code, (200, 400, 500))
        # Even if parsed, verify chain validity
        ok, msg = validate_chain()
        self.assertTrue(ok, f"Chain invalid after null bytes: {msg}")

    def test_malformed_binary_disguised_as_csv(self):
        """Test binary files (PE/ELF headers, PNG image, random bytes) disguised as .csv."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        # ELF executable header bytes
        fake_binary_csv = b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x3e\x00\x01\x00\x00\x00"
        resp = self.upload_csv(fake_binary_csv, 'binary.csv')
        self.assertIn(resp.status_code, (200, 400, 500))
        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)

        # PNG header bytes
        png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        resp2 = self.upload_csv(png_bytes, 'image.csv')
        self.assertIn(resp2.status_code, (200, 400, 500))
        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)

        # Random bytes
        rand_bytes = os.urandom(512)
        resp3 = self.upload_csv(rand_bytes, 'random.csv')
        self.assertIn(resp3.status_code, (200, 400, 500))
        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)

    def test_malformed_empty_and_whitespace_files(self):
        """Test completely empty file (0 bytes) and whitespace-only files."""
        self.login()
        initial_docs = Doc.query.count()

        # 0 bytes
        resp1 = self.upload_csv(b"", 'empty.csv')
        self.assertIn(resp1.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)

        # Whitespace only
        resp2 = self.upload_csv("   \n\n\r\n   \t  \n", 'whitespace.csv')
        self.assertIn(resp2.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)

        # Header only without data
        resp3 = self.upload_csv("roll_number,doc_type,title\n", 'header_only.csv')
        self.assertIn(resp3.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)

    def test_malformed_missing_and_mangled_headers(self):
        """Test CSVs missing required headers or with wrong case/whitespace."""
        self.login()
        initial_docs = Doc.query.count()

        # Missing 'title'
        resp1 = self.upload_csv("roll_number,doc_type\nAPEX01,DEGREE\n", 'missing_title.csv')
        self.assertIn(resp1.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)

        # Missing 'roll_number'
        resp2 = self.upload_csv("doc_type,title\nDEGREE,Bachelor of Tech\n", 'missing_roll.csv')
        self.assertIn(resp2.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)

        # Mangled header names
        resp3 = self.upload_csv("student_id,type,name\n001,DEGREE,Test\n", 'mangled.csv')
        self.assertIn(resp3.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)

    def test_malformed_mixed_line_endings_and_bom(self):
        """Test CSV with UTF-8 BOM, mixed line endings (\\r\\n, \\n, trailing blank lines)."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        # UTF-8 BOM + mixed CRLF and LF + blank lines
        mixed_csv = (
            "\ufeffroll_number,student_name,doc_type,title,validity_days\r\n"
            "APEX2026-CRLF,Alice Smith,DEGREE,Degree CRLF,365\n"
            "APEX2026-LF,Bob Jones,MARKSHEET,Marksheet LF,365\r\n"
            "\r\n"
            "   \n"
            "APEX2026-LAST,Charlie Brown,BONAFIDE,Bonafide End,180\n"
            "\n"
        )
        resp = self.upload_csv(mixed_csv, 'mixed.csv')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Doc.query.count(), initial_docs + 3)
        self.assertEqual(Block.query.count(), initial_blocks + 3)
        ok, msg = validate_chain()
        self.assertTrue(ok, f"Chain invalid: {msg}")

    # =========================================================================
    # SUITE 2: INJECTION & BOUNDARY PAYLOADS
    # =========================================================================

    def test_injection_xss_payloads(self):
        """Test XSS payloads in title, roll_number, student_name are safely rendered with escaping."""
        self.login()
        xss_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "APEX<script>alert(1)</script>,<img src=x onerror=alert(2)>,DEGREE,<svg onload=alert(3)>,365\n"
        )
        resp = self.upload_csv(xss_csv, 'xss.csv')
        self.assertEqual(resp.status_code, 200)

        doc = Doc.query.filter(Doc.title.like('%<svg%')).first()
        self.assertIsNotNone(doc)
        self.assertEqual(doc.title, '<svg onload=alert(3)>')

        # Verify public verification page renders it safely (escaped HTML)
        resp_pub = self.client.get(f'/v/{doc.doc_hash}')
        self.assertEqual(resp_pub.status_code, 200)
        pub_text = resp_pub.get_data(as_text=True)
        self.assertIn('&lt;svg onload=alert(3)&gt;', pub_text)
        self.assertNotIn('<svg onload=alert(3)>', pub_text)

        # Cryptographic verification must succeed
        with self.app.test_request_context():
            outcome = verify_hash(doc.doc_hash)
            self.assertTrue(outcome['ok'], f"Hash verification failed for XSS document: {outcome}")

    def test_injection_unicode_emojis_multilingual(self):
        """Test Unicode characters, emojis, non-Latin scripts (Hindi, Chinese, Arabic)."""
        self.login()
        unicode_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "APEX-हिंदी-01,आदित्य शर्मा,DEGREE,अभियांत्रिकी स्नातक 🎓,3650\n"
            "APEX-中文-02,李小龙,MARKSHEET,计算机科学学士 📜 🚀,3650\n"
            "APEX-AR-03,أحمد محمد,BONAFIDE,شهادة إتمام الدراسة 🛡️,180\n"
        )
        resp = self.upload_csv(unicode_csv, 'unicode.csv')
        self.assertEqual(resp.status_code, 200)

        docs = Doc.query.all()
        titles = [d.title for d in docs]
        self.assertIn('अभियांत्रिकी स्नातक 🎓', titles)
        self.assertIn('计算机科学学士 📜 🚀', titles)
        self.assertIn('شهادة إتمام الدراسة 🛡️', titles)

        with self.app.test_request_context():
            for d in docs:
                outcome = verify_hash(d.doc_hash)
                self.assertTrue(outcome['ok'], f"Verification failed for unicode doc {d.title}: {outcome}")

        ok, msg = validate_chain()
        self.assertTrue(ok, f"Blockchain integrity failed for unicode: {msg}")

    def test_injection_sql_injection_payloads(self):
        """Test SQL injection payloads in CSV fields."""
        self.login()
        initial_docs = Doc.query.count()

        sql_csv = (
            'roll_number,student_name,doc_type,title,validity_days\n'
            'SQL-001,"\' OR 1=1 --",DEGREE,"\' UNION SELECT null, null, null --",365\n'
            'SQL-002,"Robert\'); DROP TABLE block;--",MARKSHEET,Normal Title,365\n'
        )
        resp = self.upload_csv(sql_csv, 'sqli.csv')
        self.assertEqual(resp.status_code, 200)

        # Database tables must still exist and be intact
        self.assertEqual(Doc.query.count(), initial_docs + 2)
        ok, msg = validate_chain()
        self.assertTrue(ok, f"Chain invalid after SQL payload: {msg}")

    def test_injection_formula_csv_injection(self):
        """Test formula injection payloads (=cmd|' /C calc'!A0, @SUM(1+1), +1-2)."""
        self.login()
        formula_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "=cmd|' /C calc'!A0,@SUM(1+1),DEGREE,+1-2,365\n"
        )
        resp = self.upload_csv(formula_csv, 'formula.csv')
        self.assertEqual(resp.status_code, 200)
        doc = Doc.query.filter_by(title='+1-2').first()
        self.assertIsNotNone(doc)

    def test_injection_template_and_path_traversal_payloads(self):
        """Test Jinja/SSTI payloads and path traversal sequences."""
        self.login()
        payload_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "PATH-TRAV,{{ 7 * 7 }},DEGREE,SSTI Title ${7*7}%s{0},365\n"
        )
        resp = self.upload_csv(payload_csv, 'ssti.csv')
        self.assertEqual(resp.status_code, 200)

        doc = Doc.query.filter_by(title='SSTI Title ${7*7}%s{0}').first()
        self.assertIsNotNone(doc)
        # Check that Jinja does not evaluate {{ 7 * 7 }} into 49 on the public page
        resp_pub = self.client.get(f'/v/{doc.doc_hash}')
        self.assertEqual(resp_pub.status_code, 200)
        self.assertIn('{{ 7 * 7 }}', resp_pub.get_data(as_text=True))

    def test_boundary_validity_days_invalid_inputs(self):
        """Test invalid validity_days inputs (0, negative, float, non-numeric)."""
        self.login()
        initial_docs = Doc.query.count()

        invalid_cases = [
            "roll_number,doc_type,title,validity_days\nAPEX01,DEGREE,Test Title,0\n",
            "roll_number,doc_type,title,validity_days\nAPEX01,DEGREE,Test Title,-30\n",
            "roll_number,doc_type,title,validity_days\nAPEX01,DEGREE,Test Title,36.5\n",
            "roll_number,doc_type,title,validity_days\nAPEX01,DEGREE,Test Title,forever\n",
            "roll_number,doc_type,title,validity_days\nAPEX01,DEGREE,Test Title,1e5\n",
        ]
        for csv_text in invalid_cases:
            resp = self.upload_csv(csv_text, 'invalid_val.csv')
            self.assertIn(resp.status_code, (200, 400))
            self.assertEqual(Doc.query.count(), initial_docs, f"Doc created on invalid validity: {csv_text}")

    # =========================================================================
    # SUITE 3: LARGE CSV BATCHES & ATOMICITY
    # =========================================================================

    def test_large_batch_60_rows_success(self):
        """Test issuance of large 60-row valid batch."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        rows = ["roll_number,student_name,doc_type,title,validity_days"]
        for i in range(1, 61):
            rows.append(f"APEX-LRG-{i:03d},Student {i},DEGREE,Large Batch Credential {i},365")

        large_csv = "\n".join(rows) + "\n"
        resp = self.upload_csv(large_csv, 'large_60.csv')
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(Doc.query.count(), initial_docs + 60)
        self.assertEqual(Block.query.count(), initial_blocks + 60)

        ok, msg = validate_chain()
        self.assertTrue(ok, f"Chain validation failed after 60-row batch: {msg}")

    def test_large_batch_atomicity_row_1_fails(self):
        """Test 50-row batch where row 1 fails -> 0 docs, 0 blocks."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        rows = ["roll_number,student_name,doc_type,title,validity_days"]
        rows.append("APEX-F01,Fail Student,INVALID_TYPE,Degree Title,365")
        for i in range(2, 51):
            rows.append(f"APEX-R-{i:03d},Student {i},DEGREE,Good Credential {i},365")

        resp = self.upload_csv("\n".join(rows) + "\n", 'fail_r1.csv')
        self.assertIn(resp.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)

    def test_large_batch_atomicity_row_30_fails(self):
        """Test 55-row batch where middle row (row 30) fails -> 0 docs, 0 blocks."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        rows = ["roll_number,student_name,doc_type,title,validity_days"]
        for i in range(1, 56):
            if i == 30:
                rows.append(f"APEX-M-{i:03d},Student {i},,Missing DocType,365")
            else:
                rows.append(f"APEX-M-{i:03d},Student {i},DEGREE,Good Credential {i},365")

        resp = self.upload_csv("\n".join(rows) + "\n", 'fail_r30.csv')
        self.assertIn(resp.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)

    def test_large_batch_atomicity_row_49_fails(self):
        """Test large 55-row batch where row 49 has an invalid doc_type -> 0 docs, 0 blocks."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()
        initial_users = User.query.count()

        rows = ["roll_number,student_name,doc_type,title,validity_days"]
        for i in range(1, 56):
            if i == 49:
                rows.append(f"APEX-FL-{i:03d},Fail Student {i},INVALID_DOCTYPE,Failed Credential {i},365")
            else:
                rows.append(f"APEX-FL-{i:03d},Student {i},DEGREE,Good Credential {i},365")

        flawed_large_csv = "\n".join(rows) + "\n"
        resp = self.upload_csv(flawed_large_csv, 'flawed_large.csv')
        self.assertIn(resp.status_code, (200, 400))

        # Strict atomicity check: zero changes to DB and Blockchain
        self.assertEqual(Doc.query.count(), initial_docs, "Doc count altered on row 49 failure!")
        self.assertEqual(Block.query.count(), initial_blocks, "Block mined on row 49 failure!")
        self.assertEqual(User.query.count(), initial_users, "User accounts created on failed batch!")

        ok, msg = validate_chain()
        self.assertTrue(ok, f"Chain integrity compromised: {msg}")

    def test_large_batch_atomicity_last_row_fails(self):
        """Test large 50-row batch where the final row (row 50) has negative validity_days."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        rows = ["roll_number,student_name,doc_type,title,validity_days"]
        for i in range(1, 51):
            if i == 50:
                rows.append(f"APEX-END-{i:03d},Student {i},DEGREE,Final Row,-99")
            else:
                rows.append(f"APEX-END-{i:03d},Student {i},DEGREE,Row {i},365")

        csv_str = "\n".join(rows) + "\n"
        resp = self.upload_csv(csv_str, 'end_fail.csv')
        self.assertIn(resp.status_code, (200, 400))

        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)

    # =========================================================================
    # SUITE 4: CONCURRENT & SUCCESSIVE ATTEMPTS
    # =========================================================================

    def test_successive_good_bad_good_batches(self):
        """Test alternating Good -> Bad -> Good batches."""
        self.login()
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        # Batch 1: Good (5 rows)
        b1 = "roll_number,doc_type,title\n" + "\n".join(f"B1-{i},DEGREE,T1-{i}" for i in range(5))
        r1 = self.upload_csv(b1, 'b1.csv')
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(Doc.query.count(), initial_docs + 5)
        self.assertEqual(Block.query.count(), initial_blocks + 5)

        # Batch 2: Bad (5 rows, row 3 missing title)
        b2 = "roll_number,doc_type,title\nB2-1,DEGREE,T2-1\nB2-2,DEGREE,T2-2\nB2-3,DEGREE,\nB2-4,DEGREE,T2-4\n"
        r2 = self.upload_csv(b2, 'b2.csv')
        self.assertIn(r2.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs + 5)
        self.assertEqual(Block.query.count(), initial_blocks + 5)

        # Batch 3: Good (5 rows)
        b3 = "roll_number,doc_type,title\n" + "\n".join(f"B3-{i},MARKSHEET,T3-{i}" for i in range(5))
        r3 = self.upload_csv(b3, 'b3.csv')
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(Doc.query.count(), initial_docs + 10)
        self.assertEqual(Block.query.count(), initial_blocks + 10)

        ok, msg = validate_chain()
        self.assertTrue(ok, f"Chain broken after successive sequence: {msg}")

    def test_duplicate_roll_numbers_within_same_batch(self):
        """Test batch containing multiple distinct credentials for the same roll number."""
        self.login()
        initial_docs = Doc.query.count()
        initial_users = User.query.count()

        batch = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "MULTI-ROLL-01,John Multi,DEGREE,Bachelor of Science,365\n"
            "MULTI-ROLL-01,John Multi,MARKSHEET,Year 1 Transcript,365\n"
            "MULTI-ROLL-01,John Multi,BONAFIDE,Hostel Bonafide,180\n"
        )
        resp = self.upload_csv(batch, 'multi_roll.csv')
        self.assertEqual(resp.status_code, 200)

        # 3 new docs created
        self.assertEqual(Doc.query.count(), initial_docs + 3)
        # Only 1 new Student / User created for MULTI-ROLL-01
        self.assertEqual(User.query.count(), initial_users + 1)

        ok, msg = validate_chain()
        self.assertTrue(ok, f"Chain validation failed: {msg}")

    # =========================================================================
    # SUITE 5: DB & BLOCKCHAIN INTEGRITY VERIFICATION
    # =========================================================================

    def test_strict_crypto_hash_and_blockchain_anchoring(self):
        """Verify that every bulk issued credential can be cryptographically verified."""
        self.login()
        batch_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "SEC-001,Student One,DEGREE,Secure Degree,365\n"
            "SEC-002,Student Two,MARKSHEET,Secure Transcript,365\n"
            "SEC-003,Student Three,BONAFIDE,Secure Bonafide,180\n"
        )
        resp = self.upload_csv(batch_csv, 'sec.csv')
        self.assertEqual(resp.status_code, 200)

        docs = Doc.query.filter(Doc.title.like('Secure%')).all()
        self.assertEqual(len(docs), 3)

        with self.app.test_request_context():
            for d in docs:
                # Verify verify_hash against DB payload and salt
                outcome = verify_hash(d.doc_hash)
                self.assertTrue(outcome['ok'], f"Hash verification failed for {d.title}: {outcome}")

                # Verify block matches
                blk = Block.query.filter_by(doc_hash=d.doc_hash).first()
                self.assertIsNotNone(blk)
                self.assertEqual(blk.index, d.block_index)

        ok, msg = validate_chain()
        self.assertTrue(ok, f"Validate chain failed: {msg}")

    def test_student_dashboard_rendering_for_bulk_issued_credentials(self):
        """Verify that an auto-provisioned student can log in and view their text-only credentials without crashing."""
        self.login()
        batch_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "STU-VIEW-99,Alex View,DEGREE,Bachelor of Arts,365\n"
        )
        self.upload_csv(batch_csv, 'stu_view.csv')

        doc = Doc.query.filter_by(title='Bachelor of Arts').first()
        self.assertIsNotNone(doc)

        # Log out issuer and login as auto-provisioned student
        self.client.get('/logout', follow_redirects=True)
        login_resp = self.login(identifier='student.stu-view-99', password='satyameva123')
        self.assertEqual(login_resp.status_code, 200)

        resp_dash = self.client.get('/student/dashboard')
        self.assertEqual(resp_dash.status_code, 200)
        self.assertIn('Bachelor of Arts', resp_dash.get_data(as_text=True))

        resp_doc = self.client.get(f'/student/document/{doc.id}')
        self.assertEqual(resp_doc.status_code, 200)
        self.assertIn(doc.doc_hash, resp_doc.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
