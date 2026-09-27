# Satyameva Bulk Issuance: Testing Infrastructure, Environment & Verification Report

**Author**: `explorer_survey_infra_test`  
**Date**: 2026-08-29  
**Status**: Investigation Complete  

---

## 1. Executive Summary

This report documents the testing infrastructure, runtime environment, database architecture, blockchain persistence mechanisms, and existing test suites for the **Satyameva** credentialing platform. It also specifies a concrete verification strategy for the proposed **Bulk Issuance** feature covering all acceptance criteria outlined in `ORIGINAL_REQUEST.md`.

### Key Findings at a Glance
- **Python Environment**: Python 3.14.7 on Windows x64. Standard library test runner (`unittest`) and direct script execution (`python <script>.py`) are used. `pytest` is **not** installed in the environment.
- **Console / Shell Quirk**: Under Windows PowerShell with `cp1252` encoding, terminal output containing Unicode box characters (e.g. `\u2500` in test banners) requires `$env:PYTHONIOENCODING="utf-8"` or `$env:PYTHONUTF8=1`.
- **Database & Storage**: SQLite database at `instance/satyameva.db` combined with a persistent JSON blockchain mirror at `instance/blockchain.json`. Tables are auto-created on `create_app()`.
- **Issuance Architecture**: Credential issuance is handled by `services/credential_service.py:issue_credential()`, which natively supports `file_bytes=None`. In this case, `security.py` hashes metadata against `'no-file'`, storing `file_data=None`, `file_digest=None`.
- **Existing Test Coverage**: 3 robust suites exist (`test_e2e.py`, `_smoke.py`, `_assert.py`), all passing 100%.
- **Email Handling in Tests**: External SMTP calls to Gmail are caught and logged without breaking transactions. Setting `app.config['MAIL_SUPPRESS_SEND'] = True` in test configurations prevents unnecessary network timeouts.

---

## 2. Testing Infrastructure & Runtime Environment

### 2.1 Python Interpreter & Dependencies

| Component | Specification / Version | Notes |
|---|---|---|
| **Python** | `3.14.7` (Windows 64-bit) | Located at `C:\Python314\python.exe` |
| **Flask** | `3.0.0` | Application web framework |
| **Flask-SQLAlchemy** | `3.1.1` (SQLAlchemy `2.0.52`) | ORM abstraction over SQLite |
| **Flask-Login** | `0.6.3` | Session management & RBAC |
| **Flask-Mail** | `0.10.0` | Email dispatch service |
| **Pillow** | `12.3.0` | Certificate generation, stamping & PDF creation |
| **qrcode** | `7.4.2` | QR code generation for verification |
| **Werkzeug** | `3.0.1` | WSGI utilities, password hashing & secure filenames |

### 2.2 Test Runners & Execution Strategy

- **`pytest` Status**: Not installed (`No module named pytest`).
- **Standard Test Method**: Direct Python invocation (`python <test_script>.py`) or `python -m unittest discover`.
- **Recommended Execution Command**:
  ```powershell
  $env:PYTHONIOENCODING="utf-8"; python test_e2e.py
  $env:PYTHONIOENCODING="utf-8"; python _smoke.py
  $env:PYTHONIOENCODING="utf-8"; python _assert.py
  ```

### 2.3 Email & Network Isolation in Tests

In `config.py`, `MAIL_SUPPRESS_SEND` is set to `False` by default. When running unit/integration tests:
```python
app.config['TESTING'] = True
app.config['MAIL_SUPPRESS_SEND'] = True
```
This instructs `Flask-Mail` to suppress outgoing SMTP connections while preserving the issuance flow and email template rendering.

---

## 3. Database Configuration & Ledger Architecture

### 3.1 SQLite Database (`instance/satyameva.db`)

