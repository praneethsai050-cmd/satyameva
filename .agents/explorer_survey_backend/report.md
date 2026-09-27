# Satyameva Credentialing Backend Architecture & Investigation Report

## Executive Summary
This report presents a comprehensive investigation of the **Satyameva** credentialing backend codebase. It details the architecture, models, issuance pipeline, blockchain anchoring, notification engine, authentication/authorization mechanisms, and a technical feasibility analysis for implementing **Bulk Issuance** (Requirements R1, R2, and R3).

---

## 1. Project Framework, Structure & Entry Points

### 1.1 Technology Stack & Dependencies
- **Core Framework**: Flask (Python)
- **Database ORM**: Flask-SQLAlchemy (with SQLite persistence at `instance/satyameva.db`)
- **Authentication**: Flask-Login (session-based with sliding 5-minute inactivity timeout)
- **Mailing**: Flask-Mail (SMTP notification subsystem)
- **Cryptography & Hashing**: Standard library `hashlib`, `hmac`, `secrets`/`os.urandom`
- **Graphics/Stamping**: Pillow (`PIL.Image`, `PIL.ImageDraw`, `PIL.ImageFont`) and `qrcode`

### 1.2 Entry Points
- `run.py`: Minimal application runner invoking `create_app().run(debug=True)`.
- `app.py`: Application factory function `create_app(config_name)`.
  - Initializes database (`db`), login manager (`login_manager`), and mail (`mail`).
  - Ensures `instance/` folder exists and genesis block exists on first startup via `blockchain.ensure_genesis_block()`.
  - Registers blueprints, sliding session idle timeout (`_register_session_timeout`), template filters/context processors (`_register_template_helpers`), and error handlers (`_register_error_handlers`).
  - Root route `/`: Redirects authenticated users to `current_user.home_endpoint()` and unauthenticated users to `/login`.

### 1.3 Blueprints & Route Definitions
The application is organized into 5 modular Flask blueprints:

| Blueprint | Module Path | URL Prefix | Description | Primary Endpoints |
|---|---|---|---|---|
| `auth_bp` | `routes/auth_routes.py` | None (`/`) | Authentication & Account Registration | `GET/POST /login`, `GET/POST /register`, `GET /logout` |
| `public_bp` | `routes/public_routes.py` | None (`/`) | Public Verification (No auth required) | `GET/POST /verify`, `GET /v/<doc_hash>` |
| `student_bp` | `routes/student_routes.py` | `/student` | Student Portal (Student role) | `GET /dashboard`, `GET /document/<id>`, `GET /document/<id>/preview`, `GET /document/<id>/download`, `GET /document/<id>/download/image`, `GET /document/<id>/qr.png`, `GET /document/<id>/qr.json`, `GET /document/<id>/history`, `GET /history`, `GET /notifications`, `POST /notifications/mark-all-read`, `GET /chain/validate` |
| `issuer_bp` | `routes/issuer_routes.py` | `/issuer` | Issuer Portal (Issuer role) | `GET /` (dashboard), `GET/POST /issue`, `POST /revoke/<doc_id>` |
| `verifier_bp` | `routes/verifier_routes.py` | `/verifier` | Authenticated Verifier Portal (Verifier role) | `GET/POST /dashboard`, `GET /v/<doc_hash>`, `GET /history`, `POST /report-fraud` |

---

## 2. Document Issuance Pipeline

### 2.1 Database Models & Schema
The database models are defined in `models/`:

