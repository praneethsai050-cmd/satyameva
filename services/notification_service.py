"""
Notification service for student alerts and verifications.
"""
from models.document import STATUS_EXPIRED, STATUS_EXPIRING, STATUS_REVOKED
from models.notification import Notification


def build_notifications(student, documents, warning_days: int = 30) -> list[dict]:
    """
    Build a comprehensive, sorted alert list for the student.

    Includes:
    1. Critical document status alerts (Revoked, Expired, Expiring soon).
    2. Real-time verification events logged in the Notification table.
    """
    alerts: list[dict] = []

    # 1. Document status alerts
    for doc in documents:
        status = doc.status
        days = doc.days_left

        if status == STATUS_REVOKED:
            alerts.append({
                'id': f'doc-revoked-{doc.id}',
                'level': 'danger', 'icon': '🚫', 'priority': 0, 'doc': doc,
                'title': f'{doc.type_label} revoked',
                'body': doc.revoked_reason or 'The issuing institution revoked this credential.',
                'action': 'Contact your institution',
                'created_at': doc.issued_on,
            })
        elif status == STATUS_EXPIRED:
            alerts.append({
                'id': f'doc-expired-{doc.id}',
                'level': 'danger', 'icon': '⛔', 'priority': 1, 'doc': doc,
                'title': f'{doc.type_label} has expired',
                'body': f'Expired {abs(days)} day{"s" if abs(days) != 1 else ""} ago on '
                        f'{doc.valid_until.strftime("%d %b %Y") if doc.valid_until else "—"}. Verifiers will see it as expired.',
                'action': 'Request a renewal',
                'created_at': doc.valid_until or doc.issued_on,
            })
        elif status == STATUS_EXPIRING:
            alerts.append({
                'id': f'doc-expiring-{doc.id}',
                'level': 'warning', 'icon': '⏳', 'priority': 2, 'doc': doc,
                'title': f'{doc.type_label} expires in {days} day{"s" if days != 1 else ""}',
                'body': f'Valid until {doc.valid_until.strftime("%d %b %Y") if doc.valid_until else "—"}. '
                        f'Renew before then to keep sharing it.',
                'action': 'Request a renewal',
                'created_at': doc.issued_on,
            })

    # 2. Stored verification notifications
    if student:
        db_notifs = Notification.query.filter_by(student_id=student.id).order_by(Notification.created_at.desc()).all()
        for notif in db_notifs:
            alerts.append({
                'id': f'notif-{notif.id}',
                'db_id': notif.id,
                'level': notif.category or 'info',
                'icon': notif.icon,
                'priority': 3,
                'doc': notif.doc,
                'title': notif.title,
                'body': notif.message,
                'action': 'View history' if notif.doc else 'View details',
                'is_read': notif.is_read,
                'created_at': notif.created_at,
            })

    alerts.sort(key=lambda a: (a['priority'], -(a.get('created_at').timestamp() if a.get('created_at') else 0)))
    return alerts


def unread_count(student, documents, warning_days: int = 30) -> int:
    """Badge count — unread database notifications plus actionable document states."""
    doc_alerts = sum(
        1 for doc in documents
        if doc.status in (STATUS_EXPIRED, STATUS_EXPIRING, STATUS_REVOKED)
    )
    db_unread = 0
    if student:
        db_unread = Notification.query.filter_by(student_id=student.id, is_read=False).count()
    return doc_alerts + db_unread
