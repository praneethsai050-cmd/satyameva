# Satyameva Bulk Issuance Test Infrastructure

## Overview
This document defines the test architecture, fixtures, isolation strategy, and test inventory for the Satyameva Bulk Issuance end-to-end test suite (`test_bulk_issue_e2e.py`).

The test suite is built strictly to verify the interface contracts and acceptance criteria defined in `PROJECT.md` and `ORIGINAL_REQUEST.md`.

---

## 1. Test Architecture & Environment Isolation

### 1.1 Pure Python Standard Library Runner
- Test runner: Python `unittest` framework.
- Executable via standard command: `python test_bulk_issue_e2e.py` or `python -m unittest test_bulk_issue_e2e.py`.
- No external test harness dependencies (such as pytest) are required.

### 1.2 Hermetic State Isolation
- **Temporary Database**: Every test suite run generates a fresh, isolated temporary SQLite database located in a dedicated `tempfile.mkdtemp()` directory.
- **Temporary Blockchain Ledger**: The `blockchain_instance.storage_file` is dynamically redirected to a temporary JSON file in the sandbox directory for each test case.
- **PoW Difficulty**: Blockchain mining difficulty is set to `1` in the test configuration (`app.config['POW_DIFFICULTY'] = 1`), enabling instantaneous block mining while strictly executing real Proof-of-Work hashing and validation routines.
- **Suppressed Email Sending**: `app.config['MAIL_SUPPRESS_SEND'] = True` is enforced to prevent external network I/O or SMTP connection attempts during test execution.
- **CSRF Disabled**: `app.config['WTF_CSRF_ENABLED'] = False` is set for deterministic REST/form testing.

---

## 2. Test Inventory Matrix

| Tier | Test ID | Description | Specification Reference |
| :--- | :--- | :--- | :--- |
| **Tier 1** | `test_ac1_missing_required_columns_error_and_zero_docs` | Tests that missing required columns (`roll_number`, `doc_type`, or `title`) rejects the batch, produces 0 docs, and mines 0 blocks. | `ORIGINAL_REQUEST §AC1` |
| **Tier 1** | `test_ac2_valid_3_row_csv_creates_3_docs_and_3_blocks` | Tests that a valid 3-row CSV creates exactly 3 `Doc` records with `file_data=None` and mines 3 new sequential blocks. | `ORIGINAL_REQUEST §AC2` |
| **Tier 1** | `test_ac3_text_only_credentials_render_safely_across_all_views` | Tests text-only credential rendering on Student Dashboard, Document Detail view, Stamped PDF generation, and Public Verify page. | `ORIGINAL_REQUEST §AC3` |
| **Tier 1** | `test_ac4_sample_template_csv_served_with_proper_headers` | Tests that `GET /issuer/sample-csv` (and `/issuer/template.csv`) serves a valid CSV attachment with expected headers. | `ORIGINAL_REQUEST §AC4` |
| **Tier 1** | `test_bulk_issue_ui_endpoint_accessible` | Tests `GET /issuer/bulk-issue` renders the bulk upload form with file input and `.csv` restriction. | `ORIGINAL_REQUEST §R1` |
| **Tier 2** | `test_boundary_empty_csv_file` | Verifies rejection of 0-byte uploaded files with 0 docs and 0 blocks created. | `Boundary Cases` |
| **Tier 2** | `test_boundary_header_only_csv` | Verifies rejection of CSV containing only headers and 0 data rows. | `Boundary Cases` |
| **Tier 2** | `test_boundary_whitespace_in_headers_and_values` | Verifies trimming and normalization of whitespace in headers and field values. | `Robustness` |
| **Tier 2** | `test_boundary_missing_values_middle_row_fails_all_or_nothing` | Verifies strict all-or-nothing atomicity: in a 5-row batch where row 3 has missing fields, entire batch fails with 0 writes. | `ORIGINAL_REQUEST §R2` |
| **Tier 2** | `test_boundary_utf8_bom_encoding` | Verifies compatibility with UTF-8 BOM headers common in Microsoft Excel CSV exports. | `Encoding Integrity` |
| **Tier 2** | `test_boundary_invalid_doc_type` | Verifies rejection when an unknown/unsupported document type is supplied. | `Schema Validation` |
| **Tier 2** | `test_boundary_non_numeric_validity_days` | Verifies rejection when `validity_days` is non-numeric or invalid. | `Data Types` |
| **Tier 2** | `test_boundary_non_csv_file_extension` | Verifies rejection of non-CSV file uploads (`.txt`, `.pdf`, `.png`). | `File Constraints` |
| **Tier 3** | `test_state_isolation_failed_batch_leaves_state_clean_for_subsequent_batch` | Tests that a failed batch leaves the ledger clean so a subsequent valid batch succeeds cleanly. | `State Isolation` |
| **Tier 3** | `test_sequential_multiple_batches_mining_successive_blocks` | Tests successive batch issuance (Batch 1: 2 docs -> blocks #1,#2; Batch 2: 3 docs -> blocks #3,#4,#5) with cryptographic link verification. | `Ledger Integrity` |
| **Tier 3** | `test_student_auto_provisioning_and_login_view` | Tests auto-provisioning of new students included in CSV, verified via student portal login and dashboard access. | `Auto-Provisioning` |
| **Tier 3** | `test_public_verifier_query_bulk_issued_hash` | Tests public verification of generated hash via `/verify` and `/v/<hash>`. | `Public Verification` |
| **Tier 4** | `test_full_e2e_bulk_issuance_lifecycle` | Comprehensive real-world workflow: Issuer login -> template download -> bulk issue 3 credentials -> DB & blockchain check -> student login & dashboard view -> stamped PDF generation -> public verify -> employer verify audit log & notification. | `Full E2E Lifecycle` |

---

## 3. How to Run the Tests

Run via standard Python runner from project root:
```bash
python test_bulk_issue_e2e.py
```

Or via unittest module:
```bash
python -m unittest test_bulk_issue_e2e.py
```