#### A. `Doc` (`models/document.py`, table: `doc`)
Represents an individual academic credential.
- `id` (Integer, PK)
- `student_id` (Integer, FK -> `student.id`, indexed, non-null)
- `issuer_id` (Integer, FK -> `user.id`, nullable)
- `doc_type` (String(30), non-null, default='DEGREE'): Validated against `DOC_TYPES` (`DEGREE`, `MARKSHEET`, `TC`, `MIGRATION`, `BONAFIDE`, `INTERNSHIP`).
- `title` (String(160), non-null): Human-readable name of document.
- `issuer_name` (String(150), nullable): Denormalized organization/issuer display name.
- `doc_hash` (String(64), unique, indexed, non-null): SHA-256 integrity hash.
- `hash_salt` (String(64), non-null): 32-byte hex salt preventing rainbow table precomputation.
- `file_digest` (String(64), nullable): SHA-256 of the raw file binary (or `None` for text-only/data credentials).
- `payload` (Text, nullable): Canonical JSON string of credential metadata.
- `file_data` (LargeBinary, nullable): Raw document bytes (PDF or image).
- `file_name` (String(255), nullable): Uploaded file name.
- `file_mime` (String(100), nullable): MIME type (e.g., `image/png`, `application/pdf`).
- `issued_on` (DateTime, non-null, default=`utcnow`): Naive UTC issue date.
- `valid_until` (DateTime, nullable): Naive UTC expiration date (`NULL` means never expires).
- `is_stamped` (Boolean, non-null, default=False): Flag indicating if stamped verification was generated.
- `stamp_date` (DateTime, nullable) & `stamped_by` (Integer, nullable).
- `block_index` (Integer, nullable): Mined blockchain block index.
- `tx_hash` (String(80), nullable): Hex transaction ID (`0x...`).
- `verification_count` (Integer, non-null, default=0), `last_verified_at` (DateTime, nullable).
- `revoked` (Boolean, non-null, default=False), `revoked_reason` (String(255), nullable).

#### B. `Student` (`models/student.py`, table: `student`)
- `id` (Integer, PK)
- `user_id` (Integer, FK -> `user.id`, unique, non-null)
- `full_name` (String(120), non-null)
- `roll_number` (String(50), unique, indexed, non-null)
- `department` (String(120), nullable)
- `program` (String(120), nullable)
- `batch` (String(20), nullable)
- `institution` (String(150), nullable)
- `created_at` (DateTime, default=`utcnow`)
- Relationships: `user` (backref), `documents` (relationship to `Doc`, ordered by `issued_on.desc()`).

#### C. `User` (`models/user.py`, table: `user`)
- `id` (Integer, PK)
- `username` (String(80), unique, indexed, non-null)
- `email` (String(120), unique, indexed, non-null)
- `password_hash` (String(128)), `password_salt` (String(64)), `password_iterations` (Integer)
- `role` (String(20), non-null, default='student'): One of `student`, `issuer`, `verifier`, `admin`.
- `organization` (String(150), nullable)
- `created_at`, `last_login_at`
- Relationships: `student` (uselist=False).

### 2.2 Current Single Issuance Flow
1. **Form Processing** (`routes/issuer_routes.py` -> `issue()`):
   - Extracts `roll_number`, `student_name`, `doc_type`, `title`, `validity_days`.
   - Validates fields via `_validate_issue(form)`.
   - **Student Lookup / Auto-Provisioning**:
     - Looks up `Student.query.filter_by(roll_number=clean_roll).first()`.
     - If not found, automatically provisions a placeholder `User` (username: `student.<roll>`, email: `<roll>@<org>.edu`, default password `satyameva123`) and a corresponding `Student` record.
   - Reads file upload (`request.files.get('document')`), checks allowed extensions (`png`, `jpg`, `jpeg`, `pdf`, `webp`).
2. **Minting Service** (`services/credential_service.py` -> `issue_credential()`):
   - Generates salt: `generate_salt(16)`.
   - Constructs metadata dictionary:
     ```python
     metadata = {
         'student_name': student.full_name,
         'roll_number': student.roll_number,
         'program': student.program,
         'department': student.department,
         'institution': student.institution,
         'doc_type': doc_type,
         'title': title,
         'issuer': getattr(issuer, 'organization', None) or getattr(issuer, 'username', None),
         'issued_on': issued_on.isoformat(),
     }
     ```
   - Canonicalizes JSON: `payload = canonical_payload(metadata)` (sorted keys, compact separators).
   - Computes `file_digest = hashlib.sha256(file_bytes).hexdigest() if file_bytes else None`.
   - Computes `doc_hash = create_document_hash(file_bytes, metadata, salt)`:
     - Formats material as `f'{salt}|{file_digest or "no-file"}|{canonical_payload(metadata)}'`.
     - Returns SHA-256 digest.
   - Creates `Doc` instance, flushes DB to assign `doc.id`.
   - Calls `mine_block(...)` on blockchain.
   - Sets `doc.block_index = block.index`, commits DB.
   - Dispatches fire-and-forget email notifications to student and issuer.

---

## 3. Blockchain Anchoring Subsystem

