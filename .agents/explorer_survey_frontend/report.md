# Frontend & UI Investigation Report: Satyameva Credentialing Bulk Issuance

**Date:** 2026-08-29  
**Agent:** explorer_survey_frontend  
**Scope:** Issuer Portal, Student Dashboard, Public Verify Page, CSV Template Serving, and Text-Only Credential UI Display.

---

## Executive Summary

This investigation analyzed the frontend templates, UI components, interaction layer, and rendering logic across the Satyameva platform to determine how to integrate the **Bulk Issuance** feature and ensure seamless rendering of **text-only (data) credentials** without physical file attachments.

### Key Conclusions:
1. **Issuer Portal UI**: A dedicated `/issuer/bulk-issue` route and template (`templates/issuer/bulk_issue.html`) should be added alongside `/issuer/issue`. Navigation should be updated in `templates/base.html` and quick-access buttons added on `templates/issuer/dashboard.html`.
2. **Bulk Issue Interface (R1)**: The form requires `enctype="multipart/form-data"`, an `<input type="file" accept=".csv" required>`, and a direct download button/link to `/issuer/sample-csv` (and `/static/template.csv`).
3. **Student Dashboard UI**: The existing dashboard (`templates/student/dashboard.html`) and document detail page (`templates/student/document_detail.html`) already have built-in fallbacks for file-less credentials (`preview-empty` fallback: *"This credential exists as ledger metadata only"*). The stamped PDF generator (`services/stamp_service.py:generate_stamped_pdf`) generates a complete A4 cryptographic certificate page even when `file_data` is `None`.
4. **Public Verify Page**: The public verify pages (`templates/public/verify.html` and `templates/public/verify_result.html`) display only metadata and blockchain cryptographic proofs. They do not access `file_data` directly. Verification succeeds with `doc.file_digest='no-file'`, verifying text-only credentials without errors or crashes.
5. **Sample CSV Template**: Standard headers `roll_number,student_name,doc_type,title,validity_days` should be provided and served via route endpoint `issuer.sample_csv` as well as a static asset `static/template.csv`.

---

## 1. Issuer Portal UI Architecture

### 1.1 Existing Navigation & Layout
- **Base Shell (`templates/base.html`)**:
  - Contains navigation header (`.nav`) with role-based links.
  - Issuer nav links (lines 59–64 of `templates/base.html`):
    ```html
    {% elif current_user.is_authenticated and current_user.is_issuer %}
      <a class="nav-link {{ 'is-active' if request.endpoint == 'issuer.dashboard' }}"
         href="{{ url_for('issuer.dashboard') }}">Dashboard</a>
      <a class="nav-link {{ 'is-active' if request.endpoint == 'issuer.issue' }}"
         href="{{ url_for('issuer.issue') }}">Issue Document</a>
    {% endif %}
    ```
- **Dashboard (`templates/issuer/dashboard.html`)**:
  - Hero header with 3D canvas and button: `<a class="btn btn-primary" href="{{ url_for('issuer.issue') }}">＋ Issue New Document</a>` (lines 21–23).
  - Statistics grid (Total, Active, Expiring, Expired, Revoked, Verifications).
  - Filter search bar.
  - Responsive document card grid (`.grid-docs`) with accordion detail strips showing SHA-256 hash swatches, block indices, timestamps, and revocation controls.
- **Single Issuance Form (`templates/issuer/issue.html`)**:
  - Endpoint: `POST /issuer/issue`
  - Input fields:
    - `roll_number` (text, required)
    - `student_name` (text, optional)
    - `doc_type` (select dropdown populated from `doc_types`, required)
    - `title` (text, required)
    - `validity_days` (number, optional)
    - `document` (file upload, required, `accept=".png,.jpg,.jpeg,.pdf,.webp"`)

---

## 2. Requirement R1: Bulk Issue Interface Specification

