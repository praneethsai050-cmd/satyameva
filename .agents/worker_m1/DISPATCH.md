## 2026-08-29T17:23:00Z
Working directory: c:/Users/hp/OneDrive/Desktop/SIH_Aegis/.agents/worker_m1/
Project root: c:/Users/hp/OneDrive/Desktop/SIH_Aegis/

Mandatory inputs:
- Read c:/Users/hp/OneDrive/Desktop/SIH_Aegis/.agents/ORIGINAL_REQUEST.md
- Read c:/Users/hp/OneDrive/Desktop/SIH_Aegis/PROJECT.md
- Read c:/Users/hp/OneDrive/Desktop/SIH_Aegis/.agents/explorer_m1/blueprint.md
- Read c:/Users/hp/OneDrive/Desktop/SIH_Aegis/.agents/explorer_m1/handoff.md

Exclusive Write Ownership:
- routes/issuer_routes.py
- templates/issuer/bulk_issue.html
- templates/base.html
- templates/issuer/dashboard.html
- static/template.csv

Implementation Tasks:
1. In `routes/issuer_routes.py`:
   - Implement `_get_or_create_student()` helper to deduplicate student account creation.
   - Implement `_parse_and_validate_csv()` with UTF-8 BOM handling (`utf-8-sig`), whitespace stripping, required headers validation (`roll_number`, `doc_type`, `title`), row-by-row field validation, and error collection.
   - Implement `/issuer/bulk-issue` (GET and POST):
     - GET: render `issuer/bulk_issue.html`.
     - POST: handle `.csv` file upload, run all-or-nothing validation. If invalid, return HTTP 400 (or render with errors) showing what failed; ensure 0 DB rows created and 0 blocks mined. If valid, iterate rows, auto-provision student, invoke `services.credential_service.issue_credential(student=student, issuer=issuer, doc_type=doc_type, title=title, file_bytes=None, file_name=None, validity_days=validity_days, extra_fields=extra_fields)`. Flash success message and redirect to `issuer.dashboard`.
   - Implement `/issuer/sample-csv` and `/issuer/template.csv` (GET): serve `static/template.csv` as attachment.
2. Create `static/template.csv` with standard headers (`roll_number,student_name,doc_type,title,validity_days`) and 3-5 illustrative sample rows.
3. Create `templates/issuer/bulk_issue.html` containing the `.csv` file upload input, sample CSV download link, instructions table, and error summary.
4. Update `templates/base.html` and `templates/issuer/dashboard.html` with Bulk Issue navigation links.
5. Verification:
   Run verification tests:
   `$env:PYTHONIOENCODING="utf-8"; python test_e2e.py`
   `$env:PYTHONIOENCODING="utf-8"; python test_bulk_issue_e2e.py` (if created) or custom verification script.
