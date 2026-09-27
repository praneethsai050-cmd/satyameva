# Original User Request

## 2026-08-29T17:15:55Z

Add a Bulk Issuance feature to the Satyameva credentialing system. Issuers should be able to upload a CSV file to issue multiple credentials to students in a single batch.

Working directory: ~/teamwork_projects/satyameva_bulk_issue
Integrity mode: demo

## Requirements

### R1. Bulk Issue UI
Add a "Bulk Issue" interface in the Issuer Portal. It must include a file upload field restricted to `.csv` and a small link/button to download a sample CSV template.

### R2. All-or-Nothing CSV Validation
Process the uploaded CSV synchronously. The CSV must contain columns for the required credential data (e.g., `roll_number`, `doc_type`, `title`). If *any* row fails validation (e.g. missing fields), the entire batch must fail, no credentials should be issued, and the issuer should see an error message explaining what failed.

### R3. Text-Only Credential Issuance
For valid batches, iterate through the rows and issue the credentials. Because this is bulk issuance, these will be "data credentials" (text-only) with no associated PDF/image file. Ensure they are anchored to the blockchain and trigger the standard email notifications.

## Acceptance Criteria

### Verification (Objective Testing)
- [ ] Submitting a CSV with missing required columns immediately returns an error and creates 0 documents.
- [ ] Submitting a valid CSV with 3 rows successfully creates exactly 3 new `Doc` records in the SQLite database and mines 3 new blocks.
- [ ] The generated text-only credentials can be viewed on the student dashboard and public verify page without crashing (despite lacking a physical file upload).
- [ ] A sample `template.csv` is correctly served and contains the proper headers.