### 2.1 Proposed Route & Navigation Integration
1. **Route**: `GET/POST /issuer/bulk-issue` (`issuer_routes.py` -> `issuer.bulk_issue`).
2. **Template**: `templates/issuer/bulk_issue.html`.
3. **Navigation Updates**:
   - `templates/base.html`: Add `Bulk Issue` nav link:
     ```html
     <a class="nav-link {{ 'is-active' if request.endpoint == 'issuer.bulk_issue' }}"
        href="{{ url_for('issuer.bulk_issue') }}">Bulk Issue</a>
     ```
   - `templates/issuer/dashboard.html`: Add a secondary action button in the Hero section:
     ```html
     <div class="row" style="gap:.75rem; flex-wrap:wrap">
       <a class="btn btn-primary" href="{{ url_for('issuer.issue') }}">
         <span aria-hidden="true">＋</span> Issue Single Document
       </a>
       <a class="btn btn-ghost" href="{{ url_for('issuer.bulk_issue') }}">
         <span aria-hidden="true">📁</span> Bulk Issue (CSV)
       </a>
       <span class="chain-status">
         <span aria-hidden="true">🔗</span>
         <span class="mono">{{ stats.total }}</span> issued
       </span>
     </div>
     ```
   - `templates/issuer/issue.html`: Add a link/banner:
     ```html
     <div class="row row-between" style="margin-bottom:1rem">
       <span class="small faint">Need to issue for a batch of students?</span>
       <a class="btn btn-ghost btn-sm" href="{{ url_for('issuer.bulk_issue') }}">Switch to Bulk Issue →</a>
     </div>
     ```

### 2.2 Template Structure (`templates/issuer/bulk_issue.html`)
The template should follow the design language (`.panel`, `.stack`, `.btn-primary`, `.alert-danger`, `.field-label`):

```html
{% extends 'base.html' %}
{% block title %}Bulk Issue Credentials{% endblock %}

{% block content %}
<div class="stack stack-8">
  <div class="row row-between">
    <div class="stack">
      <span class="hero-kicker">Issuer Portal</span>
      <h1>Bulk Issue Credentials</h1>
      <p class="hero-lead">Upload a CSV file to issue and anchor multiple credentials in a single batch.</p>
    </div>
    <a href="{{ url_for('issuer.dashboard') }}" class="btn btn-ghost">← Back to Dashboard</a>
  </div>

  {% if errors %}
    <div class="alert alert-danger stack stack-2">
      <div class="alert-title"><strong>Validation Failed — No Credentials Issued</strong></div>
      <ul style="margin:0; padding-left:1.25rem">
        {% for err in errors %}
          <li>{{ err }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}

  <section class="panel" style="max-width: 680px;">
    <form method="post" action="{{ url_for('issuer.bulk_issue') }}" enctype="multipart/form-data" class="stack stack-4" novalidate>
      
      <div class="stack stack-3">
        <h3>Upload CSV Batch</h3>
        <p class="small muted" style="margin:0">
          Upload a <code>.csv</code> spreadsheet. All rows are validated synchronously before any credentials are minted.
        </p>

        <div>
          <label class="field-label" for="csv_file">Select CSV File *</label>
          <input type="file" id="csv_file" name="csv_file" class="input" accept=".csv" required>
        </div>
      </div>

      <div class="row row-between panel-tight" style="background:var(--surface-2); border-radius:var(--r-sm); border:1px solid var(--border)">
        <div>
          <div class="small"><b>Need the standard CSV format?</b></div>
          <div class="tiny faint">Download our pre-formatted sample template with required headers.</div>
        </div>
        <a href="{{ url_for('issuer.sample_csv') }}" class="btn btn-ghost btn-sm">
          <span aria-hidden="true">📥</span> Download Sample CSV
        </a>
      </div>

      <div class="stack stack-2">
        <h4>CSV Column Requirements</h4>
        <div class="dl" style="font-size:0.85rem">
          <div class="dl-row">
            <span class="dl-key mono">roll_number</span>
            <span class="dl-val"><b>Required.</b> Student ID / Roll Number (e.g. <code>22103001</code>).</span>
          </div>
          <div class="dl-row">
            <span class="dl-key mono">doc_type</span>
            <span class="dl-val"><b>Required.</b> Type code: <code>DEGREE</code>, <code>MARKSHEET</code>, <code>TC</code>, <code>MIGRATION</code>, <code>BONAFIDE</code>, <code>INTERNSHIP</code>.</span>
          </div>
          <div class="dl-row">
            <span class="dl-key mono">title</span>
            <span class="dl-val"><b>Required.</b> Full credential title (e.g. <code>Bachelor of Technology in Computer Science</code>).</span>
          </div>
          <div class="dl-row">
            <span class="dl-key mono">student_name</span>
            <span class="dl-val"><b>Optional.</b> Student's full name for automated profile creation.</span>
          </div>
          <div class="dl-row">
            <span class="dl-key mono">validity_days</span>
            <span class="dl-val"><b>Optional.</b> Positive integer days (leave empty for permanent/default validity).</span>
          </div>
        </div>
      </div>

      <button type="submit" class="btn btn-primary btn-lg" style="margin-top:1rem">
        <span aria-hidden="true">🔒</span> Process &amp; Issue Batch
      </button>
    </form>
  </section>
</div>
{% endblock %}
```

