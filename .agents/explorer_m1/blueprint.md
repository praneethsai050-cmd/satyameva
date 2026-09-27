# Milestone 1 Implementation Blueprint: Backend Bulk Issuance, CSV Validation, UI & Sample Template

## Executive Summary
This blueprint specifies the exact architecture, data flows, route additions, CSV parsing and validation algorithms, UI templates, navigation hooks, and edge-case handling for **Milestone 1 (Bulk Issuance Engine & Issuer Interface)** of the Satyameva credentialing system.

---

## 1. Architectural Overview & Component Seams

```
               ┌────────────────────────────────────────────────────────┐
               │                  Issuer Web Interface                  │
               │   - /issuer/bulk-issue (GET/POST)                      │
               │   - /issuer/sample-csv & /issuer/template.csv (GET)    │
               └───────────────┬───────────────────────┬────────────────┘
                               │ (Upload .csv)         │ (Download template.csv)
                               ▼                       ▼
               ┌────────────────────────────────┐ ┌──────────────────────┐
               │    _parse_and_validate_csv     │ │ static/template.csv  │
               │  - UTF-8 BOM stripping         │ └──────────────────────┘
               │  - Header normalization        │
               │  - All-or-Nothing row checks   │
               └───────────────┬────────────────┘
                               │ Passes (0 errors)
                               ▼
               ┌────────────────────────────────────────────────────────┐
               │                 Atomic Issuance Loop                   │
               │  For each row in batch:                                │
               │   1. _get_or_create_student (auto-provision)           │
               │   2. issue_credential(file_bytes=None, ...)            │
               │      ├── SHA-256 ('no-file' hash + salt + canonical)   │
               │      ├── Insert Doc record                             │
               │      ├── mine_block() (Proof of Work)                  │
               │      └── trigger email notifications                   │
               └────────────────────────────────────────────────────────┘
```

---

## 2. File Modification Specifications

### 2.1. `routes/issuer_routes.py`

#### A. Required Imports
Update top-level imports in `routes/issuer_routes.py`:
```python
import csv
import io
import os
from flask import (
    Blueprint, abort, current_app, flash, redirect, render_template, request,
    send_from_directory, url_for,
)
from flask_login import current_user
from werkzeug.utils import secure_filename

from decorators import issuer_required
from extensions import db
from models.document import DOC_TYPES, STATUS_EXPIRED, Doc, default_validity_days
from models.student import Student
from models.user import ROLE_STUDENT, User
from security import hash_password
from services.credential_service import issue_credential
```

#### B. Helper Function: `_get_or_create_student`
Extract and standardize student lookup and auto-provisioning logic:
```python
def _get_or_create_student(roll_number: str, student_name: str | None = None, institution: str | None = None) -> Student:
    """
    Look up an existing student by roll number, or auto-provision a new User and
    Student profile if one does not exist yet.
    """
    clean_roll = (roll_number or '').strip()
    student = Student.query.filter_by(roll_number=clean_roll).first()
    if student is not None:
        return student

    inst_name = institution or current_user.organization or 'Satyameva Institute'
    s_name = (student_name or '').strip() or f"Student {clean_roll}"
    username = f"student.{clean_roll}".lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
    inst_slug = (inst_name).lower().replace(' ', '_').replace('/', '_')
    email = f"{clean_roll.lower().replace('/', '_')}@{inst_slug}.edu"

    user = User.query.filter((User.username == username) | (User.email == email)).first()
    if not user:
        salt, digest, iters = hash_password('satyameva123')
        user = User(
            username=username,
            email=email,
            role=ROLE_STUDENT,
            organization=inst_name,
            password_salt=salt,
            password_hash=digest,
            password_iterations=iters,
        )
        db.session.add(user)
        db.session.flush()

    student = Student(
        user_id=user.id,
        full_name=s_name,
        roll_number=clean_roll,
        institution=inst_name,
    )
    db.session.add(student)
    db.session.flush()
    return student
```

