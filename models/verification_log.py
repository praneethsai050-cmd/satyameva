"""
One row per verification attempt.

Written for anonymous verifiers too (verifier_id NULL), because the point of
the log is to let a student see *that* their credential was checked — from
where and with what outcome — not only when the checker happened to have an
account.
"""
from extensions import db, utcnow

RESULT_VALID = 'VALID'
RESULT_EXPIRED = 'EXPIRED'
RESULT_NOT_FOUND = 'NOT_FOUND'
RESULT_REVOKED = 'REVOKED'
RESULT_TAMPERED = 'TAMPERED'
RESULT_QR_EXPIRED = 'QR_EXPIRED'


class VerificationLog(db.Model):
    __tablename__ = 'verification_log'

    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('doc.id'), nullable=True, index=True)
    verifier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    #: Free-text label for anonymous checks, e.g. "Anonymous (QR scan)".
    verifier_label = db.Column(db.String(150), nullable=True)
    queried_hash = db.Column(db.String(64), nullable=True)

    timestamp = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    ipv4 = db.Column(db.String(45), nullable=True)
    ipv6 = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    method = db.Column(db.String(20), nullable=True)           # 'QR' | 'HASH'
    result = db.Column(db.String(20), nullable=False, default=RESULT_VALID)

    doc = db.relationship('Doc', back_populates='logs')
    verifier = db.relationship('User', foreign_keys=[verifier_id])

    @property
    def who(self) -> str:
        if self.verifier:
            org = self.verifier.organization
            return f'{self.verifier.username}' + (f' · {org}' if org else '')
        return self.verifier_label or 'Anonymous verifier'

    @property
    def result_class(self) -> str:
        return {
            RESULT_VALID: 'valid',
            RESULT_EXPIRED: 'expired',
            RESULT_REVOKED: 'revoked',
            RESULT_NOT_FOUND: 'expired',
            RESULT_TAMPERED: 'revoked',
            RESULT_QR_EXPIRED: 'expiring',
        }.get(self.result, 'valid')

    @property
    def result_icon(self) -> str:
        return {
            RESULT_VALID: '✅',
            RESULT_EXPIRED: '⚠️',
            RESULT_REVOKED: '🚫',
            RESULT_NOT_FOUND: '❌',
            RESULT_TAMPERED: '🛑',
            RESULT_QR_EXPIRED: '⏱️',
        }.get(self.result, '•')

    def __repr__(self) -> str:
        return f'<VerificationLog doc={self.doc_id} {self.result}>'
