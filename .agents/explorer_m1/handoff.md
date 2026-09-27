# Milestone 1 Handoff Report: Bulk Issuance Investigation & Blueprint

## 1. Observation
- **`routes/issuer_routes.py`**: Currently defines single-credential issuance at `GET/POST /issuer/issue` (lines 76–168). It validates single form fields using `_validate_issue()`, auto-provisions student accounts when absent (lines 97–125), and calls `services.credential_service.issue_credential()` (lines 152–157). No bulk-issue or sample-CSV routes currently exist in this file.
- **`services/credential_service.py`**: `issue_credential()` function (lines 17–95) accepts `file_bytes=None`, computes hash via `security.create_document_hash(file_bytes, metadata, salt)` using fallback `'no-file'` (seen in `security.py` line 64), creates the `Doc` model instance with `file_data=None`, and calls `blockchain.mine_block()` sequentially.
- **`services/stamp_service.py`**: `generate_stamped_pdf()` (lines 305–330) explicitly checks `if doc.file_data and doc.is_previewable_image` and gracefully appends `build_certificate_page(doc, student, verify_url)` when no image/file is attached.
- **`templates/base.html`**: Lines 59–63 define issuer navigation with only `Dashboard` (`issuer.dashboard`) and `Issue Document` (`issuer.issue`).
- **`templates/issuer/dashboard.html`**: Lines 20–28 define hero action buttons with only `Issue New Document`.
- **`ORIGINAL_REQUEST.md` & `PROJECT.md`**: Specify requirements R1 (Bulk Issue UI & sample download), R2 (All-or-nothing synchronous CSV validation on `roll_number,doc_type,title`), R3 (Text-only credential issuance with blockchain anchoring & email notifications).

## 2. Logic Chain
1. **Observation 1 & 2**: `issue_credential()` and `Doc` already support text-only credentials (`file_bytes=None`) natively without requiring database schema changes or changes to core cryptographic hashing.
2. **Observation 1**: To support bulk issuance, `routes/issuer_routes.py` needs `/issuer/bulk-issue` (GET/POST) and `/issuer/sample-csv` / `/issuer/template.csv` (GET) along with a CSV validator.
3. **Observation 1 & 5**: The CSV validator must implement synchronous all-or-nothing validation before any DB write or block mining. If any row has missing required fields (`roll_number`, `doc_type`, `title`), invalid `doc_type`, or malformed `validity_days`, the validator returns a list of row-specific error messages and aborts processing, returning HTTP 400.
4. **Observation 1 & 4**: Auto-provisioning of students can be extracted into `_get_or_create_student()` to deduplicate logic between single issuance and bulk issuance.
5. **Observation 3 & 4**: Navigational links must be added to `templates/base.html` and `templates/issuer/dashboard.html` to integrate the new bulk issuance workflow into the existing UI hierarchy seamlessly.

## 3. Caveats
- `validity_days` in CSV is optional. When blank, the blueprint uses `default_validity_days(doc_type)`.
- Student auto-provisioning creates student logins with default password `satyameva123` consistent with single-issue behavior.
- Emails in `issue_credential` are dispatched asynchronously/fire-and-forget in a `try...except` block, so email transport failures do not fail credential issuance.

## 4. Conclusion
The implementation blueprint in `.agents/explorer_m1/blueprint.md` provides all exact additions and templates for Milestone 1. The codebase is fully ready for implementation across:
1. `routes/issuer_routes.py`: Addition of `_get_or_create_student()`, `_parse_and_validate_csv()`, `bulk_issue()`, and `sample_csv()`.
2. `static/template.csv`: Standard sample template with required headers and 5 sample rows.
3. `templates/issuer/bulk_issue.html`: Full UI page with file picker, format guidelines, and error list presentation.
4. `templates/base.html` & `templates/issuer/dashboard.html`: Issuer navigation links.

## 5. Verification Method
1. **Sample CSV Route Check**:
   - Issue `GET /issuer/sample-csv` and `GET /issuer/template.csv` -> Verify response status 200 and headers match `roll_number,student_name,doc_type,title,validity_days`.
2. **All-or-Nothing Error Check**:
   - Post a CSV containing invalid `doc_type` in row 2 -> Verify HTTP 400, verify error details on row 2, and verify database count of `Doc` remains 0.
3. **Valid Batch Check**:
   - Post a valid 3-row CSV -> Verify HTTP 302 redirect, verify 3 new `Doc` records created in SQLite, and verify 3 new blocks added to blockchain.
4. **Integration Test Suite**:
   - Execute test script via `python -m pytest` or `python test_e2e.py`.