#### C. Helper Function: `_parse_and_validate_csv`
Pure validation helper implementing synchronous all-or-nothing validation:
```python
def _parse_and_validate_csv(file_storage) -> tuple[list[dict], list[str]]:
    """
    Synchronously parse and validate an uploaded CSV file.
    
    Returns:
        (rows, errors):
        - If valid: (list_of_row_dicts, [])
        - If invalid: ([], list_of_error_strings)
    """
    errors: list[str] = []
    if not file_storage or not file_storage.filename:
        return [], ["No file selected. Please choose a CSV file to upload."]

    if not file_storage.filename.lower().endswith('.csv'):
        return [], ["Invalid file extension. Only .csv files are supported."]

    raw_bytes = file_storage.read()
    if not raw_bytes or not raw_bytes.strip():
        return [], ["The uploaded CSV file is empty."]

    try:
        # utf-8-sig automatically removes the UTF-8 Byte Order Mark (BOM) if present
        text = raw_bytes.decode('utf-8-sig')
    except UnicodeDecodeError:
        try:
            text = raw_bytes.decode('latin-1')
        except Exception:
            return [], ["Unable to decode CSV file. Please ensure it is saved as UTF-8."]

    stream = io.StringIO(text, newline=None)
    reader = csv.reader(stream)

    # 1. Locate and validate header row
    header_row = None
    header_line_num = 0
    for line_idx, row in enumerate(reader, start=1):
        if any(cell.strip() for cell in row):
            header_row = [c.strip().lower() for c in row if c is not None]
            header_line_num = line_idx
            break

    if not header_row:
        return [], ["The CSV file does not contain a valid header row."]

    required_headers = {'roll_number', 'doc_type', 'title'}
    header_set = set(header_row)
    missing_headers = required_headers - header_set
    if missing_headers:
        missing_list = ', '.join(sorted(missing_headers))
        return [], [f"Missing required CSV column(s): {missing_list}. Required columns are: roll_number, doc_type, title."]

    # Header column indices
    col_idx = {h: idx for idx, h in enumerate(header_row)}

    # 2. Parse and validate data rows
    parsed_rows: list[dict] = []
    data_row_count = 0

    for line_idx, row in enumerate(reader, start=header_line_num + 1):
        # Skip completely empty rows
        if not row or not any(cell.strip() for cell in row):
            continue

        data_row_count += 1
        row_dict: dict[str, str] = {}
        for h, idx in col_idx.items():
            row_dict[h] = row[idx].strip() if idx < len(row) else ''

        roll_number = row_dict.get('roll_number', '').strip()
        doc_type = row_dict.get('doc_type', '').strip().upper()
        title = row_dict.get('title', '').strip()
        student_name = row_dict.get('student_name', '').strip()
        validity_days_str = row_dict.get('validity_days', '').strip()

        row_label = f"Row {data_row_count} (Line {line_idx})"

        # Validate roll_number
        if not roll_number:
            errors.append(f"{row_label}: 'roll_number' is required.")

        # Validate doc_type
        if not doc_type:
            errors.append(f"{row_label}: 'doc_type' is required.")
        elif doc_type not in DOC_TYPES:
            allowed = ', '.join(sorted(DOC_TYPES.keys()))
            errors.append(f"{row_label}: Invalid doc_type '{row_dict.get('doc_type')}'. Allowed types: {allowed}.")

        # Validate title
        if not title:
            errors.append(f"{row_label}: 'title' is required.")

        # Validate validity_days (optional, but must be positive integer if given)
        if validity_days_str:
            if not validity_days_str.isdigit() or int(validity_days_str) <= 0:
                errors.append(f"{row_label}: 'validity_days' must be a positive whole number of days, got '{validity_days_str}'.")

        parsed_rows.append({
            'roll_number': roll_number,
            'doc_type': doc_type,
            'title': title,
            'student_name': student_name,
            'validity_days': int(validity_days_str) if (validity_days_str and validity_days_str.isdigit()) else None,
            'line_number': line_idx,
            'row_index': data_row_count,
        })

    if data_row_count == 0:
        return [], ["The CSV file contains a header but no data rows."]

    if errors:
        return [], errors

    return parsed_rows, []
```

