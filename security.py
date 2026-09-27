"""
Cryptographic primitives for Satyameva.

Everything security-sensitive lives here so the routes stay thin:

  * PBKDF2-HMAC-SHA256 password hashing with a per-user 32-byte salt
  * Per-document salting, so two identical transcripts hash differently
    and a pre-computed rainbow table is worthless
  * HMAC-signed, time-boxed tokens for the dynamic QR codes
  * IPv4 + IPv6 client extraction for the verification audit trail
"""
import hashlib
import hmac
import ipaddress
import json
import os
import time

DEFAULT_ITERATIONS = 100_000


# ─── Passwords ────────────────────────────────────────────────────────────────
def generate_salt(nbytes: int = 32) -> str:
    """Fresh cryptographically-random salt, hex encoded."""
    return os.urandom(nbytes).hex()


def hash_password(password: str, iterations: int = DEFAULT_ITERATIONS) -> tuple[str, str, int]:
    """Hash a password. Returns (salt_hex, hash_hex, iterations)."""
    salt = os.urandom(32)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return salt.hex(), digest.hex(), iterations


def verify_password(password: str, salt_hex: str, hash_hex: str,
                    iterations: int = DEFAULT_ITERATIONS) -> bool:
    """Constant-time password check against a stored salt + hash."""
    try:
        salt = bytes.fromhex(salt_hex)
    except (TypeError, ValueError):
        return False
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return hmac.compare_digest(digest.hex(), hash_hex or '')


# ─── Document hashing ─────────────────────────────────────────────────────────
def canonical_payload(metadata: dict) -> str:
    """
    Deterministic JSON for hashing.

    Sorted keys and no whitespace mean the same metadata always produces
    byte-identical input, so the hash is reproducible at verify time.
    """
    return json.dumps(metadata, sort_keys=True, separators=(',', ':'), default=str)


def create_document_hash(file_bytes: bytes | None, metadata: dict, salt: str) -> str:
    """
    SHA-256 over  salt || sha256(file) || canonical(metadata).

    Binding the file digest and the metadata together means swapping either
    one invalidates the hash, which is what makes tampering detectable.
    """
    file_digest = hashlib.sha256(file_bytes).hexdigest() if file_bytes else 'no-file'
    material = f'{salt}|{file_digest}|{canonical_payload(metadata)}'
    return hashlib.sha256(material.encode('utf-8')).hexdigest()


def recompute_document_hash(doc) -> str:
    """Re-derive a stored document's hash from its own persisted payload."""
    file_digest = doc.file_digest or 'no-file'
    material = f'{doc.hash_salt}|{file_digest}|{doc.payload or ""}'
    return hashlib.sha256(material.encode('utf-8')).hexdigest()


def hashes_match(a: str, b: str) -> bool:
    """Constant-time hash comparison."""
    return hmac.compare_digest(a or '', b or '')


