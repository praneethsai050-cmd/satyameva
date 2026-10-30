"""
Email notification helpers for Satyameva.

Two fire-and-forget helpers -- any SMTP failure is caught, logged,
and the caller's main action (credential issuance) is never blocked.
Includes strict safety guards to NEVER dispatch emails to official
university domains (e.g. JUIT, JIIT, JUET) or administrative inboxes.
"""
import logging

from flask import current_app, render_template, url_for
from flask_mail import Message

from extensions import mail

logger = logging.getLogger(__name__)

# Prohibited official domains & authorities: Under no circumstances send emails
# to actual university administrative inboxes, official registrars, or institutional domains.
BLOCKED_OFFICIAL_DOMAINS = (
    'juit.ac.in',
    'jiit.ac.in',
    'juet.ac.in',
    'jaypee.edu',
    'mail.juit.ac.in',
    'mail.jiit.ac.in',
    'mail.juet.ac.in',
)

BLOCKED_OFFICIAL_USERNAMES = (
    'registrar',
    'vc',
    'vice-chancellor',
    'vicechancellor',
    'dean',
    'coe',
    'provost',
    'director',
    'examcell',
    'examination',
    'admissions',
    'admin',
)


def _is_valid_email(email: str) -> bool:
    """Ensure recipient email matches valid syntax without invalid domain characters like underscores."""
    if not email or '@' not in email:
        return False
    user_part, domain_part = email.split('@', 1)
    if not domain_part or '.' not in domain_part or '_' in domain_part:
        return False
    return True


def _is_allowed_recipient(email: str) -> bool:
    """
    Ensure recipient email is syntactically valid and strictly blocked from sending
    to any official JUIT, JIIT, JUET, Jaypee branch, or official university authorities.
    """
    if not _is_valid_email(email):
        return False

    email_lower = email.strip().lower()
    user_part, domain_part = email_lower.split('@', 1)

    # 1. Strictly block any official Jaypee university domain
    for blocked_domain in BLOCKED_OFFICIAL_DOMAINS:
        if domain_part == blocked_domain or domain_part.endswith('.' + blocked_domain):
            logger.warning('SAFETY FILTER: Blocked email dispatch to official university domain: %s', email)
            return False

    # 2. Block any official university role/inbox (e.g. registrar@..., dean@..., vc@...)
    for blocked_role in BLOCKED_OFFICIAL_USERNAMES:
        if user_part == blocked_role or user_part.startswith(blocked_role + '.') or user_part.startswith(blocked_role + '_'):
            logger.warning('SAFETY FILTER: Blocked email dispatch to official university role: %s', email)
            return False

    # 3. Disallow dummy / internal mock domains from attempting real SMTP dispatch
    if domain_part.endswith('.local') or domain_part.endswith('.internal') or domain_part.endswith('.test'):
        logger.info('Skipping local/test domain recipient: %s', email)
        return False

    return True


def _send(subject: str, recipients: list, html_template: str,
          txt_template: str, **ctx) -> bool:
    """Render and dispatch a multipart email asynchronously in the background."""
    if not recipients:
        return False

    valid_recipients = [r for r in recipients if _is_allowed_recipient(r)]
    if not valid_recipients:
        logger.info('Skipping email "%s": no allowed external recipients in %s', subject, recipients)
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
                logger.error('Background email "%s" to %s failed: %s', subject, valid_recipients, exc)

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
    """
    Send the issuer a confirmation that their credential was anchored on-chain.
    NOTE: Automatically suppressed for university registrars and official accounts
    to prevent sending unnecessary or unintended emails to university staff.
    """
    email = getattr(issuer, 'email', None)
    if not email or not _is_allowed_recipient(email):
        logger.info('Suppressed credential issued email to issuer/registrar: %s', email)
        return True

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
    if not issuer_email or not _is_allowed_recipient(issuer_email):
        logger.info('Suppressed correction request email to official/restricted issuer %s', issuer_email)
        return True
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
