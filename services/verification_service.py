"""
Verification logic shared by the public verifier page, authenticated verifier portal, and QR flow.

Every attempt — success or failure — is written to `VerificationLog`, and successful checks
generate real-time `Notification` records for the student.
"""
from flask import current_app, request
from flask_login import current_user

from blockchain import get_block_for_doc, validate_chain
from extensions import db, utcnow
from models.document import Doc
from models.notification import Notification
from models.verification_log import (
    RESULT_EXPIRED, RESULT_NOT_FOUND, RESULT_QR_EXPIRED, RESULT_REVOKED,
    RESULT_TAMPERED, RESULT_VALID, VerificationLog,
)
from security import check_qr_token, get_client_ips, hashes_match, recompute_document_hash


def log_attempt(doc, result, queried_hash=None, method='HASH', label=None):
    """Record one verification attempt with its network fingerprint and notify student on success."""
    from flask import has_request_context
    if has_request_context():
        ipv4, ipv6 = get_client_ips(request, current_app.config.get('TRUST_PROXY_HEADERS', False))
        user_agent = (request.headers.get('User-Agent') or '')[:255]
    else:
        ipv4, ipv6 = '127.0.0.1', None
        user_agent = 'Verification Service / Script'

    verifier_user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
    
    # Derive verifier display label if not explicitly provided
    if not label and getattr(current_user, 'is_authenticated', False):
        if current_user.organization:
            label = current_user.organization
        elif current_user.display_name:
            label = current_user.display_name

    entry = VerificationLog(
        doc_id=doc.id if doc else None,
        verifier_id=verifier_user_id,
        verifier_label=label,
        queried_hash=(queried_hash or (doc.doc_hash if doc else None)),
        ipv4=ipv4,
        ipv6=ipv6,
        user_agent=user_agent,
        method=method,
        result=result,
    )
    db.session.add(entry)

    # Only successful checks count toward the public "times verified" figure
    # and trigger a student notification
    if doc is not None and result == RESULT_VALID:
        doc.verification_count = (doc.verification_count or 0) + 1
        doc.last_verified_at = utcnow()

        # Create student notification
        verifier_who = label or ("Public QR Scan (Employer)" if method == 'QR' else "an employer/verifier")
        notification = Notification(
            student_id=doc.student_id,
            doc_id=doc.id,
            title=f'{doc.type_label} Verified',
            message=f'Your {doc.title} was successfully verified by {verifier_who}.',
            category='success',
            verifier_label=verifier_who,
        )
        db.session.add(notification)

        # Dispatch real-time security alert email to student from Gmail SMTP
        if doc.student:
            try:
                from services.email_service import send_verification_alert_student
                send_verification_alert_student(
                    doc=doc,
                    student=doc.student,
                    verifier_label=verifier_who,
                    method=method,
                    timestamp=doc.last_verified_at,
                )
            except Exception as e:
                current_app.logger.error('Failed to dispatch student verification alert email: %s', e)

    db.session.commit()
    return entry


def verify_hash(doc_hash: str, method: str = 'HASH', qr_token: str | None = None, label: str | None = None) -> dict:
    """
    Resolve a document hash to a verdict.

    Returns a dict the templates render directly:
      { ok, result, message, doc, block, chain_ok, chain_message }

    Checks run cheapest-first and short-circuit: existence → QR freshness →
    revocation → integrity → expiry.
    """
    doc_hash = (doc_hash or '').strip().lower()

    if not doc_hash:
        return {'ok': False, 'result': RESULT_NOT_FOUND, 'doc': None, 'block': None,
                'message': 'No credential hash supplied.'}

    doc = Doc.query.filter_by(doc_hash=doc_hash).first()
    if doc is None:
        log_attempt(None, RESULT_NOT_FOUND, queried_hash=doc_hash, method=method, label=label)
        return {'ok': False, 'result': RESULT_NOT_FOUND, 'doc': None, 'block': None,
                'message': 'No such credential on the Satyameva ledger. '
                           'This document is not authentic.'}

    # A QR token is time-boxed, so a forwarded screenshot fails here.
    if qr_token is not None:
        token_ok, reason = check_qr_token(doc_hash, qr_token, current_app.config['SECRET_KEY'])
        if not token_ok:
            log_attempt(doc, RESULT_QR_EXPIRED, method='QR', label=label)
            note = ('This QR code has expired. Ask the student for a freshly generated code.'
                    if reason == 'expired' else
                    'This QR code is not valid for the credential it points to.')
            return {'ok': False, 'result': RESULT_QR_EXPIRED, 'doc': doc, 'block': None,
                'message': note}

    if doc.revoked:
        log_attempt(doc, RESULT_REVOKED, method=method, label=label)
        chain_ok, chain_message = validate_chain()
        return {'ok': False, 'result': RESULT_REVOKED, 'doc': doc,
                'block': get_block_for_doc(doc_hash),
                'chain_ok': chain_ok, 'chain_message': chain_message,
                'message': f'This credential was revoked by the issuer. '
                           f'{doc.revoked_reason or ""}'.strip()}

    # Re-derive the hash from the stored payload
    if not hashes_match(recompute_document_hash(doc), doc.doc_hash):
        log_attempt(doc, RESULT_TAMPERED, method=method, label=label)
        return {'ok': False, 'result': RESULT_TAMPERED, 'doc': doc, 'block': None,
                'message': 'Integrity check failed — the stored record does not match '
                           'its blockchain hash. Treat this document as tampered.'}

    # Verify asymmetric cryptographic signature if anchored with issuer key
    signature_ok = True
    if doc.signature and doc.issuer_public_key:
        try:
            from services.crypto_service import verify_hash_signature
            signature_ok = verify_hash_signature(doc.issuer_public_key, doc.doc_hash, doc.signature)
        except Exception:
            signature_ok = False

        if not signature_ok:
            log_attempt(doc, RESULT_TAMPERED, method=method, label=label)
            return {'ok': False, 'result': RESULT_TAMPERED, 'doc': doc, 'block': None,
                    'message': 'Cryptographic signature verification failed — '
                               'the credential signature does not match the issuer public key.'}

    block = get_block_for_doc(doc_hash)
    chain_ok, chain_message = validate_chain()

    if not doc.is_valid:
        log_attempt(doc, RESULT_EXPIRED, method=method, label=label)
        return {'ok': False, 'result': RESULT_EXPIRED, 'doc': doc, 'block': block,
                'chain_ok': chain_ok, 'chain_message': chain_message,
                'message': 'This credential is genuine but has passed its validity date.'}

    log_attempt(doc, RESULT_VALID, method=method, label=label)
    return {'ok': True, 'result': RESULT_VALID, 'doc': doc, 'block': block,
            'chain_ok': chain_ok, 'chain_message': chain_message,
            'message': 'Authentic credential — verified against the Satyameva blockchain.'}
