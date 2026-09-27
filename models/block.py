"""A persisted blockchain block."""
from extensions import db, utcnow


class Block(db.Model):
    __tablename__ = 'block'

    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, unique=True, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=utcnow, nullable=False)

    data = db.Column(db.Text, nullable=False)                  # canonical JSON payload
    proof = db.Column(db.Integer, nullable=False)              # PoW nonce
    previous_hash = db.Column(db.String(64), nullable=False)
    hash = db.Column(db.String(64), nullable=False, index=True)

    # Set for credential blocks; NULL for the genesis block.
    doc_hash = db.Column(db.String(64), nullable=True, index=True)

    # Cryptographic signature of block hash
    signature = db.Column(db.String(130), nullable=True)
    miner_public_key = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return f'<Block #{self.index} {self.hash[:12]}>'