- **URI**: `sqlite:///<BASE_DIR>/instance/satyameva.db` (configured in `config.py:19`).
- **Initialization**: `app.py:create_app()` ensures `os.makedirs('instance', exist_ok=True)`, calls `db.create_all()`, and executes `ensure_genesis_block()`.
- **Reset & Seeding**: `python seed.py --reset` wipes the database, recreates tables, seeds the genesis block, and populates 6 demo credentials for `aarav.sharma`, 1 revoked credential for `priya.nair`, and historical verification logs.

### 3.2 Data Models Schema

| Model | Table | Key Fields | Purpose |
|---|---|---|---|
| **`User`** | `user` | `id`, `username`, `email`, `role`, `organization`, `password_hash`, `password_salt` | Auth accounts (roles: `student`, `issuer`, `verifier`, `admin`) |
| **`Student`** | `student` | `id`, `user_id`, `full_name`, `roll_number`, `program`, `department`, `institution` | Academic profile linked to `User` |
| **`Doc`** (`Document`) | `doc` | `id`, `student_id`, `issuer_id`, `doc_type`, `title`, `issuer_name`, `doc_hash`, `hash_salt`, `file_digest`, `payload`, `file_data`, `file_name`, `file_mime`, `issued_on`, `valid_until`, `block_index`, `tx_hash`, `revoked`, `verification_count` | Issued academic credentials |
| **`Block`** | `block` | `id`, `index`, `timestamp`, `data`, `proof`, `previous_hash`, `hash`, `doc_hash` | Blockchain ledger blocks |
| **`VerificationLog`** | `verification_log` | `id`, `doc_id`, `verifier_id`, `verifier_label`, `queried_hash`, `ipv4`, `ipv6`, `user_agent`, `method`, `result`, `timestamp` | Audit trail for credential verifications |
| **`Notification`** | `notification` | `id`, `student_id`, `doc_id`, `title`, `message`, `category`, `is_read`, `created_at` | Student in-app notifications |
| **`FraudReport`** | `fraud_report` | `id`, `doc_hash`, `verifier_id`, `notes`, `timestamp` | Verifier fraud registry |

### 3.3 Blockchain Persistence (`instance/blockchain.json`)

