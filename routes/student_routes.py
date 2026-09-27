"""
The Student Portal.

Every view here resolves the *current* student first and scopes its query to
that student's id, so a student can never reach another student's credential
by guessing a URL.
"""
import json
from flask import (
    Blueprint, Response, abort, current_app, flash, jsonify, redirect,
    render_template, request, url_for,
)
from flask_login import current_user

from blockchain import chain_length, get_block_for_doc, validate_chain
from decorators import student_required
from extensions import db, utcnow
from models.document import (
    DOC_TYPES, STATUS_EXPIRED, STATUS_EXPIRING, STATUS_VALID, Doc,
)
from models.notification import Notification
from models.student import Student
from security import make_qr_token, truncate_hash, visual_hash_swatches
from services.notification_service import build_notifications, unread_count
from services.qr_service import qr_data_uri, qr_png_bytes
from services.stamp_service import generate_stamped_image, generate_stamped_pdf

student_bp = Blueprint('student', __name__, url_prefix='/student')


# ─── Scoping helpers ──────────────────────────────────────────────────────────
def _current_student() -> Student:
    """
    The Student row behind the logged-in user.
    """
    student = Student.query.filter_by(user_id=current_user.id).first()
    if student is None:
        if current_user.role == 'admin':
            student = Student.query.order_by(Student.id.asc()).first()
        if student is None:
            abort(404, 'No student profile is linked to this account.')
    return student


def _owned_doc(doc_id: int) -> tuple[Doc, Student]:
    """Fetch a document, but only if it belongs to the current student."""
    student = _current_student()
    doc = db.session.get(Doc, doc_id)
    if doc is None:
        abort(404)
    if doc.student_id != student.id and current_user.role != 'admin':
        abort(403)
    return doc, student


def _get_doc_campus_code(doc: Doc, student: Student | None = None) -> str:
    """Resolve authentic issuing Jaypee campus code (JIIT, JUIT, JUET, or AEGIS)."""
    # 1. From Issuer's Institution
    if doc.issuer and getattr(doc.issuer, 'institution', None) and doc.issuer.institution.short_code:
        return doc.issuer.institution.short_code.upper()

    # 2. From Issuer display name
    issuer_name = (doc.issuer_name or '').upper()
    if 'JIIT' in issuer_name or 'NOIDA' in issuer_name:
        return 'JIIT'
    if 'JUIT' in issuer_name or 'WAKNAGHAT' in issuer_name or 'SOLAN' in issuer_name:
        return 'JUIT'
    if 'JUET' in issuer_name or 'GUNA' in issuer_name:
        return 'JUET'

    # 3. From Student's assigned institution
    student_inst = ((student.institution if student else None) or '').upper()
    if 'JIIT' in student_inst:
        return 'JIIT'
    if 'JUIT' in student_inst:
        return 'JUIT'
    if 'JUET' in student_inst:
        return 'JUET'

    return 'JIIT'


def _verify_url(doc: Doc, with_token: bool = False) -> tuple[str, int | None]:
    """
    Public verification URL for a credential (permanent blockchain QR).
    """
    if not with_token:
        return url_for('public.verify_hash', doc_hash=doc.doc_hash, src='qr', _external=True), None

    ttl = current_app.config['QR_TOKEN_TTL_SECONDS']
    token, expires_at = make_qr_token(doc.doc_hash, current_app.config['SECRET_KEY'], ttl)
    url = url_for('public.verify_hash', doc_hash=doc.doc_hash, t=token, src='qr', _external=True)
    return url, expires_at


