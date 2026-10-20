"""
Issuer portal — the institution's side of the credential lifecycle.

An issuer looks up a student by roll number, uploads the source document and
its metadata, and the credential is minted (hashed + anchored on the chain)
by `issue_credential`. From that moment it appears in the student's dashboard
and can be verified by anyone holding the hash.
"""
import csv
import io
import os
from flask import (
    Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request,
    send_from_directory, url_for,
)
from flask_login import current_user
from werkzeug.utils import secure_filename

from decorators import issuer_required, subscription_required
from models.credential_request import CredentialRequest
import secrets
from extensions import db, utcnow
from models.document import DOC_TYPES, STATUS_EXPIRED, Doc
from models.student import Student
from models.user import ROLE_STUDENT, User
from security import hash_password
from services.credential_service import issue_credential

issuer_bp = Blueprint('issuer', __name__, url_prefix='/issuer')


@issuer_bp.route('/extract', methods=['POST'])
@issuer_required
@subscription_required
def extract_fields():
    """AI-powered field extraction from uploaded document using Gemini."""
    file = request.files.get('document')
    if not file or not file.filename:
        return jsonify({'error': 'No file uploaded.'}), 400

    mime_type = file.mimetype or 'application/octet-stream'
    api_key = current_app.config.get('GEMINI_API_KEY', '')
    if not api_key:
        return jsonify({'error': 'Gemini API key not configured. Fill fields manually.'}), 200

    try:
        file_bytes = file.read()
    except Exception:
        return jsonify({'error': 'Could not read uploaded file.'}), 400

    from services.gemini_service import extract_document_fields
    result = extract_document_fields(file_bytes, mime_type, api_key)
    return jsonify(result)


def _get_or_create_student(roll_number: str, student_name: str | None = None, institution: str | None = None, student_email: str | None = None) -> Student:
    """
    Look up an existing student by roll number OR email, or auto-provision a new User and
    Student profile if one does not exist yet. Synchronizes candidature so credentials
    reliably link to the student's dashboard.
    """
    clean_roll = (roll_number or '').strip()
    clean_email = (student_email or '').strip().lower() if student_email else None
    
    student = None
    if clean_roll:
        student = Student.query.filter_by(roll_number=clean_roll).first()

    if student is None and clean_email:
        user_by_email = User.query.filter_by(email=clean_email).first()
        if user_by_email:
            student = Student.query.filter_by(user_id=user_by_email.id).first()

    inst_name = institution or getattr(current_user, 'organization', None) or 'Jaypee Institute of Information Technology'
    s_name = (student_name or '').strip()

    if student is not None:
        # Existing student found! Synchronize candidature details:
        if s_name and (not student.full_name or student.full_name.startswith('Student ')):
            student.full_name = s_name
        if clean_roll and not student.roll_number:
            student.roll_number = clean_roll
        if clean_email and student.user:
            # If user has a placeholder email, update to their real email
            if student.user.email != clean_email and (student.user.email.endswith('.edu') or 'satyameva' in student.user.email):
                student.user.email = clean_email
        db.session.flush()
        return student

    # No existing student: provision new User & Student profile
    s_name = s_name or (f"Student {clean_roll}" if clean_roll else "Student")
    username = f"student.{clean_roll}".lower().replace(' ', '_').replace('/', '_').replace('\\', '_') if clean_roll else f"student.{clean_email.split('@')[0]}"
    inst_slug = (inst_name).lower().replace(' ', '_').replace('/', '_')
    assigned_email = clean_email or f"{clean_roll.lower().replace('/', '_')}@{inst_slug}.edu"

    user = User.query.filter((User.username == username) | (User.email == assigned_email)).first()
    if not user:
        salt, digest, iters = hash_password('satyameva123')
        user = User(
            username=username,
            email=assigned_email,
            role=ROLE_STUDENT,
            organization=inst_name,
            password_salt=salt,
            password_hash=digest,
            password_iterations=iters,
        )
        db.session.add(user)
        db.session.flush()
    elif clean_email and user.email != clean_email:
        user.email = clean_email
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
        student_email = (row_dict.get('student_email', '') or row_dict.get('email', '')).strip().lower()
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
            'student_email': student_email or None,
            'validity_days': int(validity_days_str) if (validity_days_str and validity_days_str.isdigit() and int(validity_days_str) > 0) else None,
            'line_number': line_idx,
            'row_index': data_row_count,
        })

    if data_row_count == 0:
        return [], ["The CSV file contains a header but no data rows."]

    if errors:
        return [], errors

    return parsed_rows, []


def _issued_docs():
    """Every credential this issuer has minted, newest first."""
    return (Doc.query
            .filter_by(issuer_id=current_user.id)
            .order_by(Doc.issued_on.desc())
            .all())