#### D. Routes: `/issuer/bulk-issue`, `/issuer/sample-csv`, `/issuer/template.csv`
```python
@issuer_bp.route('/bulk-issue', methods=['GET', 'POST'])
@issuer_required
def bulk_issue():
    """
    Bulk credential issuance from CSV file upload.
    Synchronously validates all rows (all-or-nothing) and atomically issues text-only credentials.
    """
    if request.method == 'GET':
        return render_template('issuer/bulk_issue.html', errors=[])

    # Support 'csv_file', 'file', or 'document' field names
    upload = request.files.get('csv_file') or request.files.get('file') or request.files.get('document')
    
    parsed_rows, validation_errors = _parse_and_validate_csv(upload)

    if validation_errors:
        for err in validation_errors[:3]:  # Flash top few errors for quick toast feedback
            flash(err, 'danger')
        return render_template('issuer/bulk_issue.html', errors=validation_errors), 400

    # All-or-nothing validation passed. Execute issuance loop.
    issued_count = 0
    try:
        for row in parsed_rows:
            student = _get_or_create_student(
                roll_number=row['roll_number'],
                student_name=row['student_name'] or None,
                institution=current_user.organization,
            )

            doc_title = row['title'] or DOC_TYPES.get(row['doc_type'], ('Credential', '📄', 365))[0]

            issue_credential(
                student=student,
                issuer=current_user,
                doc_type=row['doc_type'],
                title=doc_title,
                file_bytes=None,
                file_name=None,
                file_mime=None,
                validity_days=row['validity_days'],
            )
            issued_count += 1

        flash(f"Successfully issued {issued_count} credentials in bulk.", "success")
        return redirect(url_for('issuer.dashboard'))

    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Bulk issuance failed during execution loop.")
        flash(f"An unexpected error occurred during batch issuance: {str(exc)}", "danger")
        return render_template('issuer/bulk_issue.html', errors=[f"System error: {str(exc)}"]), 500


@issuer_bp.route('/sample-csv')
@issuer_bp.route('/template.csv')
def sample_csv():
    """
    Serve the sample CSV template for bulk issuance download.
    """
    static_folder = current_app.static_folder or os.path.join(current_app.root_path, 'static')
    return send_from_directory(
        static_folder,
        'template.csv',
        as_attachment=True,
        mimetype='text/csv',
        download_name='template.csv',
    )
```

---

### 2.2. Static Template File: `static/template.csv`

Create `static/template.csv` with standard headers and representative sample records:
```csv
roll_number,student_name,doc_type,title,validity_days
22103045,Aarav Sharma,DEGREE,Bachelor of Technology in Computer Science,3650
22103046,Diya Patel,MARKSHEET,Semester 6 Grade Sheet,3650
22103047,Rohan Verma,BONAFIDE,Bonafide Student Certificate,90
22103048,Ananya Iyer,INTERNSHIP,Summer Research Internship Certificate,730
22103049,Kabir Mehta,TC,Transfer Certificate,180
```

---

### 2.3. Template File: `templates/issuer/bulk_issue.html`

Create `templates/issuer/bulk_issue.html` conforming to Satyameva theme styles, responsive layout, and detailed user feedback:

