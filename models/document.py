"""
An issued academic credential.

Named `Doc` (not `Document`) to avoid shadowing the DOM-ish naming used
throughout the templates, and to match the project's original schema notes.
"""
from datetime import timedelta

from extensions import db, utcnow

# doc_type -> (label, emoji, default validity in days)
#
# Validity mirrors real Indian academic practice: a transfer certificate is a
# short-lived instrument, a degree is effectively permanent.
DOC_TYPES = {
    'DEGREE':     ('Degree Certificate',     '🎓', 3650),
    'MARKSHEET':  ('Marksheet',              '📊', 3650),
    'TC':         ('Transfer Certificate',   '📄', 180),
    'MIGRATION':  ('Migration Certificate',  '✈️', 365),
    'BONAFIDE':   ('Bonafide Certificate',   '🏛️', 90),
    'INTERNSHIP': ('Internship Certificate', '💼', 730),
}

STATUS_VALID = 'VALID'
STATUS_EXPIRING = 'EXPIRING'
STATUS_EXPIRED = 'EXPIRED'
STATUS_REVOKED = 'REVOKED'


def default_validity_days(doc_type: str) -> int:
    return DOC_TYPES.get((doc_type or '').upper(), (None, None, 365))[2]


class Doc(db.Model):
    __tablename__ = 'doc'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    issuer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    doc_type = db.Column(db.String(30), nullable=False, default='DEGREE')
    title = db.Column(db.String(160), nullable=False)
    issuer_name = db.Column(db.String(150), nullable=True)     # denormalised for display

    # ---- Integrity ----
    doc_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    hash_salt = db.Column(db.String(64), nullable=False)
    file_digest = db.Column(db.String(64), nullable=True)      # sha256 of raw file bytes
    payload = db.Column(db.Text, nullable=True)                # canonical metadata JSON

    # ---- File ----
    file_data = db.Column(db.LargeBinary, nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_mime = db.Column(db.String(100), nullable=True)

    # ---- Lifecycle ----
    issued_on = db.Column(db.DateTime, default=utcnow, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=True)        # NULL == never expires

    # ---- Digital stamp ----
    is_stamped = db.Column(db.Boolean, default=False, nullable=False)
    stamp_date = db.Column(db.DateTime, nullable=True)
    stamped_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # ---- Blockchain anchor ----
    block_index = db.Column(db.Integer, nullable=True)
    tx_hash = db.Column(db.String(80), nullable=True)

    # ---- Cryptographic Signature ----
    signature = db.Column(db.String(130), nullable=True)        # ECDSA signature of doc_hash
    issuer_public_key = db.Column(db.Text, nullable=True)       # Issuer's public key

    # ---- Audit / fraud ----
    verification_count = db.Column(db.Integer, default=0, nullable=False)
    last_verified_at = db.Column(db.DateTime, nullable=True)
    revoked = db.Column(db.Boolean, default=False, nullable=False)
    revoked_reason = db.Column(db.String(255), nullable=True)

    student = db.relationship('Student', back_populates='documents')
    issuer = db.relationship('User', foreign_keys=[issuer_id])
    stamper = db.relationship('User', foreign_keys=[stamped_by])
    logs = db.relationship(
        'VerificationLog',
        back_populates='doc',
        order_by='VerificationLog.timestamp.desc()',
        cascade='all, delete-orphan',
    )

    # ---- Presentation helpers ----
    @property
    def type_label(self) -> str:
        return DOC_TYPES.get(self.doc_type, (self.doc_type, '📄', 365))[0]

    @property
    def type_icon(self) -> str:
        return DOC_TYPES.get(self.doc_type, (self.doc_type, '📄', 365))[1]

    @property
    def days_left(self) -> int | None:
        """Whole days until expiry; None when the credential never expires."""
        if self.valid_until is None:
            return None
        return (self.valid_until - utcnow()).days

    @property
    def status(self) -> str:
        if self.revoked:
            return STATUS_REVOKED
        if self.valid_until is None:
            return STATUS_VALID
        remaining = self.days_left
        if remaining is not None and remaining < 0:
            return STATUS_EXPIRED
        if remaining is not None and remaining <= 30:
            return STATUS_EXPIRING
        return STATUS_VALID

    @property
    def status_label(self) -> str:
        return {
            STATUS_VALID: 'Valid',
            STATUS_EXPIRING: 'Expiring Soon',
            STATUS_EXPIRED: 'Expired',
            STATUS_REVOKED: 'Revoked',
        }[self.status]

    @property
    def status_class(self) -> str:
        """CSS modifier suffix used by the badge / ring styles."""
        return self.status.lower()

    @property
    def is_valid(self) -> bool:
        return self.status in (STATUS_VALID, STATUS_EXPIRING)

    @property
    def lifetime_percent(self) -> int:
        """
        How much of the credential's life is still ahead, 0-100.

        Drives the progress ring on each document card.
        """
        if self.valid_until is None:
            return 100
        total = (self.valid_until - self.issued_on).total_seconds()
        if total <= 0:
            return 0
        remaining = (self.valid_until - utcnow()).total_seconds()
        return max(0, min(100, round(remaining / total * 100)))

    @property
    def is_previewable_image(self) -> bool:
        return bool(self.file_mime and self.file_mime.startswith('image/'))

    @property
    def is_pdf(self) -> bool:
        return self.file_mime == 'application/pdf'

    def set_validity(self, days: int | None = None) -> None:
        """Apply the type's default validity window unless told otherwise."""
        if days is None:
            days = default_validity_days(self.doc_type)
        self.valid_until = (self.issued_on or utcnow()) + timedelta(days=days)

    def __repr__(self) -> str:
        return f'<Doc {self.doc_type} {self.doc_hash[:12]} ({self.status})>'
