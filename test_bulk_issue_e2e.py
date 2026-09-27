"""
End-to-End Automated Test Suite for Satyameva Bulk Issuance Feature.

Tests all 4 tiers of requirements:
- Tier 1: Feature Coverage (AC1: missing columns error, AC2: 3-row valid batch creates 3 docs & 3 blocks,
          AC3: text-only credentials render on student dashboard, detail view, & public verify page,
          AC4: sample template.csv served with proper headers)
- Tier 2: Boundary & Corner Cases (empty CSV, header-only CSV, whitespace in headers, missing values in middle row,
          UTF-8 BOM encoding, invalid doc types, non-numeric validity days, non-csv file extension)
- Tier 3: Cross-Feature & State Isolation (atomic all-or-nothing rollback, sequential batches mining successive blocks,
          auto-provisioned student login & view, public verifier query hash)
- Tier 4: Real-World Scenarios (End-to-end issuer login -> bulk issue 3 credentials -> student verification ->
          public verification -> verification certificate PDF generation -> employer verification log & notification)

Execution:
    python test_bulk_issue_e2e.py
    python -m unittest test_bulk_issue_e2e.py
"""
import io
import json
import os
import shutil
import tempfile
import time
import unittest
from datetime import datetime

from app import create_app
from blockchain import blockchain_instance, validate_chain
from extensions import db
from models.block import Block
from models.document import DOC_TYPES, STATUS_VALID, Doc
from models.notification import Notification
from models.student import Student
from models.user import ROLE_ISSUER, ROLE_STUDENT, ROLE_VERIFIER, User
from models.verification_log import VerificationLog
from security import hash_password