```html
{% extends 'base.html' %}
{% block title %}Bulk Issue Credentials{% endblock %}

{% block content %}
<div class="stack stack-8">
  <div class="row row-between">
    <div class="stack">
      <span class="hero-kicker">🏛️ Issuer Portal</span>
      <h1>Bulk Issue Credentials</h1>
      <p class="muted">Upload a CSV file to issue and blockchain-anchor multiple credentials in a single batch.</p>
    </div>
    <a href="{{ url_for('issuer.dashboard') }}" class="btn btn-ghost">← Back to Dashboard</a>
  </div>

  {% if errors %}
    <div class="alert alert-danger" role="alert">
      <span class="alert-icon" aria-hidden="true">🚫</span>
      <div style="flex:1">
        <div class="alert-title">Batch Validation Failed ({{ errors|length }} error{{ 's' if errors|length > 1 else '' }})</div>
        <div class="alert-body" style="margin-top:0.5rem">
          <p style="margin:0 0 0.5rem">No credentials were issued. Please fix the following issues in your CSV and re-upload:</p>
          <ul style="margin:0; padding-left:1.2rem; max-height:220px; overflow-y:auto">
            {% for err in errors %}
              <li><b>{{ err }}</b></li>
            {% endfor %}
          </ul>
        </div>
      </div>
    </div>
  {% endif %}

  <div class="grid" style="grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr); gap: 1.5rem; align-items: start;" id="bulk-issue-grid">
    
    <!-- Left Column: Upload Form -->
    <section class="panel stack stack-4">
      <div class="panel-title">📤 Upload CSV Batch</div>
      
      <form method="post" action="{{ url_for('issuer.bulk_issue') }}" enctype="multipart/form-data" class="stack stack-4" novalidate>
        <div class="stack stack-2">
          <label class="field-label" for="csv_file">Select CSV File <span style="color:var(--red,#e53935)">*</span></label>
          <input type="file" id="csv_file" name="csv_file" class="input" required accept=".csv" style="padding:0.75rem">
          <span class="tiny faint">Only <code>.csv</code> files encoded in UTF-8 are supported.</span>
        </div>

        <div class="row row-between panel-tight" style="background:var(--wash,#f6f7fd); border-radius:8px; border:1px solid var(--border,#dde2f0)">
          <div class="stack" style="gap:0.2rem">
            <b class="small">Need a starting template?</b>
            <span class="tiny muted">Download the formatted sample CSV with required columns.</span>
          </div>
          <a class="btn btn-ghost btn-sm" href="{{ url_for('issuer.sample_csv') }}" download="template.csv">
            <span aria-hidden="true">📥</span> Download Sample CSV
          </a>
        </div>

        <button type="submit" class="btn btn-primary btn-lg" style="margin-top:0.5rem">
          <span aria-hidden="true">⚡</span> Validate &amp; Issue Batch
        </button>
      </form>
    </section>

    <!-- Right Column: Format Guidelines & Column Reference -->
    <aside class="stack stack-4">
      <section class="panel stack stack-3">
        <div class="panel-title">📋 CSV Format Specification</div>
        
        <p class="small muted" style="margin:0">
          The CSV must include the following column headers in the first non-empty row:
        </p>

        <div class="table-wrap">
          <table class="table" style="font-size:0.82rem; width:100%">
            <thead>
              <tr>
                <th>Column</th>
                <th>Required</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>roll_number</code></td>
                <td><span class="badge badge-error" style="font-size:0.68rem">Required</span></td>
                <td>Unique Student ID (e.g., <code>22103045</code>)</td>
              </tr>
              <tr>
                <td><code>doc_type</code></td>
                <td><span class="badge badge-error" style="font-size:0.68rem">Required</span></td>
                <td>Credential type code (e.g., <code>DEGREE</code>)</td>
              </tr>
              <tr>
                <td><code>title</code></td>
                <td><span class="badge badge-error" style="font-size:0.68rem">Required</span></td>
                <td>Document title (e.g., <code>B.Tech CSE</code>)</td>
              </tr>
              <tr>
                <td><code>student_name</code></td>
                <td><span class="badge badge-neutral" style="font-size:0.68rem">Optional</span></td>
                <td>Full name if student is not registered</td>
              </tr>
              <tr>
                <td><code>validity_days</code></td>
                <td><span class="badge badge-neutral" style="font-size:0.68rem">Optional</span></td>
                <td>Days valid (blank = default)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="stack stack-2" style="margin-top:0.5rem">
          <div class="tiny upper faint">Supported Document Types</div>
          <div class="row" style="gap:0.35rem; flex-wrap:wrap">
            {% for code, meta in doc_types.items() %}
              <span class="badge badge-neutral" style="font-size:0.75rem" title="{{ meta[0] }}">
                {{ meta[1] }} <code>{{ code }}</code>
              </span>
            {% endfor %}
          </div>
        </div>

        <div class="alert alert-info" style="padding:0.65rem 0.85rem; font-size:0.78rem; margin:0">
          <span>ℹ️ <b>All-or-Nothing Rule:</b> If any row fails validation, 0 credentials are created and 0 blocks are mined.</span>
        </div>
      </aside>
    </div>
  </div>
</div>
{% endblock %}

{% block head %}
<style>
  @media (max-width: 960px) {
    #bulk-issue-grid { grid-template-columns: 1fr !important; }
  }
</style>
{% endblock %}
```

---

### 2.4. Navigation Updates

#### A. `templates/base.html`
In `templates/base.html` around line 59:
```html
        {% elif current_user.is_authenticated and current_user.is_issuer %}
          <a class="nav-link {{ 'is-active' if request.endpoint == 'issuer.dashboard' }}"
             href="{{ url_for('issuer.dashboard') }}">Dashboard</a>
          <a class="nav-link {{ 'is-active' if request.endpoint == 'issuer.issue' }}"
             href="{{ url_for('issuer.issue') }}">Issue Document</a>
          <a class="nav-link {{ 'is-active' if request.endpoint == 'issuer.bulk_issue' }}"
             href="{{ url_for('issuer.bulk_issue') }}">Bulk Issue</a>
```