- Implemented in `blockchain.py`.
- **Genesis Block (#0)**: `previous_hash = '0'*64`, `proof = 1`, `doc_hash = None`.
- **Proof-of-Work**: Leading zeros difficulty = 4 (`POW_DIFFICULTY = 4`). Nonce search iterates until SHA-256 hash matches `0000...`.
- **Double Storage**: Every block mined via `mine_block(payload, doc_hash)` writes to SQLite `block` table AND synchronizes with `instance/blockchain.json`.
- **Integrity Validation**: `validate_chain()` walks all blocks sequentially, recomputing block digests and verifying previous hash links.

---

## 4. Existing Test Suite Analysis

### 4.1 Test Suites Overview

| Suite | File | Tests / Checks Covered | Execution Time | Current Status |
|---|---|---|---|---|
| **E2E Integration** | `test_e2e.py` | 6 workflows: Genesis validation, Unified 3-role registration, Document issuance & PoW mining, Student dashboard & detail QR rendering, Verifier hash check + notification + fraud reporting, Student notification check. | ~3.5s | **PASS** |
| **Smoke Suite** | `_smoke.py` | 23 endpoints: Public routes, unauth redirects, student dashboard filters, 6 owned document views (preview, qr.png, qr.json, download, download/image), 403 RBAC foreign doc isolation, logout. | ~1.5s | **PASS** |
| **Assertion Suite** | `_assert.py` | Behavioural checks: Dynamic QR token lifecycle (fresh, stale, mismatched, unknown), Verification logging, Session idle timeout (5m sliding window), RBAC barriers between roles. | ~2.0s | **PASS** |

### 4.2 Code Inspection: Issuance of File-Less / Text-Only Credentials

In `services/credential_service.py`:
```python
def issue_credential(student, issuer, doc_type, title, *, file_bytes=None,
                     file_name=None, file_mime=None, validity_days=None,
                     issued_on=None, extra=None, difficulty=4) -> Doc:
```
When `file_bytes=None`:
1. `file_digest` becomes `None`.
2. In `security.py:create_document_hash`:
   ```python
   file_digest = hashlib.sha256(file_bytes).hexdigest() if file_bytes else 'no-file'
   material = f'{salt}|{file_digest}|{canonical_payload(metadata)}'
   return hashlib.sha256(material.encode('utf-8')).hexdigest()
   ```
3. In `security.py:recompute_document_hash`:
   ```python
   file_digest = doc.file_digest or 'no-file'
   material = f'{doc.hash_salt}|{file_digest}|{doc.payload or ""}'
   return hashlib.sha256(material.encode('utf-8')).hexdigest()
   ```
4. In `services/stamp_service.py:generate_stamped_pdf`:
   - Checks `if doc.file_data and doc.is_previewable_image: ...`
   - For file-less credentials, it skips rasterizing the source file and renders the standalone A4 **Verification Certificate** page containing student details, document details, blockchain anchor band, QR code, and SHA-256 hash.

---

## 5. Acceptance Criteria Verification Strategy

The following matrix details the objective verification strategy for each requirement in `ORIGINAL_REQUEST.md`.

### 5.1 AC1: All-or-Nothing CSV Validation (0 Documents Created on Error)

#### Test Cases:
1. **Missing Required Header**: CSV missing `roll_number`, `doc_type`, or `title`.
2. **Empty Field in a Row**: Row 2 has an empty `title` or empty `roll_number`.
3. **Invalid Document Type**: Row 3 has `doc_type = 'INVALID_TYPE'` (not in `DOC_TYPES`).
4. **Invalid Validity Value**: Row 1 has `validity_days = '-10'` or `'abc'`.
5. **Non-CSV Upload**: Uploading `.txt`, `.pdf`, or empty file.

#### Verification Procedure:
```python
# Initial state
initial_doc_count = Doc.query.count()
initial_block_count = Block.query.count()

# Submit invalid CSV
resp = client.post('/issuer/bulk-issue', data={
    'csv_file': (io.BytesIO(invalid_csv_bytes), 'invalid.csv')
}, follow_redirects=True)

# Assertions
assert resp.status_code == 200
assert 'error' in resp.get_data(as_text=True).lower() or 'missing' in resp.get_data(as_text=True).lower()
assert Doc.query.count() == initial_doc_count      # Exactly 0 new docs
assert Block.query.count() == initial_block_count  # Exactly 0 new blocks mined
```

---

### 5.2 AC2: Valid 3-Row CSV Batch Issuance (Creates 3 Docs & Mines 3 Blocks)

#### Test CSV Content:
```csv
roll_number,doc_type,title,student_name,validity_days
BULK2026_01,DEGREE,Bachelor of Technology in Data Science,Alice Johnson,3650
BULK2026_02,MARKSHEET,Semester 8 Grade Report,Bob Smith,3650
BULK2026_03,BONAFIDE,Certificate of Ongoing Enrollment,Charlie Brown,90
```

#### Verification Procedure:
```python
initial_doc_count = Doc.query.count()
initial_block_count = Block.query.count()

resp = client.post('/issuer/bulk-issue', data={
    'csv_file': (io.BytesIO(valid_csv_bytes), 'batch_3.csv')
}, follow_redirects=True)

assert resp.status_code == 200
assert Doc.query.count() == initial_doc_count + 3
assert Block.query.count() == initial_block_count + 3

# Verify Blockchain Integrity
ok, msg = validate_chain()
assert ok, f"Blockchain invalid after bulk issue: {msg}"

# Verify each doc properties
new_docs = Doc.query.filter(Doc.student.has(Student.roll_number.in_(['BULK2026_01', 'BULK2026_02', 'BULK2026_03']))).all()
assert len(new_docs) == 3
for doc in new_docs:
    assert doc.file_data is None
    assert doc.file_digest is None
    assert doc.block_index is not None
    assert doc.doc_hash is not None
```

---

### 5.3 AC3: Text-Only Credential Dashboard & Public Verification Resilience

#### Test Cases & Verification Steps:
1. **Student Dashboard (`/student/dashboard`)**:
   - Log in as student `student.bulk2026_01`.
   - `GET /student/dashboard` -> status 200.
   - Assert HTML contains `Bachelor of Technology in Data Science`, status badge `Valid`, and rendered `data:image/png;base64` card QR code.
2. **Student Document Detail (`/student/document/<id>`)**:
   - `GET /student/document/<id>` -> status 200.
   - Assert HTML contains `No file preview`, `This credential exists as ledger metadata only`, Block `#<index>`, and dynamic QR code.
3. **Student Download Stamped PDF (`/student/document/<id>/download`)**:
   - `GET /student/document/<id>/download` -> status 200, Content-Type `application/pdf`.
   - Verify binary payload starts with `%PDF-` and contains valid certificate structure.
4. **Public Verification (`/v/<doc_hash>`)**:
   - Unauthenticated `GET /v/<doc_hash>` -> status 200.
   - Assert HTML contains `Authentic credential`, `Alice Johnson`, `BULK2026_01`, block index, and `chain intact`.
5. **Verifier Search (`/verify`)**:
   - `POST /verify` with `doc_hash` -> redirects to `/v/<doc_hash>` and renders valid verdict.

---

### 5.4 AC4: Sample `template.csv` Serving & Header Schema

#### Verification Procedure:
1. **Route Endpoint**: `GET /issuer/template.csv` (or `/issuer/bulk-issue/template.csv`).
2. **Assertions**:
   - HTTP status code: 200.
   - Content-Type: `text/csv; charset=utf-8` (or `application/octet-stream`).
   - Content-Disposition header contains `attachment; filename=...`.
   - CSV content parsed:
     - Header row must contain at minimum: `roll_number`, `doc_type`, `title`.
     - Recommended optional columns: `student_name`, `validity_days`.
     - Sample data row provides valid example inputs (e.g. `22103045,DEGREE,Bachelor of Science,Aarav Sharma,3650`).

---

## 6. Recommended Test Suite Architecture for Bulk Issuance

We recommend creating an automated test file `test_bulk_issue.py` (or integrating into `test_e2e.py`) structured as follows:

```python
"""
test_bulk_issue.py - Dedicated test suite for Bulk Issuance feature.
"""
import io
import os
from app import create_app
from extensions import db
from models import Doc, Student, Block, User
from blockchain import validate_chain

def run_bulk_tests():
    app = create_app()
    app.config['TESTING'] = True
    app.config['MAIL_SUPPRESS_SEND'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    with app.app_context():
        # 1. Login as Issuer
        # 2. Test sample template download (AC4)
        # 3. Test missing column error & 0 docs created (AC1)
        # 4. Test row-level error rollback & 0 docs created (AC1)
        # 5. Test 3-row valid CSV issuance (AC2)
        # 6. Test student dashboard, detail view, stamped PDF download (AC3)
        # 7. Test public /v/<doc_hash> verification without crash (AC3)
        # 8. Re-verify validate_chain()
```

---

## 7. Conclusion & Next Steps

The existing infrastructure in `SIH_Aegis` provides exceptional native support for text-only credential hashing (`'no-file'` digest in `security.py`), blockchain PoW mining (`blockchain.py`), and dynamic PDF verification certificate rendering (`services/stamp_service.py`). Implementing the Bulk Issuance feature requires only:
1. Issuer Bulk Issue route & template upload handling with all-or-nothing CSV parsing.
2. Sample CSV template download endpoint.
3. Issuer portal UI additions (tab/link to Bulk Issue and download button).
4. Running the verification test suite (`test_bulk_issue.py` and `test_e2e.py`).
