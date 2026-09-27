from extensions import db, utcnow

class FraudReport(db.Model):
    __tablename__ = 'fraud_report'

    id = db.Column(db.Integer, primary_key=True)
    doc_hash = db.Column(db.String(64), nullable=False, index=True)
    verifier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=utcnow, nullable=False)
    
    verifier = db.relationship('User')
