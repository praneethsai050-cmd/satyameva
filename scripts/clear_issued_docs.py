"""
scripts/clear_issued_docs.py
Clears all issued documents, verification logs, and resets the blockchain to Genesis (Block #0),
while preserving the clean 4 core production user accounts (Praneeth Sai @ JUIT, Registrar, Verifier, Admin)
and the Jaypee Institutions (JUIT, JIIT, JUET).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.document import Doc
from models.verification_log import VerificationLog
from models.notification import Notification
from models.block import Block
import blockchain

def clear_docs():
    app = create_app()
    with app.app_context():
        print("[1/3] Deleting verification logs and student notifications...")
        VerificationLog.query.delete()
        Notification.query.delete()
        
        print("[2/3] Deleting all issued documents...")
        Doc.query.delete()
        db.session.commit()

        print("[3/3] Resetting blockchain ledger to Genesis Block #0...")
        Block.query.delete()
        db.session.commit()

        chain_json = os.path.join(app.instance_path, 'blockchain.json')
        if os.path.exists(chain_json):
            os.remove(chain_json)

        blockchain.ensure_genesis_block()
        print("[OK] All issued documents removed! Blockchain ledger reset to Genesis Block #0.")
        print("Ready for live file upload & automatic Gemini OCR issuance via /issuer/issue.")

if __name__ == '__main__':
    clear_docs()
