"""
Credential issuance.

Kept as a service rather than inline in a route so that the hash, the stored
payload and the blockchain anchor are always produced together — the three
have to agree or `verify_hash` will (correctly) report tampering.
"""
import hashlib
import uuid

from blockchain import mine_block
from extensions import db, utcnow
from models.document import Doc, default_validity_days
from security import canonical_payload, create_document_hash, generate_salt


def issue_credential(student, issuer, doc_type, title, *, file_bytes=None,
                     file_name=None, file_mime=None, validity_days=None,
                     issued_on=None, extra=None, difficulty=4) -> Doc:
    """
    Mint a credential: hash it, anchor it on the chain, persist it.

    `extra` merges issuer-specific fields (CGPA, division, …) into the hashed
    payload, so they are covered by the integrity check too.
    """
    issued_on = issued_on or utcnow()
    salt = generate_salt(16)

    metadata = {
        'student_name': student.full_name,
        'roll_number': student.roll_number,
        'program': student.program,
        'department': student.department,
        'institution': student.institution,
        'doc_type': doc_type,
        'title': title,
        'issuer': getattr(issuer, 'organization', None) or getattr(issuer, 'username', None),
        'issued_on': issued_on.isoformat(),
    }
    if extra:
        metadata.update(extra)

    payload = canonical_payload(metadata)
    file_digest = hashlib.sha256(file_bytes).hexdigest() if file_bytes else None
    doc_hash = create_document_hash(file_bytes, metadata, salt)

    # Asymmetric cryptographic signature (ECDSA secp256k1)
    priv_key, pub_key = None, None
    if hasattr(issuer, 'ensure_crypto_keys'):
        try:
            priv_key, pub_key = issuer.ensure_crypto_keys()
        except Exception:
            pass

    signature = None
    if priv_key:
        try:
            from services.crypto_service import sign_hash
            signature = sign_hash(priv_key, doc_hash)
        except Exception:
            signature = None

    doc = Doc(
        student_id=student.id,
        issuer_id=getattr(issuer, 'id', None),
        doc_type=doc_type,
        title=title,
        issuer_name=metadata['issuer'],
        doc_hash=doc_hash,
        hash_salt=salt,
        file_digest=file_digest,
        payload=payload,
        file_data=file_bytes,
        file_name=file_name,
        file_mime=file_mime,
        issued_on=issued_on,
        tx_hash='0x' + uuid.uuid4().hex,
        signature=signature,
        issuer_public_key=pub_key,
    )
    doc.set_validity(validity_days if validity_days is not None
                     else default_validity_days(doc_type))

    db.session.add(doc)
    db.session.flush()          # need doc.id before anchoring

    block = mine_block(
        {
            'doc_hash': doc_hash,
            'doc_type': doc_type,
            'roll_number': student.roll_number,
            'issuer': metadata['issuer'],
            'issued_on': issued_on.isoformat(),
            'valid_until': doc.valid_until.isoformat() if doc.valid_until else None,
            'signature': signature,
            'issuer_public_key': pub_key,
        },
        doc_hash=doc_hash,
        difficulty=difficulty,
        private_key=priv_key,
        public_key=pub_key,
    )
    doc.block_index = block.index
    db.session.commit()

    # ---- Email notifications (fire-and-forget; failures are logged, never raised) ----
    try:
        from services.email_service import (
            send_credential_issued_issuer,
            send_credential_issued_student,
        )
        send_credential_issued_student(doc, student)
        send_credential_issued_issuer(doc, student, issuer)
    except Exception:  # noqa: BLE001
        pass  # email import itself should not break credential issuance

    return doc