#### B. `templates/issuer/dashboard.html`
In `templates/issuer/dashboard.html`:
1. Hero action buttons (lines 20-28):
```html
      <div class="row" style="gap:.75rem">
        <a class="btn btn-primary" href="{{ url_for('issuer.issue') }}">
          <span aria-hidden="true">＋</span> Issue Single Document
        </a>
        <a class="btn btn-ghost" href="{{ url_for('issuer.bulk_issue') }}">
          <span aria-hidden="true">📑</span> Bulk Issue (CSV)
        </a>
        <span class="chain-status">
          <span aria-hidden="true">🔗</span>
          <span class="mono">{{ stats.total }}</span> issued
        </span>
      </div>
```
2. Empty state actions (lines 218-222):
```html
          <div class="row center" style="gap: .75rem; justify-content: center;">
            <a class="btn btn-primary" href="{{ url_for('issuer.issue') }}">
              <span aria-hidden="true">＋</span> Issue Single Document
            </a>
            <a class="btn btn-ghost" href="{{ url_for('issuer.bulk_issue') }}">
              <span aria-hidden="true">📑</span> Bulk Issue (CSV)
            </a>
          </div>
```

---

## 3. Edge Cases & Safeguards Analysis

| Edge Case | Failure Mode / Risk | Solution / Implementation |
|---|---|---|
| **UTF-8 BOM (`\xef\xbb\xbf`)** | Excel on Windows prefixes BOM; `roll_number` decoded as `\ufeffroll_number`, causing missing header errors. | Use `raw_bytes.decode('utf-8-sig')` which strips BOM seamlessly. |
| **Header Whitespace & Casing** | User types ` Roll_Number `, `DOC_TYPE`, or trailing spaces. | Normalize with `[h.strip().lower() for h in row]` before key indexing. |
| **Row Field Whitespace** | Cell values have spaces e.g. `' DEGREE '` or `'22103045 '`. | Apply `.strip()` to all cell values and `.upper()` to `doc_type`. |
| **Trailing Blank Lines** | CSV exported from spreadsheet tools often has trailing empty lines `, , ,`. | Skip rows where `not any(cell.strip() for cell in row)`. |
| **Invalid `doc_type`** | Unknown doc type code passed (e.g. `'CERT'`). | Checked against `DOC_TYPES.keys()`; detailed error citing all valid options. |
| **Invalid `validity_days`** | Non-digit, negative, or zero validity days given (e.g. `'-5'`, `'abc'`). | Validated as positive integer (`isdigit() and int(val) > 0`); blank defaults to `None`. |
| **Missing Student Profile** | Roll number does not exist in DB yet. | Auto-provisions `User` and `Student` profile (username `student.<roll>`, password `satyameva123`). |
| **Partial Batch Failure Risk** | Any row invalid in batch. | Synchronous pre-validation pass; if even 1 error found, abort immediately, 0 DB inserts, 0 blocks mined. |
| **Runtime Exceptions in Loop** | Unexpected DB error mid-loop. | Wrapped in `try...except` with `db.session.rollback()` and error flash. |
| **Text-Only Credential Safety** | `file_bytes=None` credentials viewed on student dashboard or public verifier. | Verified: `security.create_document_hash` defaults to `'no-file'`; `stamp_service.generate_stamped_pdf` creates standalone certificate page; detail templates render metadata preview without crashing. |

---

## 4. Verification & Testing Strategy

### 4.1. Unit & Integration Verification Checklist
1. **Sample CSV Route (`/issuer/sample-csv` & `/issuer/template.csv`)**:
   - `GET /issuer/sample-csv` returns HTTP 200, Content-Type `text/csv` (or attachment).
   - Content contains required headers: `roll_number,student_name,doc_type,title,validity_days`.
2. **Missing Columns Validation**:
   - Upload CSV lacking `doc_type` or `title` header.
   - Assert HTTP 400 or error flash.
   - Assert `Doc.query.count()` unchanged, blockchain length unchanged.
3. **Invalid Row Data Validation**:
   - Upload CSV with 3 rows where Row 2 has `doc_type = INVALID_TYPE`.
   - Assert HTTP 400, error message mentions `Row 2: Invalid doc_type 'INVALID_TYPE'`.
   - Assert 0 documents created, 0 blocks mined.
4. **Valid Batch Execution**:
   - Upload valid 3-row CSV with valid headers and data.
   - Assert HTTP 302 redirect to `/issuer/dashboard`.
   - Assert exactly 3 new `Doc` records created and 3 new blocks mined on the blockchain.
   - Assert student accounts auto-provisioned.
5. **Text-Only Credential Verification**:
   - Verify student can view detail page `/student/document/<id>` without error.
   - Verify student can download stamped certificate PDF `/student/document/<id>/download`.
   - Verify public verification `/v/<hash>` renders authentic status.

---
