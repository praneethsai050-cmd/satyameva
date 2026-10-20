"""CredentialRequest — student requests for credential correction or re-issuance."""
from extensions import db, utcnow


class CredentialRequest(db.Model):
    __tablename__ = 'credential_request'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('doc.id'), nullable=True)

    request_type = db.Column(db.String(30), nullable=False, default='correction')  # 'correction' | 'reissuance'
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending' | 'approved' | 'rejected'

    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolver_note = db.Column(db.Text, nullable=True)

    student = db.relationship('Student', backref=db.backref('credential_requests', cascade='all, delete-orphan', order_by='CredentialRequest.created_at.desc()'))
    doc = db.relationship('Doc', backref=db.backref('requests', cascade='all, delete-orphan'), foreign_keys=[doc_id])
    resolver = db.relationship('User', foreign_keys=[resolved_by_id])

    @property
    def status_badge_class(self) -> str:
        if self.status == 'approved':
            return 'valid'
        elif self.status == 'rejected':
            return 'revoked'
        return 'expiring'

    def __repr__(self) -> str:
        return f'<CredentialRequest {self.id} student={self.student_id} status={self.status}>'
