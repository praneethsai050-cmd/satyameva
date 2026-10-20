"""Institution — a university or organisation that issues credentials.

Multi-institution support: each Issuer user belongs to one Institution.
The admin portal controls institution approval status.
"""
from extensions import db, utcnow


class Institution(db.Model):
    __tablename__ = 'institution'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    domain = db.Column(db.String(120), nullable=True)    # e.g. jiit.ac.in
    logo_url = db.Column(db.String(500), nullable=True)
    address = db.Column(db.String(300), nullable=True)

    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', use_alter=True, name='fk_institution_approved_by'),
        nullable=True,
    )

    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    # Subscription Management
    subscription_expires_at = db.Column(db.DateTime, nullable=True)   # None = lifetime / unconfigured
    subscription_plan = db.Column(db.String(50), default='annual', nullable=True)  # 'annual', 'trial', 'lifetime'

    # Relationships
    users = db.relationship(
        'User',
        foreign_keys='User.institution_id',
        back_populates='institution',
        lazy='select',
    )

    @property
    def issuer_count(self) -> int:
        from models.user import ROLE_ISSUER
        return sum(1 for u in self.users if u.role == ROLE_ISSUER)

    @property
    def status_label(self) -> str:
        return 'Approved' if self.is_approved else 'Pending'

    @property
    def status_class(self) -> str:
        return 'valid' if self.is_approved else 'revoked'

    @property
    def subscription_is_active(self) -> bool:
        if not self.is_approved:
            return False
        if self.subscription_expires_at is None:
            return True
        return utcnow() < self.subscription_expires_at

    @property
    def subscription_days_left(self) -> int | None:
        if self.subscription_expires_at is None:
            return None
        delta = (self.subscription_expires_at - utcnow()).days
        return max(0, delta)

    def __repr__(self) -> str:
        return f'<Institution {self.short_code} approved={self.is_approved}>'
