# Project: Satyameva Credentialing — Bulk Issuance Feature

## Architecture
- **Framework**: Python 3.14 + Flask 3.0 + Flask-SQLAlchemy + Flask-Login + Flask-Mail + Pillow + qrcode.
- **Blueprints**:
  - `auth`: Authentication & session management (`routes/auth_routes.py`).
  - `issuer`: Credential issuance, batch issuance, sample template serving (`routes/issuer_routes.py`).
  - `student`: Credential viewer, download, stamped PDF generation (`routes/student_routes.py`).
  - `public`: Public verification of credentials against blockchain (`routes/public_routes.py`).
  - `verifier`: Third-party verification portal (`routes/verifier_routes.py`).
- **Core Services**:
  - `services/credential_service.py`: Core credential lifecycle (`issue_credential()`), cryptographic hashing (`security.create_document_hash()`), DB record insertion, blockchain mining, and email notification triggering.
  - `blockchain.py`: Proof-of-work blockchain ledger, dual-persisted in SQLite `block` table and `instance/blockchain.json`.
  - `services/stamp_service.py`: Stamped PDF and verification certificate generation.
  - `services/email_service.py`: Student and issuer notification emails.
- **Database**: SQLite at `instance/satyameva.db` with models `User`, `Student`, `Issuer`, `Doc`, `Block`.

## Feature Inventory
| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|--------|
| 1 | R1.1 Bulk Issue UI | Dedicated Bulk Issue form in Issuer Portal with `.csv` file upload input, styled guidance, and navigation integration. | M2 | ORIGINAL_REQUEST §R1 | DONE |
| 2 | R1.2 Sample Template | Endpoint and static file serving `template.csv` with valid headers and sample data, linked from Bulk Issue UI. | M2 | ORIGINAL_REQUEST §R1, AC4 | DONE |
| 3 | R2.1 CSV Parser & Header Check | Synchronous CSV parser handling header normalization, BOM stripping, and required column validation (`roll_number`, `doc_type`, `title`). | M1 | ORIGINAL_REQUEST §R2 | DONE |
| 4 | R2.2 All-or-Nothing Batch Validator | Pre-validation of every row before any database write or blockchain mining; any invalid row halts the batch, creates 0 documents, mines 0 blocks, and returns error details. | M1 | ORIGINAL_REQUEST §R2, AC1 | DONE |
| 5 | R3.1 Text-Only Batch Issuance | Atomic batch execution invoking `issue_credential()` with `file_bytes=None`, creating `Doc` records, auto-provisioning students if required. | M1 | ORIGINAL_REQUEST §R3, AC2 | DONE |
| 6 | R3.2 Blockchain Anchoring | Sequential block mining for each credential in the batch, updating SQLite and `blockchain.json`. | M1 | ORIGINAL_REQUEST §R3, AC2 | DONE |
| 7 | R3.3 Email Notification | Triggering standard multi-part student and issuer email notifications per issued credential. | M1 | ORIGINAL_REQUEST §R3 | DONE |
| 8 | R3.4 Student Dashboard & Detail Display | Safe rendering of text-only credentials on student dashboard and document detail page without crashing, supporting verification certificate download. | M3 | ORIGINAL_REQUEST §R3, AC3 | DONE |
| 9 | R3.5 Public Verification Display | Safe public verification and cryptographic verification of text-only credentials without crashing. | M3 | ORIGINAL_REQUEST §R3, AC3 | DONE |
| 10 | E2E Test Suite | Comprehensive 4-Tier test suite verifying all acceptance criteria and edge cases. | E2E-Track | ORIGINAL_REQUEST §Acceptance Criteria | DONE |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Track | Build comprehensive opaque-box test suite (`test_bulk_issue_e2e.py`) covering Tiers 1-4. | None | DONE |
| M1 | Backend Bulk Issuance Engine | Implement CSV parsing, all-or-nothing validation, sample CSV route, and batch issuance in `routes/issuer_routes.py` and `services/credential_service.py`. | None | DONE |
| M2 | Issuer UI & Template Integration | Create `templates/issuer/bulk_issue.html`, static `static/template.csv`, navigation links in `templates/base.html` and `templates/issuer/dashboard.html`. | M1 | DONE |
| M3 | Student & Public View Resilience | Verify and harden student dashboard, detail view, stamped PDF certificate, and public verify page for text-only credentials. | M1, M2 | DONE |
| M4 | Final E2E Pass & Hardening | Pass 100% of E2E tests, run Tier 5 Adversarial Hardening with Challengers, and Forensic Audit. | E2E, M1, M2, M3 | DONE |

## Interface Contracts
### Issuer Bulk Issue API / Route Contract
- **Endpoint**: `POST /issuer/bulk-issue`
- **Content-Type**: `multipart/form-data`
- **Form Field**: `csv_file` (FileStorage, restricted to `.csv`)
- **CSV Required Headers**: `roll_number`, `doc_type`, `title`
- **CSV Optional Headers**: `student_name`, `validity_days`, `extra_fields`
- **Success Response**: Redirect to `issuer.dashboard` with flash message `"Successfully issued N credentials in bulk."`
- **Error Response**: Render `templates/issuer/bulk_issue.html` with HTTP 400 and clear flash error messages detailing row-by-row validation failures; 0 documents created, 0 blocks mined.

### Sample CSV Route Contract
- **Endpoint**: `GET /issuer/sample-csv` and `GET /issuer/template.csv`
- **Response**: `text/csv` attachment with headers `roll_number,student_name,doc_type,title,validity_days` and 5 sample rows.

## Code Layout
- `routes/issuer_routes.py`: Contains `/issuer/bulk-issue` (GET/POST) and `/issuer/sample-csv` routes, CSV parsing and validation logic.
- `templates/issuer/bulk_issue.html`: Bulk Issue template with file upload, CSV guidelines, sample download link.
- `templates/base.html`: Issuer navigation bar link to Bulk Issue.
- `templates/issuer/dashboard.html`: Quick action button to Bulk Issue.
- `static/template.csv`: Static sample CSV template.
- `test_bulk_issue_e2e.py`: End-to-end automated test runner for Bulk Issuance.