def _issued_doc(doc_id: int) -> Doc:
    """Fetch a document, 404 if missing and 403 if issued by someone else."""
    doc = db.session.get(Doc, doc_id)
    if doc is None:
        abort(404)
    if doc.issuer_id != current_user.id and current_user.role != 'admin':
        abort(403)
    return doc


def _allowed_file(filename: str) -> bool:
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']


@issuer_bp.route('/')
@issuer_required
def dashboard():
    docs = _issued_docs()

    stats = {
        'total': len(docs),
        'active': sum(1 for d in docs if d.is_valid),
        'expired': sum(1 for d in docs if d.status == STATUS_EXPIRED),
        'revoked': sum(1 for d in docs if d.revoked),
        'verifications': sum(d.verification_count for d in docs),
    }

    search = (request.args.get('q') or '').strip()
    if search:
        needle = search.lower()
        docs = [d for d in docs if needle in (
            f'{d.title} {d.doc_hash} {d.student.full_name} '
            f'{d.student.roll_number}'.lower()
        )]

    return render_template(
        'issuer/dashboard.html',
        documents=docs, stats=stats, search=search,
    )


@issuer_bp.route('/issue', methods=['GET', 'POST'])
@issuer_required
@subscription_required
def issue():
    # Preserve what the issuer typed so a validation bounce is not punishing.
    form = {
        'roll_number': (request.form.get('roll_number') or '').strip(),
        'student_name': (request.form.get('student_name') or '').strip(),
        'student_email': (request.form.get('student_email') or '').strip().lower(),
        'doc_type': (request.form.get('doc_type') or '').strip().upper(),
        'title': (request.form.get('title') or '').strip(),
        'validity_days': (request.form.get('validity_days') or '').strip(),
    }

    if request.method == 'POST':
        errors = _validate_issue(form)
        student = None

        if not errors.get('roll_number'):
            student = _get_or_create_student(
                roll_number=form['roll_number'],
                student_name=form['student_name'] or None,
                institution=current_user.organization,
                student_email=form.get('student_email') or None,
            )

        upload = request.files.get('document')
        file_bytes = file_name = file_mime = None
        if upload and upload.filename:
            if not _allowed_file(upload.filename):
                errors['document'] = (
                    'Unsupported file type. Allowed: '
                    + ', '.join(sorted(current_app.config['ALLOWED_EXTENSIONS'])) + '.'
                )
            else:
                file_bytes = upload.read()
                file_name = secure_filename(upload.filename)
                file_mime = upload.mimetype or 'application/octet-stream'
                if not file_bytes:
                    errors['document'] = 'That file appears to be empty.'
        else:
            errors['document'] = 'Attach the source document to issue.'

        if errors:
            for message in errors.values():
                flash(message, 'danger')
            return render_template('issuer/issue.html', form=form, errors=errors)

        validity = int(form['validity_days']) if form['validity_days'] else None
        doc_title = form['title'] or DOC_TYPES.get(form['doc_type'], ('Credential', '📄', 365))[0]

        dob_extracted = (request.form.get('dob') or '').strip()
        if dob_extracted and student:
            student.dob = dob_extracted
        if student and not student.issuer_approved:
            student.issuer_approved = True
            student.issuer_approved_by_id = current_user.id
            student.issuer_approved_at = utcnow()
            db.session.commit()

        doc = issue_credential(
            student, current_user, form['doc_type'],
            doc_title,
            file_bytes=file_bytes, file_name=file_name, file_mime=file_mime,
            validity_days=validity,
        )

        flash(
            f'Issued {doc.type_label} to {student.full_name} '
            f'(Roll {student.roll_number}). It is now anchored on block '
            f'#{doc.block_index} and visible in their dashboard.',
            'success',
        )
        return redirect(url_for('issuer.dashboard'))

    return render_template('issuer/issue.html', form=form, errors={})


def _validate_issue(form: dict) -> dict:
    """Field-level validation for the issue form; returns {field: message}."""
    errors = {}
    if not form['roll_number']:
        errors['roll_number'] = 'Enter the student\'s roll number.'
    if form['doc_type'] not in DOC_TYPES:
        errors['doc_type'] = 'Choose a document type.'
    if not form['title']:
        errors['title'] = 'Give the document a title.'
    if form['validity_days']:
        if not form['validity_days'].isdigit() or int(form['validity_days']) <= 0:
            errors['validity_days'] = 'Validity must be a positive number of days.'
    return errors