# ─── Dashboard ────────────────────────────────────────────────────────────────
@student_bp.route('/dashboard')
@student_required
def dashboard():
    student = _current_student()

    query = Doc.query.filter_by(student_id=student.id)

    # ---- Filters ----
    doc_type = (request.args.get('type') or '').upper()
    status_filter = (request.args.get('status') or '').upper()
    search = (request.args.get('q') or '').strip()

    if doc_type:
        query = query.filter_by(doc_type=doc_type)

    if status_filter == 'VALID':
        query = query.filter(
            Doc.revoked.is_(False),
            db.or_(Doc.valid_until.is_(None), Doc.valid_until > utcnow()),
        )
    elif status_filter == 'EXPIRED':
        query = query.filter(Doc.valid_until.isnot(None), Doc.valid_until <= utcnow())
    elif status_filter == 'REVOKED':
        query = query.filter_by(revoked=True)

    if search:
        # Search by title or roll number
        query = query.filter(
            db.or_(
                Doc.title.ilike(f'%{search}%'),
                Doc.doc_hash.ilike(f'%{search}%'),
            ),
        )

    documents = query.order_by(Doc.issued_on.desc()).all()

    # Pre-generate QR code for each document card with authentic campus emblem
    for d in documents:
        v_url = url_for('public.verify_hash', doc_hash=d.doc_hash, _external=True)
        c_code = _get_doc_campus_code(d, student)
        d.card_qr = qr_data_uri(v_url, campus_code=c_code, box_size=4, border=1)

    # ---- Stats bar ----
    all_docs = Doc.query.filter_by(student_id=student.id).all()
    stats = {
        'total': len(all_docs),
        'valid': sum(1 for d in all_docs if d.status == STATUS_VALID),
        'expiring': sum(1 for d in all_docs if d.status == STATUS_EXPIRING),
        'expired': sum(1 for d in all_docs if d.status == STATUS_EXPIRED),
        'revoked': sum(1 for d in all_docs if d.revoked),
        'verifications': sum(d.verification_count or 0 for d in all_docs),
    }

    chain_ok, chain_message = validate_chain()

    return render_template(
        'student/dashboard.html',
        student=student,
        documents=documents,
        stats=stats,
        doc_types=DOC_TYPES,
        active_type=doc_type,
        active_status=status_filter,
        search=search,
        chain_ok=chain_ok,
        chain_message=chain_message,
        chain_blocks=chain_length(),
        alert_count=unread_count(student, all_docs),
    )


# ─── Document detail ──────────────────────────────────────────────────────────
@student_bp.route('/document/<int:doc_id>')
@student_required
def document_detail(doc_id):
    doc, student = _owned_doc(doc_id)
    block = get_block_for_doc(doc.doc_hash)
    chain_ok, chain_message = validate_chain()
    campus_code = _get_doc_campus_code(doc, student)

    permanent_url, _ = _verify_url(doc, with_token=False)
    qr_url = permanent_url

    return render_template(
        'student/document_detail.html',
        student=student,
        doc=doc,
        block=block,
        chain_ok=chain_ok,
        chain_message=chain_message,
        campus_code=campus_code,
        qr_image=qr_data_uri(qr_url, campus_code=campus_code),
        qr_url=qr_url,
        qr_expires=None,
        qr_ttl=None,
        permanent_url=permanent_url,
        short_hash=truncate_hash(doc.doc_hash),
        swatches=visual_hash_swatches(doc.doc_hash),
        recent_logs=doc.logs[:5],
        alert_count=unread_count(student, student.documents),
    )


# ─── Original file preview ────────────────────────────────────────────────────
@student_bp.route('/document/<int:doc_id>/preview')
@student_required
def document_preview(doc_id):
    """Serve the raw upload inline, for the preview pane."""
    doc, _ = _owned_doc(doc_id)
    if not doc.file_data:
        abort(404)

    return Response(
        doc.file_data,
        mimetype=doc.file_mime or 'application/octet-stream',
        headers={
            'Content-Disposition': f'inline; filename="{doc.file_name or "document"}"',
            'Cache-Control': 'private, max-age=300',
            'X-Content-Type-Options': 'nosniff',
        },
    )


# ─── Downloads ────────────────────────────────────────────────────────────────
@student_bp.route('/document/<int:doc_id>/download')
@student_required
def download_stamped(doc_id):
    """
    Stamped PDF: the original page plus generated verification certificate.
    """
    doc, student = _owned_doc(doc_id)

    if not doc.is_stamped:
        doc.is_stamped = True
        doc.stamp_date = utcnow()
        doc.stamped_by = doc.issuer_id or current_user.id
        db.session.commit()

    campus_code = _get_doc_campus_code(doc, student)
    permanent_url, _ = _verify_url(doc, with_token=False)
    pdf_bytes = generate_stamped_pdf(doc, student, permanent_url, campus_code=campus_code)

    safe_roll = (student.roll_number or 'student').replace('/', '-').replace('\\', '-')
    filename = f'Satyameva_{campus_code}_{doc.doc_type}_{safe_roll}.pdf'

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Cache-Control': 'no-store',
        },
    )


