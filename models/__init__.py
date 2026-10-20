"""Model package — importing this registers every table with SQLAlchemy."""
from models.block import Block
from models.credential_request import CredentialRequest
from models.document import Doc
from models.fraud_report import FraudReport
from models.institution import Institution
from models.notification import Notification
from models.student import Student
from models.user import User
from models.verification_log import VerificationLog

# Compatibility aliases
Document = Doc
Issuer = User
Verifier = User

__all__ = [
    'User',
    'Student',
    'Doc',
    'Document',
    'Issuer',
    'Verifier',
    'Block',
    'VerificationLog',
    'FraudReport',
    'Notification',
    'Institution',
    'CredentialRequest',
]
