"""
Verifier Portal: authenticated verification workflow with QR scanning, history, and fraud reporting.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from decorators import verifier_required
from services.verification_service import verify_hash as run_verification
from models.document import Doc
from models.fraud_report import FraudReport
from models.verification_log import VerificationLog
from extensions import db

verifier_bp = Blueprint('verifier', __name__, url_prefix='/verifier')


@verifier_bp.route('/dashboard', methods=['GET', 'POST'])
@verifier_required
def dashboard():
    """Dashboard with QR scanner and manual hash entry."""
    if request.method == 'POST':
        doc_hash = (request.form.get('doc_hash') or '').strip()
        if doc_hash:
            return redirect(url_for('verifier.verify_hash_result', doc_hash=doc_hash))
        return render_template('verifier/dashboard.html', error='Enter a credential hash to verify.')

    recent_logs = VerificationLog.query.filter_by(verifier_id=current_user.id).order_by(VerificationLog.timestamp.desc()).limit(5).all()
    recent_reports = FraudReport.query.filter_by(verifier_id=current_user.id).order_by(FraudReport.timestamp.desc()).limit(5).all()

    stats = {
        'total_checks': VerificationLog.query.filter_by(verifier_id=current_user.id).count(),
        'valid_checks': VerificationLog.query.filter_by(verifier_id=current_user.id, result='VALID').count(),
        'flagged_checks': VerificationLog.query.filter_by(verifier_id=current_user.id).filter(VerificationLog.result != 'VALID').count(),
        'reports_count': len(recent_reports),
    }

    return render_template(
        'verifier/dashboard.html',
        error=None,
        recent_logs=recent_logs,
        recent_reports=recent_reports,
        stats=stats,
    )


@verifier_bp.route('/v/<doc_hash>')
@verifier_required
def verify_hash_result(doc_hash):
    """Result of verification for authenticated verifiers."""
    token = request.args.get('t')
    verifier_label = current_user.organization or current_user.display_name

    if token is not None:
        outcome = run_verification(doc_hash, method='QR', qr_token=token, label=verifier_label)
    else:
        outcome = run_verification(doc_hash, method='HASH', label=verifier_label)

    from security import truncate_hash, visual_hash_swatches

    doc = outcome.get('doc')
    return render_template(
        'verifier/verify_result.html',
        outcome=outcome,
        doc=doc,
        block=outcome.get('block'),
        queried_hash=doc_hash,
        short_hash=truncate_hash(doc_hash),
        swatches=visual_hash_swatches(doc_hash),
        was_dynamic=token is not None,
    )


@verifier_bp.route('/history')
@verifier_required
def history():
    """View verification history performed by this verifier."""
    search = (request.args.get('q') or '').strip()
    result_filter = (request.args.get('result') or '').strip().upper()

    query = VerificationLog.query.filter_by(verifier_id=current_user.id)

    if result_filter:
        query = query.filter(VerificationLog.result == result_filter)

    logs = query.order_by(VerificationLog.timestamp.desc()).all()

    if search:
        needle = search.lower()
        filtered = []
        for l in logs:
            title = l.doc.title if l.doc else ''
            holder = l.doc.student.full_name if l.doc and l.doc.student else ''
            roll = l.doc.student.roll_number if l.doc and l.doc.student else ''
            h = l.queried_hash or ''
            if needle in f"{title} {holder} {roll} {h}".lower():
                filtered.append(l)
        logs = filtered

    stats = {
        'total': VerificationLog.query.filter_by(verifier_id=current_user.id).count(),
        'valid': VerificationLog.query.filter_by(verifier_id=current_user.id, result='VALID').count(),
        'expired': VerificationLog.query.filter_by(verifier_id=current_user.id, result='EXPIRED').count(),
        'tampered': VerificationLog.query.filter_by(verifier_id=current_user.id, result='TAMPERED').count(),
        'not_found': VerificationLog.query.filter_by(verifier_id=current_user.id, result='NOT_FOUND').count(),
    }

    return render_template(
        'verifier/history.html',
        logs=logs,
        search=search,
        result_filter=result_filter,
        stats=stats,
    )


@verifier_bp.route('/report-fraud', methods=['POST'])
@verifier_required
def report_fraud():
    """Report a fraudulent document hash."""
    doc_hash = (request.form.get('doc_hash') or '').strip()
    notes = (request.form.get('notes') or '').strip()

    if not doc_hash:
        flash('Document hash is required to report fraud.', 'danger')
        return redirect(url_for('verifier.dashboard'))

    report = FraudReport(
        doc_hash=doc_hash,
        verifier_id=current_user.id,
        notes=notes,
    )
    db.session.add(report)
    db.session.commit()

    flash('Fraud report submitted successfully to the registry.', 'success')
    return redirect(url_for('verifier.dashboard'))


# ─── Batch Verification & Audit Reports ────────────────────────────────────────
@verifier_bp.route('/batch', methods=['GET', 'POST'])
@verifier_required
def batch_verify():
    """
    Batch verification: Verify multiple credential hashes via CSV upload or text area.
    """
    results = []
    stats = {'total': 0, 'valid': 0, 'expired': 0, 'tampered': 0, 'revoked': 0, 'not_found': 0}

    if request.method == 'POST':
        hashes = []
        raw_text = (request.form.get('raw_hashes') or '').strip()

        # 1. Parse textarea input
        if raw_text:
            for line in raw_text.replace(',', '\n').splitlines():
                clean = line.strip()
                if clean and clean not in hashes:
                    hashes.append(clean)

        # 2. Parse CSV file upload
        csv_file = request.files.get('csv_file')
        if csv_file and csv_file.filename:
            try:
                import csv
                import io
                content = csv_file.stream.read().decode('utf-8-sig', errors='replace')
                reader = csv.reader(io.StringIO(content))
                header = next(reader, None)

                # Determine hash column index if headers exist
                hash_col = 0
                if header:
                    for idx, col in enumerate(header):
                        if any(term in col.lower() for term in ('hash', 'doc_hash', 'credential_hash')):
                            hash_col = idx
                            break
                    else:
                        # If first row wasn't a recognized header, check if it's a hash itself
                        first_val = header[0].strip()
                        if len(first_val) in (16, 64) and first_val not in hashes:
                            hashes.append(first_val)

                for row in reader:
                    if row and len(row) > hash_col:
                        val = row[hash_col].strip()
                        if val and val not in hashes:
                            hashes.append(val)
            except Exception as e:
                flash(f'Error reading CSV file: {e}', 'danger')

        verifier_label = current_user.organization or current_user.display_name

        # Run verification on all parsed hashes
        for h in hashes:
            outcome = run_verification(h, method='BATCH', label=verifier_label)
            res_type = outcome.get('result', 'NOT_FOUND')
            stats['total'] += 1
            if res_type == 'VALID':
                stats['valid'] += 1
            elif res_type == 'EXPIRED':
                stats['expired'] += 1
            elif res_type == 'REVOKED':
                stats['revoked'] += 1
            elif res_type in ('TAMPERED', 'QR_EXPIRED'):
                stats['tampered'] += 1
            else:
                stats['not_found'] += 1

            results.append({
                'hash': h,
                'outcome': outcome,
                'doc': outcome.get('doc'),
                'block': outcome.get('block'),
            })

    return render_template('verifier/batch_verify.html', results=results, stats=stats)


@verifier_bp.route('/history/export.csv')
@verifier_required
def export_history_csv():
    """Export the verifier's entire audit log to a downloadable CSV."""
    import csv
    import io
    from flask import Response

    logs = VerificationLog.query.filter_by(
        verifier_id=current_user.id
    ).order_by(VerificationLog.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Verification ID', 'Timestamp (UTC)', 'Result', 'Verification Method',
        'Queried Hash', 'Document Title', 'Document Type', 'Student Name',
        'Student Roll Number', 'Issuer Name', 'IP Address (v4)', 'User Agent'
    ])

    for l in logs:
        doc = l.doc
        writer.writerow([
            l.id,
            l.timestamp.strftime('%Y-%m-%d %H:%M:%S') if l.timestamp else '',
            l.result,
            l.method or 'HASH',
            l.queried_hash or '',
            doc.title if doc else 'Unregistered Credential',
            doc.type_label if doc else 'N/A',
            doc.student.full_name if (doc and doc.student) else 'N/A',
            doc.student.roll_number if (doc and doc.student) else 'N/A',
            doc.issuer_name if doc else 'N/A',
            l.ipv4 or '',
            l.user_agent or '',
        ])

    csv_data = output.getvalue()
    filename = f'Satyameva_Verification_Audit_{current_user.username}.csv'

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Cache-Control': 'no-store',
        }
    )


@verifier_bp.route('/history/audit-report')
@verifier_required
def audit_report():
    """Printable official audit report with cryptographic verification summary."""
    logs = VerificationLog.query.filter_by(
        verifier_id=current_user.id
    ).order_by(VerificationLog.timestamp.desc()).limit(50).all()

    stats = {
        'total': VerificationLog.query.filter_by(verifier_id=current_user.id).count(),
        'valid': VerificationLog.query.filter_by(verifier_id=current_user.id, result='VALID').count(),
        'flagged': VerificationLog.query.filter_by(verifier_id=current_user.id).filter(
            VerificationLog.result != 'VALID'
        ).count(),
    }

    import hashlib
    # Compute audit summary hash
    raw_material = f"{current_user.id}|{stats['total']}|{stats['valid']}|{len(logs)}"
    report_hash = hashlib.sha256(raw_material.encode('utf-8')).hexdigest()

    return render_template(
        'verifier/audit_report.html',
        logs=logs,
        stats=stats,
        report_hash=report_hash,
    )