@issuer_bp.route('/bulk-issue', methods=['GET', 'POST'])
@issuer_required
@subscription_required
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
        for err in validation_errors[:3]:
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
                student_email=row.get('student_email') or None,
            )

            doc_title = row['title'] or DOC_TYPES.get(row['doc_type'], ('Credential', '📄', 365))[0]

            issue_credential(
                student,
                current_user,
                row['doc_type'],
                doc_title,
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


@issuer_bp.route('/revoke/<int:doc_id>', methods=['POST'])
@issuer_required
def revoke(doc_id):
    """Withdraw a credential."""
    doc = _issued_doc(doc_id)
    if doc.revoked:
        flash('That credential is already revoked.', 'info')
        return redirect(url_for('issuer.dashboard'))

    doc.revoked = True
    doc.revoked_reason = (request.form.get('reason') or '').strip() or 'Revoked by issuer.'
    db.session.commit()
    flash(f'Revoked "{doc.title}" for {doc.student.full_name}. '
          f'It will now fail verification.', 'warning')
    return redirect(url_for('issuer.dashboard'))


# ─── Student Management & Verification Gates ──────────────────────────────────
@issuer_bp.route('/students')
@issuer_required
def students():
    """List students belonging to this issuer's campus/organization."""
    inst_org = getattr(current_user, 'organization', '') or ''
    inst_code = ''
    if getattr(current_user, 'institution', None):
        inst_code = current_user.institution.short_code.upper()

    query = Student.query.join(Student.user)
    if inst_code:
        query = query.filter(
            db.or_(
                Student.institution.ilike(f'%{inst_code}%'),
                Student.institution.ilike(f'%{inst_org}%') if inst_org else False,
                User.organization.ilike(f'%{inst_code}%'),
                User.institution_id == current_user.institution_id if current_user.institution_id else False,
            )
        )
    elif inst_org:
        query = query.filter(
            db.or_(
                Student.institution.ilike(f'%{inst_org}%'),
                User.organization.ilike(f'%{inst_org}%'),
            )
        )

    all_students = query.order_by(Student.created_at.desc()).all()
    if not all_students:
        all_students = Student.query.order_by(Student.created_at.desc()).limit(100).all()

    req_count = CredentialRequest.query.filter_by(status='pending').count()
    return render_template('issuer/students.html', students=all_students, pending_requests_count=req_count)


@issuer_bp.route('/students/<int:student_id>/approve', methods=['POST'])
@issuer_required
def approve_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('issuer.students'))

    student.issuer_approved = True
    student.issuer_approved_by_id = current_user.id
    from extensions import utcnow
    student.issuer_approved_at = utcnow()
    db.session.commit()

    from services.email_service import send_student_approved_email
    send_student_approved_email(student)

    flash(f'Student "{student.full_name}" ({student.roll_number}) approved successfully.', 'success')
    return redirect(url_for('issuer.students'))


@issuer_bp.route('/students/<int:student_id>/reject', methods=['POST'])
@issuer_required
def reject_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('issuer.students'))

    student.issuer_approved = False
    db.session.commit()
    flash(f'Student "{student.full_name}" access approval revoked.', 'warning')
    return redirect(url_for('issuer.students'))


@issuer_bp.route('/students/<int:student_id>/send-verify-email', methods=['POST'])
@issuer_required
def send_verify_email(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('issuer.students'))

    token = secrets.token_hex(32)
    student.email_verify_token = token
    from extensions import utcnow
    student.email_verify_sent_at = utcnow()
    db.session.commit()

    verify_url = url_for('auth.verify_email', token=token, _external=True)
    from services.email_service import send_student_verification_email
    sent = send_student_verification_email(student, verify_url)

    target_email = getattr(getattr(student, 'user', None), 'email', 'student email')
    if sent:
        flash(f'Verification email dispatched to {target_email}.', 'success')
    else:
        flash(f'Verification link generated: {verify_url}', 'info')
    return redirect(url_for('issuer.students'))


# ─── Student Credential Requests (Correction / Re-issuance) ───────────────────
@issuer_bp.route('/requests')
@issuer_required
def requests():
    """View all credential correction and re-issuance requests from students."""
    reqs = CredentialRequest.query.order_by(CredentialRequest.created_at.desc()).all()
    return render_template('issuer/requests.html', requests=reqs)


@issuer_bp.route('/requests/<int:req_id>/resolve', methods=['POST'])
@issuer_required
def resolve_request(req_id):
    cr = db.session.get(CredentialRequest, req_id)
    if not cr:
        flash('Request not found.', 'danger')
        return redirect(url_for('issuer.requests'))

    action = request.form.get('action')  # 'approve' | 'reject'
    note = (request.form.get('resolver_note') or '').strip()

    from extensions import utcnow
    cr.status = 'approved' if action == 'approve' else 'rejected'
    cr.resolved_at = utcnow()
    cr.resolved_by_id = current_user.id
    cr.resolver_note = note
    db.session.commit()

    flash(f'Request #{cr.id} marked as {cr.status.upper()}.', 'success')
    return redirect(url_for('issuer.requests'))
