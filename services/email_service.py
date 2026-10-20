"""
Email notification helpers for Satyameva.

Two fire-and-forget helpers -- any SMTP failure is caught, logged,
and the caller's main action (credential issuance) is never blocked.
"""
import logging

from flask import current_app, render_template, url_for
from flask_mail import Message

from extensions import mail

logger = logging.getLogger(__name__)


def _is_valid_email(email: str) -> bool:
    """Ensure recipient email matches valid syntax without invalid domain characters like underscores."""
    if not email or '@' not in email:
        return False
    user_part, domain_part = email.split('@', 1)
    if not domain_part or '.' not in domain_part or '_' in domain_part:
        return False
    return True


def _send(subject: str, recipients: list, html_template: str,
          txt_template: str, **ctx) -> bool:
    """Render and dispatch a multipart email asynchronously in the background."""
    if not recipients:
        return False

    valid_recipients = [r for r in recipients if _is_valid_email(r)]
    if not valid_recipients:
        logger.info('Skipping email "%s": no RFC-compliant recipients in %s', subject, recipients)
        return False

    try:
        html_body = render_template(html_template, **ctx)
        text_body = render_template(txt_template, **ctx)

        msg = Message(
            subject=subject,
            recipients=valid_recipients,
            body=text_body,
            html=html_body,
        )

        app = current_app._get_current_object()

        # If testing or suppressed, return immediately without connecting to SMTP
        if app.config.get('MAIL_SUPPRESS_SEND', False) or app.testing:
            return True

        # Non-blocking async background delivery
        from services.async_tasks import submit_with_app_context

        def _do_send():
            try:
                mail.send(msg)
            except Exception as exc:
                logger.error('Background email "%s" to %s failed: %s', subject, recipients, exc)

        submit_with_app_context(app, _do_send)
        return True

    except Exception as exc:
        logger.error('Failed to prepare email "%s" to %s: %s', subject, recipients, exc)
        return False


def send_credential_issued_student(doc, student) -> bool:
    """Notify the student that a new credential has been issued to them."""
    email = getattr(getattr(student, 'user', None), 'email', None)
    if not email:
        return False

    try:
        dashboard_url = url_for('student.dashboard', _external=True)
    except RuntimeError:
        dashboard_url = ''

    return _send(
        subject='New credential issued: ' + doc.title,
        recipients=[email],
        html_template='email/credential_issued_student.html',
        txt_template='email/credential_issued_student.txt',
        student=student,
        doc=doc,
        dashboard_url=dashboard_url,
        brand=current_app.config.get('INSTITUTION_NAME', 'Satyameva'),
    )


def send_credential_issued_issuer(doc, student, issuer) -> bool:
    """Send the issuer a confirmation that their credential was anchored on-chain."""
    email = getattr(issuer, 'email', None)
    if not email:
        return False

    try:
        issuer_dashboard_url = url_for('issuer.dashboard', _external=True)
    except RuntimeError:
        issuer_dashboard_url = ''

    return _send(
        subject='Credential issued: ' + doc.title + ' to ' + student.full_name,
        recipients=[email],
        html_template='email/credential_issued_issuer.html',
        txt_template='email/credential_issued_issuer.txt',
        student=student,
        doc=doc,
        issuer=issuer,
        issuer_dashboard_url=issuer_dashboard_url,
        brand=current_app.config.get('INSTITUTION_NAME', 'Satyameva'),
    )


def send_verification_alert_student(doc, student, verifier_label: str, method: str = 'HASH', timestamp = None) -> bool:
    """Notify the student that their credential was verified by an employer or QR scan."""
    email = getattr(getattr(student, 'user', None), 'email', None)
    if not email:
        return False

    try:
        dashboard_url = url_for('student.all_history', _external=True)
    except RuntimeError:
        dashboard_url = ''

    from extensions import utcnow
    ts = timestamp or utcnow()
    sender = current_app.config.get('MAIL_USERNAME', 'hackathonsage@gmail.com')

    return _send(
        subject=f'🛡️ Credential Verified: {doc.title} — Satyameva Alert',
        recipients=[email],
        html_template='email/credential_verified_student.html',
        txt_template='email/credential_verified_student.txt',
        student=student,
        doc=doc,
        verifier_label=verifier_label,
        method=method,
        timestamp=ts,
        dashboard_url=dashboard_url,
        sender_email=sender,
        brand=current_app.config.get('INSTITUTION_NAME', 'Satyameva'),
    )



def send_student_verification_email(student, verify_url: str) -> bool:
    """Send student an email with the verification link."""
    email = getattr(getattr(student, 'user', None), 'email', None)
    if not email:
        return False
    return _send(
        subject='Verify your student email — Satyameva',
        recipients=[email],
        html_template='email/email_verify_student.html',
        txt_template='email/email_verify_student.txt',
        student=student,
        verify_url=verify_url,
        brand=current_app.config.get('INSTITUTION_NAME', 'Satyameva'),
    )


def send_student_approved_email(student) -> bool:
    """Notify student that their account has been approved by the institution."""
    email = getattr(getattr(student, 'user', None), 'email', None)
    if not email:
        return False
    try:
        login_url = url_for('auth.login', _external=True)
    except RuntimeError:
        login_url = ''
    return _send(
        subject='Account Approved: Access your Satyameva Credentials',
        recipients=[email],
        html_template='email/student_approved.html',
        txt_template='email/student_approved.txt',
        student=student,
        login_url=login_url,
        brand=current_app.config.get('INSTITUTION_NAME', 'Satyameva'),
    )


def send_correction_request_notification(req, issuer_email: str) -> bool:
    """Alert the issuer that a student submitted a correction/re-issuance request."""
    if not issuer_email:
        return False
    try:
        requests_url = url_for('issuer.requests', _external=True)
    except RuntimeError:
        requests_url = ''
    return _send(
        subject=f'Credential {req.request_type.title()} Request: {req.student.full_name}',
        recipients=[issuer_email],
        html_template='email/correction_request_issuer.html',
        txt_template='email/correction_request_issuer.txt',
        req=req,
        requests_url=requests_url,
        brand=current_app.config.get('INSTITUTION_NAME', 'Satyameva'),
    )