---

## 3. Student Dashboard & Document Rendering Investigation

### 3.1 Document List View (`templates/student/dashboard.html`)
- **Card Rendering (Lines 138–227)**:
  - Cards render document metadata: `doc.type_icon`, `doc.type_label`, `doc.title`, `doc.status_label`, `doc.card_qr` (base64 data URI generated in `student_routes.py:dashboard`), `doc.issuer_name`, `doc.issued_on`, `doc.valid_until`, `doc.lifetime_percent`, and `doc.doc_hash`.
  - **No raw file access or thumbnail load** occurs on the dashboard card list.
  - Action buttons:
    - `View Details` -> `url_for('student.document_detail', doc_id=doc.id)`
    - `Download` -> `url_for('student.download_stamped', doc_id=doc.id)`
    - `Share QR` -> `url_for('student.document_detail', doc_id=doc.id) + '#share'`

### 3.2 Document Detail View (`templates/student/document_detail.html`)
- **Flip Card Front Face (Lines 64–112)**:
  ```html
  <div class="preview-plate" data-plate>
    {% if doc.is_previewable_image %}
      <img src="{{ url_for('student.document_preview', doc_id=doc.id) }}"
           alt="Preview of {{ doc.title }}" data-plate-image>
    {% elif doc.is_pdf %}
      <div class="preview-empty">
        <div class="big" aria-hidden="true">📄</div>
        <b>{{ doc.file_name }}</b>
        <p class="small muted" style="margin-top:.5rem">
          PDF original — download the stamped copy to view it.
        </p>
      </div>
    {% else %}
      <div class="preview-empty">
        <div class="big" aria-hidden="true">🗂️</div>
        <b>No file preview</b>
        <p class="small muted" style="margin-top:.5rem">
          This credential exists as ledger metadata only.
        </p>
      </div>
    {% endif %}

    {# The verification stamp presses in on top of the plate #}
    <div class="stamp {{ 'is-void' if doc.revoked else ('is-muted' if not doc.is_valid else '') }}" ...>
    ...
  ```
- **Properties in `models/document.py`**:
  - `doc.is_previewable_image` returns `bool(self.file_mime and self.file_mime.startswith('image/'))` -> Returns `False` when `file_mime` is `None`.
  - `doc.is_pdf` returns `self.file_mime == 'application/pdf'` -> Returns `False` when `file_mime` is `None`.
  - When both are `False`, it falls cleanly to the third branch (`No file preview: This credential exists as ledger metadata only`).
- **Original File Preview Route (`routes/student_routes.py:168-185`)**:
  - `/student/document/<doc_id>/preview` aborts with `404` if `not doc.file_data`. Since the template never references the `/preview` URL when `doc.is_previewable_image` is `False`, no 404 error is triggered.
- **Stamped PDF Download (`services/stamp_service.py:305-331`)**:
  - When `doc.file_data` is `None`, `generate_stamped_pdf` executes:
    1. Skips image stamping (`if doc.file_data and doc.is_previewable_image`).
    2. Builds the A4 verification certificate page: `pages.append(build_certificate_page(doc, student, verify_url))`.
    3. Saves `pages[0]` to PDF buffer and returns the generated PDF bytes.
  - Result: Student gets a valid, beautifully formatted verification certificate PDF containing student info, document metadata, blockchain anchor, digital seal, and scannable QR code!
- **Stamped Image Download (`services/stamp_service.py:333-347`)**:
  - `generate_stamped_image(doc)` returns `None` if `not (doc.file_data and doc.is_previewable_image)`.
  - In `templates/student/document_detail.html` (lines 195–200), the PNG download button is wrapped in `{% if doc.is_previewable_image %}` and is therefore not displayed for text-only credentials.

---

## 4. Public Verify Page Investigation