class BaseBulkIssueTestCase(unittest.TestCase):
    """Base test setup with isolated temporary database and blockchain file."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix='satyameva_bulk_test_')
        self.temp_db_path = os.path.join(self.temp_dir, 'test_satyameva.db')
        self.temp_chain_path = os.path.join(self.temp_dir, 'blockchain.json')

        # Ensure strict database isolation in environment and config classes before create_app()
        self.old_db_url = os.environ.get('DATABASE_URL')
        os.environ['DATABASE_URL'] = f'sqlite:///{self.temp_db_path}'

        import config
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

        # Point blockchain singleton to isolated test storage and fast difficulty before app initialization
        self.original_chain_storage = blockchain_instance.storage_file
        self.original_chain_difficulty = blockchain_instance.difficulty
        blockchain_instance.storage_file = self.temp_chain_path
        blockchain_instance.difficulty = 1

        # Configure isolated environment
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'MAIL_SUPPRESS_SEND': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.temp_db_path}',
            'POW_DIFFICULTY': 1,  # Fast mining for tests
        })

        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create fresh tables and genesis block in isolated temp database
        db.drop_all()
        db.create_all()
        blockchain_instance.ensure_genesis_block()

        self.client = self.app.test_client()

        # Seed standard test users
        self._seed_standard_users()

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

        # Restore blockchain singleton settings
        blockchain_instance.storage_file = self.original_chain_storage
        blockchain_instance.difficulty = self.original_chain_difficulty

        # Restore config class attributes
        import config
        config.BaseConfig.SQLALCHEMY_DATABASE_URI = self.old_base_uri
        config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI = self.old_dev_uri
        config.ProductionConfig.SQLALCHEMY_DATABASE_URI = self.old_prod_uri
        config.BaseConfig.MAIL_SUPPRESS_SEND = self.old_mail_suppress
        config.DevelopmentConfig.MAIL_SUPPRESS_SEND = self.old_mail_suppress
        config.ProductionConfig.MAIL_SUPPRESS_SEND = self.old_mail_suppress

        # Clean up database environment variable
        if self.old_db_url is not None:
            os.environ['DATABASE_URL'] = self.old_db_url
        else:
            os.environ.pop('DATABASE_URL', None)

        # Remove temp directory
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def _seed_standard_users(self):
        """Seed standard Issuer, Student, and Verifier accounts."""
        salt, digest, iters = hash_password('password123', iterations=1000)

        # 1. Issuer
        self.issuer_user = User(
            username='apex.issuer',
            email='issuer@apex.edu',
            role=ROLE_ISSUER,
            organization='Apex National University',
            password_salt=salt,
            password_hash=digest,
            password_iterations=iters,
        )
        db.session.add(self.issuer_user)
        db.session.flush()

        # 2. Existing Student
        self.student_user = User(
            username='student.rohit',
            email='rohit@apex.edu',
            role=ROLE_STUDENT,
            organization='Apex National University',
            password_salt=salt,
            password_hash=digest,
            password_iterations=iters,
        )
        db.session.add(self.student_user)
        db.session.flush()

        self.student_profile = Student(
            user_id=self.student_user.id,
            full_name='Rohit Verma',
            roll_number='APEX2026-001',
            program='B.Tech Computer Science',
            department='Computer Science',
            institution='Apex National University',
            batch='2022-2026',
        )
        db.session.add(self.student_profile)

        # 3. Verifier
        self.verifier_user = User(
            username='techcorp.hr',
            email='hr@techcorp.com',
            role=ROLE_VERIFIER,
            organization='TechCorp Global Ltd.',
            password_salt=salt,
            password_hash=digest,
            password_iterations=iters,
        )
        db.session.add(self.verifier_user)
        db.session.commit()

    def login(self, username='apex.issuer', password='password123'):
        """Log in as a specific user via the auth route."""
        return self.client.post('/login', data={
            'identifier': username,
            'password': password,
        }, follow_redirects=True)

    def logout(self):
        """Log out the current user session."""
        return self.client.get('/logout', follow_redirects=True)

    def make_csv_upload(self, csv_content: str | bytes, filename: str = 'bulk_credentials.csv'):
        """Create a FileStorage-like tuple for POST multipart/form-data."""
        if isinstance(csv_content, str):
            data_bytes = csv_content.encode('utf-8')
        else:
            data_bytes = csv_content
        return (io.BytesIO(data_bytes), filename)


# ==============================================================================
# TIER 1: FEATURE COVERAGE
# ==============================================================================
class TestTier1FeatureCoverage(BaseBulkIssueTestCase):
    """
    Tier 1 tests covering core Acceptance Criteria (AC1 - AC4) from ORIGINAL_REQUEST.md.
    """

    def test_ac1_missing_required_columns_error_and_zero_docs(self):
        """
        AC1: Submitting a CSV with missing required columns immediately returns an error
        and creates 0 documents and 0 new blocks.
        """
        self.login('apex.issuer', 'password123')
        initial_doc_count = Doc.query.count()
        initial_block_count = Block.query.count()

        # CSV missing 'doc_type' column
        csv_missing_doctype = (
            "roll_number,title,student_name\n"
            "APEX2026-001,Bachelor of Technology in CS,Rohit Verma\n"
        )
        file_tuple = self.make_csv_upload(csv_missing_doctype, 'missing_doctype.csv')
        resp = self.client.post('/issuer/bulk-issue', data={'csv_file': file_tuple}, follow_redirects=True)

        # Must report validation failure
        self.assertIn(resp.status_code, (200, 400), f"Unexpected status code: {resp.status_code}")
        resp_text = resp.get_data(as_text=True)
        self.assertTrue(
            any(err_word in resp_text.lower() for err_word in ['missing', 'column', 'header', 'required', 'doc_type', 'invalid']),
            f"Expected error message indicating missing column, got: {resp_text[:300]}"
        )

        # Database and blockchain must remain completely untouched
        self.assertEqual(Doc.query.count(), initial_doc_count, "No documents should be created when required column is missing")
        self.assertEqual(Block.query.count(), initial_block_count, "No blocks should be mined when required column is missing")

        # Also test CSV missing 'roll_number'
        csv_missing_roll = (
            "doc_type,title,student_name\n"
            "DEGREE,Bachelor of Technology in CS,Rohit Verma\n"
        )
        file_tuple2 = self.make_csv_upload(csv_missing_roll, 'missing_roll.csv')
        resp2 = self.client.post('/issuer/bulk-issue', data={'csv_file': file_tuple2}, follow_redirects=True)
        self.assertIn(resp2.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_doc_count)
        self.assertEqual(Block.query.count(), initial_block_count)

        # Also test CSV missing 'title'
        csv_missing_title = (
            "roll_number,doc_type,student_name\n"
            "APEX2026-001,DEGREE,Rohit Verma\n"
        )
        file_tuple3 = self.make_csv_upload(csv_missing_title, 'missing_title.csv')
        resp3 = self.client.post('/issuer/bulk-issue', data={'csv_file': file_tuple3}, follow_redirects=True)
        self.assertIn(resp3.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_doc_count)
        self.assertEqual(Block.query.count(), initial_block_count)

    def test_ac2_valid_3_row_csv_creates_3_docs_and_3_blocks(self):
        """
        AC2: Submitting a valid CSV with 3 rows successfully creates exactly 3 new Doc records
        in the SQLite database and mines 3 new blocks.
        """
        self.login('apex.issuer', 'password123')
        initial_doc_count = Doc.query.count()
        initial_block_count = Block.query.count()

        valid_3_row_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "APEX2026-001,Rohit Verma,DEGREE,Bachelor of Technology in Computer Science,3650\n"
            "APEX2026-002,Ananya Sen,MARKSHEET,Consolidated Grade Sheet - 8 Semesters,3650\n"
            "APEX2026-003,Karan Patel,BONAFIDE,Bonafide Academic Certificate,180\n"
        )

        file_tuple = self.make_csv_upload(valid_3_row_csv, 'valid_batch.csv')
        resp = self.client.post('/issuer/bulk-issue', data={'csv_file': file_tuple}, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)

        # Exactly 3 new Doc records created
        new_doc_count = Doc.query.count()
        self.assertEqual(new_doc_count, initial_doc_count + 3, f"Expected {initial_doc_count + 3} docs, found {new_doc_count}")

        # Exactly 3 new blocks mined
        new_block_count = Block.query.count()
        self.assertEqual(new_block_count, initial_block_count + 3, f"Expected {initial_block_count + 3} blocks, found {new_block_count}")

        # Verify each document record properties
        doc1 = Doc.query.filter_by(title='Bachelor of Technology in Computer Science').first()
        doc2 = Doc.query.filter_by(title='Consolidated Grade Sheet - 8 Semesters').first()
        doc3 = Doc.query.filter_by(title='Bonafide Academic Certificate').first()

        self.assertIsNotNone(doc1, "Doc 1 was not created")
        self.assertIsNotNone(doc2, "Doc 2 was not created")
        self.assertIsNotNone(doc3, "Doc 3 was not created")

        for doc in (doc1, doc2, doc3):
            self.assertIsNotNone(doc.doc_hash, "doc_hash must be generated")
            self.assertEqual(len(doc.doc_hash), 64, "doc_hash must be a 64-char SHA-256 hex string")
            self.assertIsNotNone(doc.block_index, "block_index must be assigned")
            self.assertGreater(doc.block_index, 0, "block_index must be > 0 (genesis is 0)")
            self.assertIsNone(doc.file_data, "Bulk issued credentials must be text-only (file_data is None)")
            self.assertTrue(doc.is_valid, "Freshly issued credential should have VALID status")

        # Verify blockchain validity
        ok, msg = validate_chain()
        self.assertTrue(ok, f"Blockchain verification failed after 3-row batch: {msg}")

    def test_ac3_text_only_credentials_render_safely_across_all_views(self):
        """
        AC3: The generated text-only credentials can be viewed on student dashboard,
        student document detail view, and public verify page without crashing.
        """
        self.login('apex.issuer', 'password123')
        valid_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "APEX2026-001,Rohit Verma,DEGREE,B.Tech Degree Certificate,3650\n"
        )
        self.client.post('/issuer/bulk-issue', data={'csv_file': self.make_csv_upload(valid_csv)}, follow_redirects=True)

        doc = Doc.query.filter_by(title='B.Tech Degree Certificate').first()
        self.assertIsNotNone(doc)
        self.assertIsNone(doc.file_data, "Credential must be text-only without file upload")

        self.logout()

        # 1. Student Dashboard
        self.login('student.rohit', 'password123')
        resp_dash = self.client.get('/student/dashboard')
        self.assertEqual(resp_dash.status_code, 200, "Student dashboard crashed on text-only credential")
        dash_html = resp_dash.get_data(as_text=True)
        self.assertIn('B.Tech Degree Certificate', dash_html)
        self.assertIn(doc.doc_hash[:8], dash_html)
        self.assertIn('data:image/png;base64', dash_html, "QR code data URI should render on card")

        # 2. Student Document Detail View
        resp_detail = self.client.get(f'/student/document/{doc.id}')
        self.assertEqual(resp_detail.status_code, 200, "Student document detail crashed on text-only credential")
        detail_html = resp_detail.get_data(as_text=True)
        self.assertIn('B.Tech Degree Certificate', detail_html)
        self.assertIn(str(doc.block_index), detail_html)

        # 3. Student Stamped PDF Download
        resp_pdf = self.client.get(f'/student/document/{doc.id}/download')
        self.assertEqual(resp_pdf.status_code, 200, "PDF certificate generation crashed for text-only credential")
        self.assertEqual(resp_pdf.mimetype, 'application/pdf')
        self.assertTrue(resp_pdf.data.startswith(b'%PDF'), "Response is not a valid PDF file")
        self.assertGreater(len(resp_pdf.data), 500, "Generated PDF is abnormally small")

        self.logout()

        # 4. Public Verify Result Page
        resp_public = self.client.get(f'/v/{doc.doc_hash}')
        self.assertEqual(resp_public.status_code, 200, "Public verify page crashed for text-only credential")
        public_html = resp_public.get_data(as_text=True)
        self.assertIn('Authentic credential', public_html)
        self.assertIn('Rohit Verma', public_html)
        self.assertIn('B.Tech Degree Certificate', public_html)

    def test_ac4_sample_template_csv_served_with_proper_headers(self):
        """
        AC4: Sample template.csv is correctly served and contains the proper headers.
        """
        self.login('apex.issuer', 'password123')

        # Test both possible endpoints specified in route contract
        resp = self.client.get('/issuer/sample-csv')
        if resp.status_code == 404:
            resp = self.client.get('/issuer/template.csv')

        self.assertEqual(resp.status_code, 200, "Sample CSV endpoint failed to serve file")
        content_type = resp.headers.get('Content-Type', '')
        self.assertTrue(
            'text/csv' in content_type or 'application/octet-stream' in content_type or 'application/csv' in content_type,
            f"Expected CSV content type, got: {content_type}"
        )

        csv_text = resp.get_data(as_text=True)
        lines = [line.strip() for line in csv_text.strip().splitlines() if line.strip()]
        self.assertGreaterEqual(len(lines), 2, "Sample CSV must contain a header and at least one sample row")

        header_line = lines[0].lower()
        self.assertIn('roll_number', header_line, "Sample CSV header must include roll_number")
        self.assertIn('doc_type', header_line, "Sample CSV header must include doc_type")
        self.assertIn('title', header_line, "Sample CSV header must include title")

    def test_bulk_issue_ui_endpoint_accessible(self):
        """
        Verify GET /issuer/bulk-issue renders the Bulk Issue interface with form and sample link.
        """
        self.login('apex.issuer', 'password123')
        resp = self.client.get('/issuer/bulk-issue')
        self.assertEqual(resp.status_code, 200, "GET /issuer/bulk-issue should render 200 OK")
        html = resp.get_data(as_text=True)
        self.assertIn('csv_file', html, "Form must contain file upload input named 'csv_file'")
        self.assertTrue('.csv' in html.lower(), "Interface should indicate .csv requirement")


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES
# ==============================================================================
class TestTier2BoundaryCases(BaseBulkIssueTestCase):
    """
    Tier 2 tests covering edge cases, boundary inputs, malformed files, and encoding variations.
    """

    def setUp(self):
        super().setUp()
        self.login('apex.issuer', 'password123')

    def test_boundary_empty_csv_file(self):
        """Uploading an empty 0-byte CSV file must fail validation with 0 docs/blocks created."""
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        empty_file = self.make_csv_upload(b"", "empty.csv")
        resp = self.client.post('/issuer/bulk-issue', data={'csv_file': empty_file}, follow_redirects=True)

        self.assertIn(resp.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs, "0 docs should be created from empty CSV")
        self.assertEqual(Block.query.count(), initial_blocks, "0 blocks should be mined from empty CSV")

    def test_boundary_header_only_csv(self):
        """Uploading a CSV with headers but zero data rows must fail with 0 docs/blocks created."""
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        header_only = "roll_number,doc_type,title,validity_days\n"
        resp = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(header_only, "headers_only.csv")},
            follow_redirects=True
        )

        self.assertIn(resp.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs, "0 docs should be created from header-only CSV")
        self.assertEqual(Block.query.count(), initial_blocks, "0 blocks should be mined from header-only CSV")

    def test_boundary_whitespace_in_headers_and_values(self):
        """Headers and fields with leading/trailing whitespace must be trimmed and processed cleanly."""
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        whitespace_csv = (
            "   roll_number  ,  student_name   ,  doc_type  ,   title   ,   validity_days   \n"
            "   APEX2026-001   ,   Rohit Verma   ,   DEGREE   ,   Bachelor of Science in Physics   ,   365   \n"
        )
        resp = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(whitespace_csv, "whitespace.csv")},
            follow_redirects=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Doc.query.count(), initial_docs + 1)
        self.assertEqual(Block.query.count(), initial_blocks + 1)

        doc = Doc.query.filter_by(title='Bachelor of Science in Physics').first()
        self.assertIsNotNone(doc)
        self.assertEqual(doc.doc_type, 'DEGREE')
        self.assertEqual(doc.student.roll_number, 'APEX2026-001')

    def test_boundary_missing_values_middle_row_fails_all_or_nothing(self):
        """
        In a 5-row CSV where row 3 has missing required fields,
        the entire batch must fail (0 docs created, 0 blocks mined).
        """
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        five_row_with_flawed_middle = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "APEX2026-001,Student One,DEGREE,Degree One,365\n"
            "APEX2026-002,Student Two,MARKSHEET,Marksheet Two,365\n"
            "APEX2026-003,Student Three,DEGREE,,365\n"  # Missing title!
            "APEX2026-004,Student Four,TC,TC Four,180\n"
            "APEX2026-005,Student Five,BONAFIDE,Bonafide Five,90\n"
        )

        resp = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(five_row_with_flawed_middle, "flawed_5_rows.csv")},
            follow_redirects=True
        )

        self.assertIn(resp.status_code, (200, 400))
        resp_text = resp.get_data(as_text=True)
        self.assertTrue(
            any(k in resp_text.lower() for k in ['row 3', 'row', 'title', 'error', 'failed', 'missing']),
            f"Expected error mentioning row 3 or missing title, got: {resp_text[:300]}"
        )

        # STRICT ALL-OR-NOTHING: 0 documents created, 0 blocks mined
        self.assertEqual(Doc.query.count(), initial_docs, "All-or-nothing violated: documents were created on partial failure")
        self.assertEqual(Block.query.count(), initial_blocks, "All-or-nothing violated: blocks were mined on partial failure")

    def test_boundary_utf8_bom_encoding(self):
        """CSV files with UTF-8 BOM prefix (common from Excel exports) must be parsed cleanly."""
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        bom_csv = (
            "\ufeffroll_number,student_name,doc_type,title,validity_days\n"
            "APEX2026-001,Rohit Verma,DEGREE,B.Tech Degree via BOM,365\n"
        ).encode('utf-8')

        resp = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(bom_csv, "excel_bom.csv")},
            follow_redirects=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Doc.query.count(), initial_docs + 1)
        self.assertEqual(Block.query.count(), initial_blocks + 1)
        doc = Doc.query.filter_by(title='B.Tech Degree via BOM').first()
        self.assertIsNotNone(doc)

    def test_boundary_invalid_doc_type(self):
        """A CSV row with an unsupported or unknown doc_type must fail validation with 0 docs/blocks."""
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        invalid_doctype_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "APEX2026-001,Rohit Verma,DRIVING_LICENSE,Motor Vehicle Permit,365\n"
        )

        resp = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(invalid_doctype_csv, "invalid_type.csv")},
            follow_redirects=True
        )

        self.assertIn(resp.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs, "0 docs should be created with invalid doc_type")
        self.assertEqual(Block.query.count(), initial_blocks, "0 blocks should be mined with invalid doc_type")

    def test_boundary_non_numeric_validity_days(self):
        """A CSV row with non-numeric or negative validity_days must fail validation with 0 docs/blocks."""
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        invalid_validity_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "APEX2026-001,Rohit Verma,DEGREE,Invalid Validity Degree,thirty_days\n"
        )

        resp = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(invalid_validity_csv, "bad_validity.csv")},
            follow_redirects=True
        )

        self.assertIn(resp.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)

    def test_boundary_non_csv_file_extension(self):
        """Uploading non-CSV files (e.g. .txt, .pdf, .exe) must be rejected."""
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        txt_file = (io.BytesIO(b"roll_number,doc_type,title\nAPEX2026-001,DEGREE,Test\n"), "batch.txt")
        resp = self.client.post('/issuer/bulk-issue', data={'csv_file': txt_file}, follow_redirects=True)

        self.assertIn(resp.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)


# ==============================================================================
# TIER 3: CROSS-FEATURE & STATE ISOLATION
# ==============================================================================
class TestTier3CrossFeatureAndStateIsolation(BaseBulkIssueTestCase):
    """
    Tier 3 tests verifying cross-feature workflows, rollback state isolation,
    sequential blockchain integrity, and verifier queries.
    """

    def test_state_isolation_failed_batch_leaves_state_clean_for_subsequent_batch(self):
        """
        An invalid batch fails completely and leaves DB & blockchain clean.
        A subsequent valid batch immediately succeeds without collision or corruption.
        """
        self.login('apex.issuer', 'password123')
        initial_docs = Doc.query.count()
        initial_blocks = Block.query.count()

        # Step 1: Failed batch
        bad_csv = (
            "roll_number,doc_type,title\n"
            "APEX2026-001,INVALID_TYPE,Test Bad Title\n"
        )
        resp1 = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(bad_csv, "bad.csv")},
            follow_redirects=True
        )
        self.assertIn(resp1.status_code, (200, 400))
        self.assertEqual(Doc.query.count(), initial_docs)
        self.assertEqual(Block.query.count(), initial_blocks)

        # Step 2: Valid batch succeeding immediately after
        good_csv = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "APEX2026-001,Rohit Verma,DEGREE,Subsequent Valid Degree,3650\n"
            "APEX2026-002,Pooja Sharma,MARKSHEET,Subsequent Marksheet,3650\n"
        )
        resp2 = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(good_csv, "good.csv")},
            follow_redirects=True
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(Doc.query.count(), initial_docs + 2)
        self.assertEqual(Block.query.count(), initial_blocks + 2)

        # Step 3: Verify chain is intact
        ok, msg = validate_chain()
        self.assertTrue(ok, f"Chain integrity compromised after failed-then-good batch: {msg}")

    def test_sequential_multiple_batches_mining_successive_blocks(self):
        """
        Multiple sequential batches mine successive blocks monotonically (#1, #2, #3...)
        and preserve complete cryptographic linkage across all blocks.
        """
        self.login('apex.issuer', 'password123')

        # Batch 1: 2 credentials
        batch1_csv = (
            "roll_number,student_name,doc_type,title\n"
            "APEX-A01,Student A1,DEGREE,Batch 1 Degree A1\n"
            "APEX-A02,Student A2,MARKSHEET,Batch 1 Marksheet A2\n"
        )
        resp1 = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(batch1_csv, "batch1.csv")},
            follow_redirects=True
        )
        self.assertEqual(resp1.status_code, 200)

        # Batch 2: 3 credentials
        batch2_csv = (
            "roll_number,student_name,doc_type,title\n"
            "APEX-B01,Student B1,TC,Batch 2 TC B1\n"
            "APEX-B02,Student B2,BONAFIDE,Batch 2 Bonafide B2\n"
            "APEX-B03,Student B3,MIGRATION,Batch 2 Migration B3\n"
        )
        resp2 = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(batch2_csv, "batch2.csv")},
            follow_redirects=True
        )
        self.assertEqual(resp2.status_code, 200)

        # Total 5 docs and 6 blocks (genesis + 5)
        self.assertEqual(Doc.query.count(), 5)
        self.assertEqual(Block.query.count(), 6)

        blocks = Block.query.order_by(Block.index.asc()).all()
        for idx, blk in enumerate(blocks):
            self.assertEqual(blk.index, idx, f"Block index mismatch: expected {idx}, got {blk.index}")
            if idx > 0:
                self.assertEqual(blk.previous_hash, blocks[idx - 1].hash, f"Block #{idx} parent hash mismatch")

        ok, msg = validate_chain()
        self.assertTrue(ok, f"Blockchain validate_chain failed across multiple batches: {msg}")

    def test_student_auto_provisioning_and_login_view(self):
        """
        When a new student roll number is included in a bulk batch,
        a student profile and user account are provisioned, enabling login and view.
        """
        self.login('apex.issuer', 'password123')
        new_student_roll = 'APEX2026-NEW99'
        bulk_csv = (
            f"roll_number,student_name,doc_type,title,validity_days\n"
            f"{new_student_roll},Vikram Aditya,DEGREE,Honorary Degree in Robotics,3650\n"
        )

        resp = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(bulk_csv, "new_student.csv")},
            follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)

        # Verify Student and User exist
        student = Student.query.filter_by(roll_number=new_student_roll).first()
        self.assertIsNotNone(student, "New student profile should be automatically provisioned")
        self.assertEqual(student.full_name, 'Vikram Aditya')
        self.assertIsNotNone(student.user, "Student user account should be provisioned")

        # Verify document is linked to this student
        doc = Doc.query.filter_by(student_id=student.id).first()
        self.assertIsNotNone(doc)
        self.assertEqual(doc.title, 'Honorary Degree in Robotics')

        self.logout()

        # Log in as the auto-provisioned student (default password 'satyameva123')
        resp_login = self.login(student.user.username, 'satyameva123')
        self.assertEqual(resp_login.status_code, 200)

        resp_dash = self.client.get('/student/dashboard')
        self.assertEqual(resp_dash.status_code, 200)
        self.assertIn('Honorary Degree in Robotics', resp_dash.get_data(as_text=True))

    def test_public_verifier_query_bulk_issued_hash(self):
        """
        Public verifier can query the hash of a bulk-issued credential
        via /verify and /v/<hash> and get an authentic result.
        """
        self.login('apex.issuer', 'password123')
        bulk_csv = (
            "roll_number,student_name,doc_type,title\n"
            "APEX2026-001,Rohit Verma,DEGREE,Degree for Public Verification\n"
        )
        self.client.post('/issuer/bulk-issue', data={'csv_file': self.make_csv_upload(bulk_csv)}, follow_redirects=True)
        doc = Doc.query.filter_by(title='Degree for Public Verification').first()
        self.assertIsNotNone(doc)

        self.logout()

        # Submit hash on public /verify POST form -> redirects to /v/<hash>
        resp_post = self.client.post('/verify', data={'doc_hash': doc.doc_hash}, follow_redirects=True)
        self.assertEqual(resp_post.status_code, 200)
        html = resp_post.get_data(as_text=True)

        self.assertIn('Authentic credential', html)
        self.assertIn(doc.title, html)
        self.assertIn(doc.student.full_name, html)
        self.assertIn(str(doc.block_index), html)


# ==============================================================================
# TIER 4: REAL-WORLD SCENARIOS
# ==============================================================================
class TestTier4RealWorldScenarios(BaseBulkIssueTestCase):
    """
    Tier 4 tests verifying complete end-to-end real-world lifecycle.
    """

    def test_full_e2e_bulk_issuance_lifecycle(self):
        """
        End-to-End Real World Scenario:
        1. Issuer logs in.
        2. Issuer downloads template CSV.
        3. Issuer uploads a 3-credential bulk CSV batch.
        4. DB and Blockchain integrity verified.
        5. Student logs in, views credentials and downloads stamped PDF certificate.
        6. Public verifier verifies credential hash.
        7. Authenticated Employer/Verifier verifies credential, generating audit log and student notification.
        """
        # Step 1: Issuer Login
        resp_login = self.login('apex.issuer', 'password123')
        self.assertEqual(resp_login.status_code, 200)
        self.assertIn('Apex National University', resp_login.get_data(as_text=True))

        # Step 2: Download Template CSV
        resp_tmpl = self.client.get('/issuer/sample-csv')
        if resp_tmpl.status_code == 404:
            resp_tmpl = self.client.get('/issuer/template.csv')
        self.assertEqual(resp_tmpl.status_code, 200)
        self.assertIn('roll_number', resp_tmpl.get_data(as_text=True).lower())

        # Step 3: Issue 3 Credentials in Bulk
        csv_payload = (
            "roll_number,student_name,doc_type,title,validity_days\n"
            "APEX2026-001,Rohit Verma,DEGREE,B.Tech in Artificial Intelligence,3650\n"
            "APEX2026-001,Rohit Verma,MARKSHEET,Official Consolidated Transcript,3650\n"
            "APEX2026-001,Rohit Verma,BONAFIDE,Bonafide Student Certificate 2026,90\n"
        )
        resp_bulk = self.client.post(
            '/issuer/bulk-issue',
            data={'csv_file': self.make_csv_upload(csv_payload, "cohort_2026.csv")},
            follow_redirects=True
        )
        self.assertEqual(resp_bulk.status_code, 200)

        # Step 4: Verify DB records & Blockchain State
        docs = Doc.query.filter_by(student_id=self.student_profile.id).all()
        self.assertEqual(len(docs), 3, "Expected 3 documents created for Rohit Verma")

        degree_doc = next(d for d in docs if d.doc_type == 'DEGREE')
        marksheet_doc = next(d for d in docs if d.doc_type == 'MARKSHEET')
        bonafide_doc = next(d for d in docs if d.doc_type == 'BONAFIDE')

        self.assertEqual(Block.query.count(), 4, "Expected Genesis + 3 blocks = 4 blocks")
        ok, chain_msg = validate_chain()
        self.assertTrue(ok, f"Blockchain validation failed: {chain_msg}")

        self.logout()

        # Step 5: Student Logs In and Views Dashboard & Downloads PDF
        resp_stud_login = self.login('student.rohit', 'password123')
        self.assertEqual(resp_stud_login.status_code, 200)

        resp_dash = self.client.get('/student/dashboard')
        self.assertEqual(resp_dash.status_code, 200)
        dash_html = resp_dash.get_data(as_text=True)
        self.assertIn('B.Tech in Artificial Intelligence', dash_html)
        self.assertIn('Official Consolidated Transcript', dash_html)
        self.assertIn('Bonafide Student Certificate 2026', dash_html)

        # Student downloads stamped verification certificate PDF for degree
        resp_pdf = self.client.get(f'/student/document/{degree_doc.id}/download')
        self.assertEqual(resp_pdf.status_code, 200)
        self.assertEqual(resp_pdf.mimetype, 'application/pdf')
        self.assertTrue(resp_pdf.data.startswith(b'%PDF'), "PDF header check failed")
        self.assertGreater(len(resp_pdf.data), 1000, "Generated certificate PDF is too small")

        self.logout()

        # Step 6: Public Verification
        resp_pub = self.client.get(f'/v/{degree_doc.doc_hash}')
        self.assertEqual(resp_pub.status_code, 200)
        pub_html = resp_pub.get_data(as_text=True)
        self.assertIn('Authentic credential', pub_html)
        self.assertIn(degree_doc.doc_hash, pub_html)
        self.assertIn('Rohit Verma', pub_html)

        # Step 7: Authenticated Employer Verification & Audit Logging
        self.login('techcorp.hr', 'password123')
        resp_verifier = self.client.get(f'/verifier/v/{degree_doc.doc_hash}')
        self.assertEqual(resp_verifier.status_code, 200)
        ver_html = resp_verifier.get_data(as_text=True)
        self.assertIn('Authentic credential', ver_html)

        # Verify VerificationLog entry created
        vlog = VerificationLog.query.filter_by(doc_id=degree_doc.id, verifier_id=self.verifier_user.id).first()
        self.assertIsNotNone(vlog, "VerificationLog entry not created for employer check")
        self.assertEqual(vlog.result, 'VALID')

        # Verify Notification generated for student
        notif = Notification.query.filter_by(student_id=self.student_profile.id, doc_id=degree_doc.id).first()
        self.assertIsNotNone(notif, "Student Notification not created upon verification")
        self.assertIn('Verified', notif.title)

        self.logout()


# ==============================================================================
# TEST RUNNER & FORMATTED REPORTING
# ==============================================================================
def run_all_e2e_tests():
    """Execute all test suites with structured console output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestTier1FeatureCoverage))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2BoundaryCases))
    suite.addTests(loader.loadTestsFromTestCase(TestTier3CrossFeatureAndStateIsolation))
    suite.addTests(loader.loadTestsFromTestCase(TestTier4RealWorldScenarios))

    print("\n" + "=" * 70)
    print(" SATYAMEVA BULK ISSUANCE — END-TO-END AUTOMATED TEST SUITE ")
    print("=" * 70)
    print(f" Loaded {suite.countTestCases()} test cases across Tiers 1 to 4.")
    print("=" * 70 + "\n")

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print(f" TEST RUN COMPLETED in {elapsed:.2f}s")
    print(f" Total Tests: {result.testsRun}")
    print(f" Passed:      {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" Failures:    {len(result.failures)}")
    print(f" Errors:      {len(result.errors)}")
    print("=" * 70)

    if result.wasSuccessful():
        print(" >>> ALL BULK ISSUANCE E2E TESTS PASSED SUCCESSFULLY! <<<")
        return 0
    else:
        print(" >>> SOME TESTS FAILED / REPORTED ERRORS <<<")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_all_e2e_tests())
