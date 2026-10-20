"""User account + role-based access control."""
from flask_login import UserMixin

from extensions import db, login_manager, utcnow

ROLE_STUDENT = 'student'
ROLE_ISSUER = 'issuer'
ROLE_VERIFIER = 'verifier'
ROLE_ADMIN = 'admin'

ROLES = (ROLE_STUDENT, ROLE_ISSUER, ROLE_VERIFIER, ROLE_ADMIN)

#: Where each role lands after signing in.
ROLE_HOME = {
    ROLE_STUDENT: 'student.dashboard',
    ROLE_ISSUER: 'issuer.dashboard',
    ROLE_VERIFIER: 'verifier.dashboard',
    ROLE_ADMIN: 'admin.dashboard',
}


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(128), nullable=False)
    password_salt = db.Column(db.String(64), nullable=False)
    password_iterations = db.Column(db.Integer, nullable=False, default=100_000)

    role = db.Column(db.String(20), nullable=False, default=ROLE_STUDENT, index=True)
    organization = db.Column(db.String(150), nullable=True)   # university / employer
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    # OAuth fields (populated when user signs in via Google/Microsoft)
    oauth_provider = db.Column(db.String(30), nullable=True)   # 'google' | 'microsoft'
    oauth_sub = db.Column(db.String(256), nullable=True)       # provider's subject/oid
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Asymmetric cryptographic keypair (ECDSA secp256k1)
    public_key = db.Column(db.Text, nullable=True)
    private_key = db.Column(db.Text, nullable=True)

    student = db.relationship('Student', foreign_keys='Student.user_id', back_populates='user', uselist=False)
    institution = db.relationship(
        'Institution',
        foreign_keys=[institution_id],
        back_populates='users',
    )

    def ensure_crypto_keys(self) -> tuple[str, str]:
        """Ensure this user (especially an issuer) has an asymmetric cryptographic keypair."""
        if not self.public_key or not self.private_key:
            from services.crypto_service import generate_keypair
            self.private_key, self.public_key = generate_keypair()
        return self.private_key, self.public_key

    # ---- Convenience ----
    @property
    def is_student(self) -> bool:
        return self.role == ROLE_STUDENT

    @property
    def is_issuer(self) -> bool:
        return self.role == ROLE_ISSUER

    @property
    def is_verifier(self) -> bool:
        return self.role == ROLE_VERIFIER

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    @property
    def display_name(self) -> str:
        """Prefer the student's real name over the login handle."""
        if self.student and self.student.full_name:
            return self.student.full_name
        return self.username

    @property
    def initials(self) -> str:
        parts = [p for p in self.display_name.replace('.', ' ').split() if p]
        if not parts:
            return '?'
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    def home_endpoint(self) -> str:
        return ROLE_HOME.get(self.role, 'student.dashboard')

    def __repr__(self) -> str:
        return f'<User {self.username} ({self.role})>'


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