### 4.1 Verification Routing & Logic (`routes/public_routes.py`)
- Route `GET /v/<doc_hash>` executes `services.verification_service.verify_hash(doc_hash)`.
- Verification performs:
  1. Lookup `doc = Doc.query.filter_by(doc_hash=doc_hash).first()`.
  2. QR token expiry check (if token provided).
  3. Revocation check (`doc.revoked`).
  4. Cryptographic integrity check via `security.recompute_document_hash(doc)`:
     ```python
     def recompute_document_hash(doc) -> str:
         file_digest = doc.file_digest or 'no-file'
         material = f'{doc.hash_salt}|{file_digest}|{doc.payload or ""}'
         return hashlib.sha256(material.encode('utf-8')).hexdigest()
     ```
     When `file_bytes` is `None`, `issue_credential` computes the hash using `'no-file'`. Thus, `recompute_document_hash` produces the exact same hash. Integrity check succeeds with `RESULT_VALID`.
  5. Chain validation against the mined block in the ledger.

### 4.2 Display Template (`templates/public/verify_result.html`)
- Displays:
  - Verdict banner: Authentic / Expired / Revoked / Tampered / Not Found.
  - SHA-256 Hash and visual color swatches.
  - Credential details panel (Holder Name, Roll Number, Programme, Issued By, Issued On, Valid Until, Status, Times Verified).
  - Blockchain proof panel (Block #, Mined Timestamp, Proof of Work nonce, Block Hash, Previous Hash, Chain status).
- **Physical File Independence**:
  - The public verify page never attempts to render, preview, or download the original file. It relies entirely on metadata and cryptographic proofs.
  - **Verdict**: 100% crash-free and fully supported for text-only credentials.

---

## 5. Sample CSV Template Specification & Serving

### 5.1 Format & Headers
- **Filename**: `template.csv` / `sample_bulk_issue.csv`
- **MIME Type**: `text/csv`
- **Encoding**: UTF-8
- **Header Row**:
  ```csv
  roll_number,student_name,doc_type,title,validity_days
  ```
- **Sample Content**:
  ```csv
  roll_number,student_name,doc_type,title,validity_days
  22103001,Aarav Sharma,DEGREE,Bachelor of Technology in Computer Science,3650
  22103002,Diya Patel,MARKSHEET,Semester VIII Grade Report,3650
  22103003,Rohan Verma,BONAFIDE,Bonafide Certificate 2026,90
  22103004,Ananya Gupta,INTERNSHIP,Summer Research Internship,730
  22103005,Vikram Singh,TC,Transfer Certificate,180
  ```

### 5.2 Serving Location
1. **Dedicated Route**: Add `@issuer_bp.route('/sample-csv')` or `@issuer_bp.route('/template.csv')` in `routes/issuer_routes.py`:
   ```python
   @issuer_bp.route('/sample-csv')
   @issuer_required
   def sample_csv():
       csv_content = (
           "roll_number,student_name,doc_type,title,validity_days\r\n"
           "22103001,Aarav Sharma,DEGREE,Bachelor of Technology in Computer Science,3650\r\n"
           "22103002,Diya Patel,MARKSHEET,Semester VIII Grade Report,3650\r\n"
           "22103003,Rohan Verma,BONAFIDE,Bonafide Certificate 2026,90\r\n"
       )
       return Response(
           csv_content,
           mimetype="text/csv",
           headers={
               "Content-Disposition": "attachment; filename=template.csv",
               "Content-Type": "text/csv; charset=utf-8",
           },
       )
   ```
2. **Static Asset**: Place a pre-built `static/template.csv` file in the project's `static/` directory so it is directly downloadable as well.

---

## 6. Implementation Checklist & Verification Recommendations

| Component | Target File | Description |
|-----------|-------------|-------------|
| **Navigation** | `templates/base.html` | Add Bulk Issue link under `current_user.is_issuer` |
| **Issuer Dashboard** | `templates/issuer/dashboard.html` | Add "📁 Bulk Issue (CSV)" button in Hero section |
| **Bulk Issue Template** | `templates/issuer/bulk_issue.html` | Create new template with CSV file input, sample download link, column documentation, and error list display |
| **CSV Template Serving** | `routes/issuer_routes.py` & `static/template.csv` | Implement `/issuer/sample-csv` endpoint and static sample file |
| **Issuer Route** | `routes/issuer_routes.py` | Add `GET/POST /issuer/bulk-issue` handler with validation, transaction rollback on failure, and batch issuance |
