"""
Admin portal — super-admin oversight of all institutions, users, and credentials.

Blueprint URL prefix: /admin/
All views require role='admin'.
"""
from flask import (
    Blueprint, flash, jsonify, redirect, render_template,
    request, url_for,
)
from flask_login import current_user

from decorators import admin_required
from extensions import db, utcnow
from models.document import Doc
from models.institution import Institution
from models.user import ROLE_ADMIN, ROLE_ISSUER, ROLE_STUDENT, ROLE_VERIFIER, User
from models.verification_log import VerificationLog

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_required
def dashboard():
    """System-wide stats overview."""
    stats = {
        'users': User.query.count(),
        'students': User.query.filter_by(role=ROLE_STUDENT).count(),
        'issuers': User.query.filter_by(role=ROLE_ISSUER).count(),
        'verifiers': User.query.filter_by(role=ROLE_VERIFIER).count(),
        'institutions': Institution.query.count(),
        'pending_institutions': Institution.query.filter_by(is_approved=False).count(),
        'approved_institutions': Institution.query.filter_by(is_approved=True).count(),
        'documents': Doc.query.count(),
        'revoked': Doc.query.filter_by(revoked=True).count(),
        'verifications': VerificationLog.query.count(),
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    pending = Institution.query.filter_by(is_approved=False).order_by(Institution.created_at.desc()).all()
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users,
                           pending_institutions=pending)


@admin_bp.route('/users')
@admin_required
def users():
    role_filter = request.args.get('role', '')
    q = request.args.get('q', '').strip()
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if q:
        query = query.filter(
            (User.username.ilike(f'%{q}%')) | (User.email.ilike(f'%{q}%'))
        )
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=25)
    return render_template('admin/users.html', pagination=pagination,
                           role_filter=role_filter, q=q)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))
    if user.role == ROLE_ADMIN:
        flash('Cannot deactivate another admin.', 'warning')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    state = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} {state}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/institutions')
@admin_required
def institutions():
    q = request.args.get('q', '').strip()
    query = Institution.query
    if q:
        query = query.filter(
            (Institution.name.ilike(f'%{q}%')) | (Institution.short_code.ilike(f'%{q}%'))
        )
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Institution.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/institutions.html', pagination=pagination, q=q)


@admin_bp.route('/institutions/<int:inst_id>/approve', methods=['POST'])
@admin_required
def approve_institution(inst_id):
    inst = db.session.get(Institution, inst_id)
    if not inst:
        flash('Institution not found.', 'danger')
        return redirect(url_for('admin.institutions'))
    inst.is_approved = True
    inst.approved_at = utcnow()
    inst.approved_by_id = current_user.id
    db.session.commit()
    flash(f'"{inst.name}" approved.', 'success')
    return redirect(url_for('admin.institutions'))


@admin_bp.route('/institutions/<int:inst_id>/revoke', methods=['POST'])
@admin_required
def revoke_institution(inst_id):
    inst = db.session.get(Institution, inst_id)
    if not inst:
        flash('Institution not found.', 'danger')
        return redirect(url_for('admin.institutions'))
    inst.is_approved = False
    inst.approved_at = None
    db.session.commit()
    flash(f'"{inst.name}" approval revoked.', 'warning')
    return redirect(url_for('admin.institutions'))


@admin_bp.route('/documents')
@admin_required
def documents():
    q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '')
    query = Doc.query
    if q:
        query = query.filter(
            (Doc.title.ilike(f'%{q}%')) | (Doc.doc_hash.ilike(f'%{q}%'))
        )
    if status_filter == 'revoked':
        query = query.filter_by(revoked=True)
    elif status_filter == 'active':
        query = query.filter_by(revoked=False)
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Doc.issued_on.desc()).paginate(page=page, per_page=25)
    return render_template('admin/documents.html', pagination=pagination, q=q,
                           status_filter=status_filter)


@admin_bp.route('/documents/<int:doc_id>/revoke', methods=['POST'])
@admin_required
def revoke_document(doc_id):
    doc = db.session.get(Doc, doc_id)
    if not doc:
        flash('Document not found.', 'danger')
        return redirect(url_for('admin.documents'))
    reason = (request.form.get('reason') or '').strip() or 'Revoked by administrator.'
    doc.revoked = True
    doc.revoked_reason = reason
    db.session.commit()
    flash(f'Document "{doc.title}" revoked.', 'warning')
    return redirect(url_for('admin.documents'))


@admin_bp.route('/documents/<int:doc_id>/restore', methods=['POST'])
@admin_required
def restore_document(doc_id):
    doc = db.session.get(Doc, doc_id)
    if not doc:
        flash('Document not found.', 'danger')
        return redirect(url_for('admin.documents'))
    doc.revoked = False
    doc.revoked_reason = None
    db.session.commit()
    flash(f'Document "{doc.title}" restored.', 'success')
    return redirect(url_for('admin.documents'))


@admin_bp.route('/stats.json')
@admin_required
def stats_json():
    """Return system stats as JSON for dashboard charts."""
    from models.student import Student
    return jsonify({
        'users': {
            'student': User.query.filter_by(role=ROLE_STUDENT).count(),
            'issuer': User.query.filter_by(role=ROLE_ISSUER).count(),
            'verifier': User.query.filter_by(role=ROLE_VERIFIER).count(),
            'admin': User.query.filter_by(role=ROLE_ADMIN).count(),
        },
        'institutions': {
            'approved': Institution.query.filter_by(is_approved=True).count(),
            'pending': Institution.query.filter_by(is_approved=False).count(),
        },
        'documents': {
            'total': Doc.query.count(),
            'revoked': Doc.query.filter_by(revoked=True).count(),
            'active': Doc.query.filter_by(revoked=False).count(),
        },
        'verifications': VerificationLog.query.count(),
    })
