# Satyameva Bulk Issuance Test Suite — Ready Status

## Test Suite Summary
- **Test File**: `test_bulk_issue_e2e.py`
- **Runner Framework**: Standard Python `unittest` (no pytest required)
- **Total Test Cases**: 18
- **Tiers Covered**:
  - **Tier 1 (Feature Coverage)**: 5 tests (AC1 missing columns error, AC2 3-row valid batch, AC3 text-only multi-view rendering, AC4 sample template serving, UI endpoint)
  - **Tier 2 (Boundary & Corner Cases)**: 8 tests (empty file, header-only CSV, whitespace trimming, 5-row middle-row failure all-or-nothing, UTF-8 BOM encoding, invalid doc type, non-numeric validity days, non-CSV extension)
  - **Tier 3 (Cross-Feature & State Isolation)**: 4 tests (state isolation after failed batch, sequential multiple batches with blockchain link verification, auto-provisioning student login & dashboard, public verification)
  - **Tier 4 (Real-World Scenarios)**: 1 comprehensive test (Full end-to-end issuer login -> template download -> bulk issue 3 credentials -> student verification -> public verification -> stamped PDF certificate generation -> employer verification log & notification)

## Execution Command
```bash
python test_bulk_issue_e2e.py
```

## Implementation Contract Checklist for Implementer (M1 / M2 / M3)
To achieve a 100% pass rate on `test_bulk_issue_e2e.py`, the implementing agent should implement:
1. `GET /issuer/bulk-issue`: Render bulk issuance upload template with `csv_file` file input restricted to `.csv`.
2. `POST /issuer/bulk-issue`: Process uploaded CSV file:
   - Validate headers: `roll_number`, `doc_type`, `title` (case-insensitive & trimmed; handle UTF-8 BOM `\ufeff`).
   - Validate rows: non-empty required fields, supported `doc_type` in `DOC_TYPES`, positive integer `validity_days` if present.
   - Atomic All-or-Nothing execution: if any row is invalid, do not create any documents or mine any blocks; return 400 or re-render form with error message.
   - For valid batches: iterate rows, auto-provision missing students, invoke `issue_credential(student, current_user, doc_type, title, file_bytes=None, file_name=None, file_mime=None, validity_days=...)`, mine sequential blocks, redirect to dashboard with success message.
3. `GET /issuer/sample-csv` and `GET /issuer/template.csv`: Serve downloadable CSV template containing headers `roll_number,student_name,doc_type,title,validity_days` and sample data rows.