# ─── Dynamic QR tokens ────────────────────────────────────────────────────────
def make_qr_token(doc_hash: str, secret: str, ttl: int = 60) -> tuple[str, int]:
    """
    Build a short-lived HMAC token for a QR code.

    Returns (token, expires_at_epoch). The token is `expiry.signature`, so a
    screenshot of the QR stops verifying once the clock passes the expiry —
    that is what defeats replay of a shared image.
    """
    expires_at = int(time.time()) + ttl
    signature = hmac.new(
        secret.encode('utf-8'),
        f'{doc_hash}|{expires_at}'.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()[:32]
    return f'{expires_at}.{signature}', expires_at


def check_qr_token(doc_hash: str, token: str, secret: str) -> tuple[bool, str]:
    """
    Validate a QR token. Returns (ok, reason).

    Reason is one of 'ok', 'malformed', 'expired', 'bad-signature' so the
    caller can show the verifier something useful.
    """
    if not token or '.' not in token:
        return False, 'malformed'
    expiry_str, signature = token.rsplit('.', 1)
    try:
        expires_at = int(expiry_str)
    except (TypeError, ValueError):
        return False, 'malformed'

    expected = hmac.new(
        secret.encode('utf-8'),
        f'{doc_hash}|{expires_at}'.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()[:32]
    if not hmac.compare_digest(expected, signature):
        return False, 'bad-signature'
    if time.time() > expires_at:
        return False, 'expired'
    return True, 'ok'


# ─── Client IP capture ────────────────────────────────────────────────────────
def get_client_ips(req, trust_proxy: bool = False) -> tuple[str, str]:
    """
    Best-effort (ipv4, ipv6) for the requesting client.

    X-Forwarded-For is only consulted when `trust_proxy` is on, because a
    client can forge that header when Flask is exposed directly.
    """
    ipv4, ipv6 = 'N/A', 'N/A'

    candidates: list[str] = []
    if trust_proxy:
        forwarded = req.headers.get('X-Forwarded-For', '')
        candidates += [part.strip() for part in forwarded.split(',') if part.strip()]
    if req.remote_addr:
        candidates.append(req.remote_addr)

    for candidate in candidates:
        try:
            address = ipaddress.ip_address(candidate.strip().strip('[]'))
        except ValueError:
            continue
        if address.version == 4 and ipv4 == 'N/A':
            ipv4 = str(address)
        elif address.version == 6 and ipv6 == 'N/A':
            ipv6 = str(address)
            # ::ffff:127.0.0.1 style addresses also give us the v4 form.
            if address.ipv4_mapped and ipv4 == 'N/A':
                ipv4 = str(address.ipv4_mapped)

    return ipv4, ipv6


# ─── Display helpers ──────────────────────────────────────────────────────────
def truncate_hash(value: str, head: int = 10, tail: int = 8) -> str:
    """`a1b2c3d4e5…f6g7h8i9` — for stamps and cramped table cells."""
    if not value or len(value) <= head + tail + 1:
        return value or ''
    return f'{value[:head]}…{value[-tail:]}'


def visual_hash_swatches(value: str, count: int = 5) -> list[str]:
    """
    Turn a hash into a row of colour swatches.

    A human can eyeball two colour strips and spot a mismatch far faster
    than they can diff 64 hex characters.
    """
    if not value:
        return []
    swatches = []
    for i in range(count):
        chunk = value[i * 6:(i + 1) * 6]
        swatches.append(f'#{chunk.ljust(6, "0")}')
    return swatches


# ─── Asymmetric Digital Signatures (secp256k1) ────────────────────────────────
# Standard parameters matching Bitcoin/Ethereum secp256k1
_SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_SECP_GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_SECP_GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
_SECP_G = (_SECP_GX, _SECP_GY)


def _ec_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if (y1 + y2) % _SECP_P == 0:
            return None
        m = (3 * x1 * x1 * pow(2 * y1, -1, _SECP_P)) % _SECP_P
    else:
        m = ((y2 - y1) * pow(x2 - x1, -1, _SECP_P)) % _SECP_P
    x3 = (m * m - x1 - x2) % _SECP_P
    y3 = (m * (x1 - x3) - y1) % _SECP_P
    return (x3, y3)


def _ec_mul(k, p):
    res = None
    curr = p
    while k > 0:
        if k & 1:
            res = _ec_add(res, curr)
        curr = _ec_add(curr, curr)
        k >>= 1
    return res


def generate_asymmetric_keypair() -> tuple[str, str]:
    """
    Generate an asymmetric secp256k1 keypair for an issuer.
    Returns (private_key_hex, public_key_hex).
    """
    import secrets
    d = secrets.randbelow(_SECP_N - 2) + 1
    q = _ec_mul(d, _SECP_G)
    pub_hex = f'{q[0]:064x}{q[1]:064x}'
    return f'{d:064x}', pub_hex


def sign_payload(private_key_hex: str, message: str | bytes) -> str:
    """
    Sign a message using deterministic Schnorr signature on secp256k1.
    Returns a 128-character hex signature (R.x || s).
    """
    if isinstance(message, str):
        msg_bytes = message.encode('utf-8')
    else:
        msg_bytes = message

    d = int(private_key_hex, 16) % _SECP_N
    # Deterministic nonce k = SHA256(d || message)
    k_digest = hashlib.sha256(f'{d:064x}'.encode('utf-8') + msg_bytes).hexdigest()
    k = (int(k_digest, 16) % (_SECP_N - 1)) + 1
    r_point = _ec_mul(k, _SECP_G)
    rx = r_point[0]

    q = _ec_mul(d, _SECP_G)
    qx = q[0]

    # e = SHA256(R.x || Q.x || message)
    e_digest = hashlib.sha256(f'{rx:064x}{qx:064x}'.encode('utf-8') + msg_bytes).hexdigest()
    e = int(e_digest, 16) % _SECP_N

    s = (k + e * d) % _SECP_N
    return f'{rx:064x}{s:064x}'


def verify_signature(public_key_hex: str, message: str | bytes, signature_hex: str) -> bool:
    """
    Verify a secp256k1 Schnorr signature.
    """
    try:
        if not public_key_hex or len(public_key_hex) != 128 or not signature_hex or len(signature_hex) != 128:
            return False

        if isinstance(message, str):
            msg_bytes = message.encode('utf-8')
        else:
            msg_bytes = message

        qx = int(public_key_hex[:64], 16)
        qy = int(public_key_hex[64:], 16)
        q = (qx, qy)

        rx = int(signature_hex[:64], 16)
        s = int(signature_hex[64:], 16)

        if s >= _SECP_N:
            return False

        e_digest = hashlib.sha256(f'{rx:064x}{qx:064x}'.encode('utf-8') + msg_bytes).hexdigest()
        e = int(e_digest, 16) % _SECP_N

        # Compute s*G - e*Q
        sg = _ec_mul(s, _SECP_G)
        minus_eq = _ec_mul((_SECP_N - e) % _SECP_N, q)
        r_calc = _ec_add(sg, minus_eq)

        if r_calc is None:
            return False

        return r_calc[0] == rx
    except Exception:
        return False