@student_bp.route('/document/<int:doc_id>/download/image')
@student_required
def download_stamped_image(doc_id):
    """Stamped PNG of the original upload."""
    doc, student = _owned_doc(doc_id)

    png = generate_stamped_image(doc)
    if png is None:
        flash('This credential has no image to stamp — download the PDF copy instead.', 'warning')
        return redirect(url_for('student.document_detail', doc_id=doc.id))

    if not doc.is_stamped:
        doc.is_stamped = True
        doc.stamp_date = utcnow()
        doc.stamped_by = doc.issuer_id or current_user.id
        db.session.commit()

    campus_code = _get_doc_campus_code(doc, student)
    safe_roll = (student.roll_number or 'student').replace('/', '-').replace('\\', '-')
    return Response(
        png,
        mimetype='image/png',
        headers={
            'Content-Disposition': f'attachment; filename="Satyameva_{campus_code}_{doc.doc_type}_{safe_roll}.png"',
            'Cache-Control': 'no-store',
        },
    )


# ─── QR sharing ───────────────────────────────────────────────────────────────
@student_bp.route('/document/<int:doc_id>/qr.png')
@student_required
def document_qr_png(doc_id):
    """Standalone QR image, for printing or saving with authentic Jaypee crest."""
    doc, student = _owned_doc(doc_id)
    campus_code = _get_doc_campus_code(doc, student)
    url, _ = _verify_url(doc, with_token=False)
    return Response(
        qr_png_bytes(url, campus_code=campus_code, box_size=12),
        mimetype='image/png',
        headers={
            'Content-Disposition': f'attachment; filename="Satyameva_{campus_code}_QR_{doc.doc_hash[:12]}.png"',
            'Cache-Control': 'no-store',
        },
    )


@student_bp.route('/document/<int:doc_id>/qr.json')
@student_required
def document_qr_json(doc_id):
    doc, student = _owned_doc(doc_id)
    campus_code = _get_doc_campus_code(doc, student)
    url, _ = _verify_url(doc, with_token=False)
    return jsonify({
        'image': qr_data_uri(url, campus_code=campus_code),
        'url': url,
        'expires_at': None,
        'ttl': None,
        'campus_code': campus_code,
    })


# ─── Verification history ─────────────────────────────────────────────────────
@student_bp.route('/document/<int:doc_id>/history')
@student_required
def document_history(doc_id):
    doc, student = _owned_doc(doc_id)
    return render_template(
        'student/history.html',
        student=student,
        doc=doc,
        logs=doc.logs,
        alert_count=unread_count(student, student.documents),
    )


@student_bp.route('/history')
@student_required
def all_history():
    """Every verification of every credential this student holds."""
    student = _current_student()
    logs = [log for doc in student.documents for log in doc.logs]
    logs.sort(key=lambda entry: entry.timestamp, reverse=True)

    return render_template(
        'student/history.html',
        student=student,
        doc=None,
        logs=logs,
        alert_count=unread_count(student, student.documents),
    )


# ─── Notifications ────────────────────────────────────────────────────────────
@student_bp.route('/notifications')
@student_required
def notifications():
    student = _current_student()
    alerts = build_notifications(
        student,
        student.documents,
        current_app.config['EXPIRY_WARNING_DAYS'],
    )
    return render_template(
        'student/notifications.html',
        student=student,
        alerts=alerts,
        alert_count=unread_count(student, student.documents),
    )


@student_bp.route('/notifications/mark-all-read', methods=['POST'])
@student_required
def mark_all_notifications_read():
    student = _current_student()
    Notification.query.filter_by(student_id=student.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('student.notifications'))


# ─── Chain integrity probe ────────────────────────────────────────────────────
@student_bp.route('/chain/validate')
@student_required
def chain_validate():
    """Let the student re-run the integrity check themselves, on demand."""
    ok, message = validate_chain()
    return jsonify({'ok': ok, 'message': message, 'blocks': chain_length()})
