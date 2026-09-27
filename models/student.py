"""Student profile — the academic identity behind a student login."""
from extensions import db, utcnow


class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    full_name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    department = db.Column(db.String(120), nullable=True)
    program = db.Column(db.String(120), nullable=True)        # e.g. B.Tech CSE
    batch = db.Column(db.String(20), nullable=True)           # e.g. 2022-2026
    institution = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    user = db.relationship('User', back_populates='student')
    documents = db.relationship(
        'Doc',
        back_populates='student',
        order_by='Doc.issued_on.desc()',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f'<Student {self.roll_number} {self.full_name}>'