### 3.1 Model & Persistence
- Table: `block` (`models/block.py`) with columns `index`, `timestamp`, `data` (canonical JSON), `proof` (integer nonce), `previous_hash`, `hash`, `doc_hash`.
- Dual Storage Architecture (`blockchain.py`):
  - Primary store: SQLite `block` table.
  - Secondary mirror: `instance/blockchain.json`. Synchronized after every block creation and genesis block generation.
  - Genesis block (#0): Generated via `ensure_genesis_block()` with `previous_hash = '0'*64`, `proof = 1`, `data = canonical_payload({'genesis': True, 'chain': 'satyameva'})`.

### 3.2 Proof of Work & Mining Logic
- Mining function: `Blockchain.mine_block(payload, doc_hash=None, difficulty=4)`:
  - Fetches last block from database (`get_last_block()`).
  - Next index = `previous.index + 1`.
  - PoW Algorithm:
    ```python
    def proof_of_work(self, previous_proof: int, index: int, difficulty: int | None = None) -> int:
        target = '0' * (difficulty or self.difficulty)
        proof = 1
        while True:
            guess = hashlib.sha256(f'{previous_proof}{proof}{index}'.encode('utf-8')).hexdigest()
            if guess.startswith(target):
                return proof
            proof += 1
    ```
  - Block Hash computation:
    `sha256(f'{index}|{timestamp.isoformat()}|{canonical_payload(data)}|{proof}|{previous_hash}')`
  - Persists new block in SQLite and writes updated chain array to `instance/blockchain.json`.

### 3.3 Chain Integrity Validation
- `validate_chain()`: Walks the chain from block 0 to tip, recomputing block hashes and validating parent linkages (`block[i].previous_hash == block[i-1].hash`).

---

## 4. Email Notification Subsystem

### 4.1 Implementation & Configuration
- Handled in `services/email_service.py` using `Flask-Mail`.
- Configured in `config.py` with SMTP parameters (`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`, `MAIL_SUPPRESS_SEND`).
- **Resilience**: All email dispatches are wrapped in `try...except` and logged on failure; SMTP connection timeouts or authentication failures never abort or roll back database transactions or credential issuance.

### 4.2 Notifications Triggered on Issuance
1. `send_credential_issued_student(doc, student)`:
   - Recipient: `student.user.email`.
   - Templates: `templates/email/credential_issued_student.html` & `.txt`.
   - Context: `student`, `doc`, `dashboard_url`, `brand`.
2. `send_credential_issued_issuer(doc, student, issuer)`:
   - Recipient: `issuer.email`.
   - Templates: `templates/email/credential_issued_issuer.html` & `.txt`.
   - Context: `student`, `doc`, `issuer`, `issuer_dashboard_url`, `brand`.

---

## 5. Authentication, Sessions & Issuer Authorization

### 5.1 RBAC & Role Verification
- Defined in `decorators.py`:
  - `role_required(*roles)`: Checks `current_user.is_authenticated` (redirects to login if unauthenticated) and `current_user.role in roles` (aborts with 403 Forbidden if wrong role).
  - `issuer_required = role_required('issuer', 'admin')`.
- All routes under `/issuer` (`dashboard`, `issue`, `revoke`) are protected by `@issuer_required`.
- Issuer identity in views is accessed via `current_user` (`current_user.id`, `current_user.organization`, `current_user.display_name`).

### 5.2 Session Inactivity Security
- Sliding 5-minute idle timeout registered via `@app.before_request` in `app.py`.
- Refreshes `session['last_active'] = time.time()` on every authenticated request.
- Logs out user and clears session if `now - session['last_active'] > SESSION_TIMEOUT_SECONDS` (300 seconds).

---

## 6. Analysis of Requirements R2 & R3 for Bulk Issuance

### 6.1 Requirement R2: All-or-Nothing CSV Parsing & Validation
- **Input Constraints**:
  - File must be `.csv` (MIME/extension validation).
  - Max size governed by `MAX_CONTENT_LENGTH` (16 MB).
- **Required Columns**:
  - `roll_number`: Student identifier string (e.g. "22103045"). Must be non-empty.
  - `doc_type`: Credential type code. Must be valid key in `DOC_TYPES` (`DEGREE`, `MARKSHEET`, `TC`, `MIGRATION`, `BONAFIDE`, `INTERNSHIP`).
  - `title`: Credential title. Must be non-empty string.
- **Optional Columns**:
  - `student_name`: Name for student profile creation if student doesn't exist yet.
  - `validity_days`: Positive integer if provided; if empty or absent, defaults to `default_validity_days(doc_type)`.
- **All-or-Nothing Invariant**:
  - The entire CSV file must be read into memory and parsed row-by-row before any database writes or block mining occur.
  - If header row is missing any required column (`roll_number`, `doc_type`, `title`), immediate failure.
  - If any row is missing a required field, has an unknown `doc_type`, or has an invalid `validity_days`, the entire batch is rejected:
    - **0 `Doc` records created.**
    - **0 `Block` records mined.**
    - Detailed, user-friendly error message is displayed (specifying the row number and the exact issue).
  - Only when 100% of rows pass validation does execution proceed to iteration and issuance.

### 6.2 Requirement R3: Text-Only Credential Issuance
- **Data Credential Semantics**:
  - In `issue_credential(student, issuer, doc_type, title, file_bytes=None, file_name=None, file_mime=None, validity_days=...)`:
    - `file_bytes` is `None`.
    - `file_digest` is `None` in the database.
    - `doc_hash` is computed as `create_document_hash(None, metadata, salt)` which replaces missing file digest with `'no-file'`.
    - `recompute_document_hash(doc)` checks `doc.file_digest or 'no-file'`, which re-derives the identical hash for verification.
  - **Blockchain Anchoring**:
    - Each row in the batch triggers `mine_block()`, creating an unbroken series of blocks.
    - For 3 rows in a valid batch, exactly 3 `Doc` rows and 3 new `Block` records are created.
  - **Email Notification**:
    - `issue_credential()` will fire `send_credential_issued_student` and `send_credential_issued_issuer` for each issued row.
  - **Student Auto-Provisioning**:
    - If a student with the `roll_number` does not exist, provision user + student record identically to single issuance.

### 6.3 Front-end & Rendering Safety for Text-Only Credentials
Our survey examined all views and templates to ensure text-only credentials without physical files will not cause exceptions or crashes:
1. **Student Dashboard (`templates/student/dashboard.html`)**:
   - Renders QR code on card using `qr_data_uri(...)` without touching file data.
   - Shows metadata, status badge, validity bar, and short hash.
2. **Document Detail (`templates/student/document_detail.html`)**:
   - Contains fallback branch in lines 81-88:
     ```html
     {% else %}
       <div class="preview-empty">
         <div class="big" aria-hidden="true">🗂️</div>
         <b>No file preview</b>
         <p class="small muted" style="margin-top:.5rem">
           This credential exists as ledger metadata only.
         </p>
       </div>
     {% endif %}
     ```
   - PNG download button is guarded by `{% if doc.is_previewable_image %}`.
3. **Stamped PDF Generation (`services/stamp_service.py` -> `generate_stamped_pdf`)**:
   - Checks `if doc.file_data and doc.is_previewable_image:`.
   - When `doc.file_data` is `None`, it generates the standalone `build_certificate_page` as Page 1. Stamped PDF download succeeds flawlessly!
4. **Public Verification (`templates/public/verify_result.html` & `services/verification_service.py`)**:
   - Validates hash against blockchain and recomputes payload hash.
   - Displays credential holder info, doc type, title, blockchain proof without needing a physical file.

---

## 7. Recommended Implementation Blueprint for Bulk Issuance

### 7.1 Backend Blueprint: New Routes in `routes/issuer_routes.py`
1. `GET /issuer/bulk-issue`: Renders bulk issuance upload interface (`templates/issuer/bulk_issue.html`).
2. `POST /issuer/bulk-issue`:
   - Validates uploaded `.csv` file.
   - Parses CSV via `csv.DictReader` with stripped header keys and values.
   - Validates all rows with complete error accumulation.
   - If invalid: rolls back session, flashes specific error with row number, re-renders page.
   - If valid: iterates rows, creates students if missing, calls `issue_credential()`, flashes success with count and block range, redirects to `/issuer/`.
3. `GET /issuer/template.csv`:
   - Returns a downloadable sample CSV containing proper headers:
     `roll_number,student_name,doc_type,title,validity_days`
   - Includes sample rows illustrating valid values.

---

## 8. Summary of Findings & Next Steps
The backend architecture is clean, modular, and natively supports text-only credential issuance without requiring structural changes to database models or blockchain hashing algorithms. All prerequisites for implementing Bulk Issuance (R1, R2, R3) are confirmed.
