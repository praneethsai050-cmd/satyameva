"""
Notification model for student alerts and verifications.
"""
from extensions import db, utcnow


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('doc.id'), nullable=True, index=True)

    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(30), default='info', nullable=False)  # info, success, warning, danger
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    verifier_label = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)

    student = db.relationship('Student', backref=db.backref('notifications_list', lazy='dynamic', cascade='all, delete-orphan'))
    doc = db.relationship('Doc', backref=db.backref('notifications', lazy='dynamic', cascade='all, delete-orphan'))

    @property
    def icon(self) -> str:
        return {
            'success': '✅',
            'info': '🔍',
            'warning': '⏳',
            'danger': '🚫',
        }.get(self.category, '🔔')

    def __repr__(self) -> str:
        return f'<Notification {self.id} student={self.student_id} title="{self.title}">'
