"""
Asymmetric cryptographic primitives for Satyameva.

Implements ECDSA over the secp256k1 elliptic curve using Python's standard
library (secrets, hashlib, math) — completely self-contained with no external
C-extension or package dependencies.

Used for:
  * Issuers signing academic credentials with private key
  * Verifiers verifying credentials with the issuer's public key
  * Miners/nodes signing newly mined blockchain blocks
"""
import hashlib
import secrets

# secp256k1 curve parameters (standard Bitcoin / Ethereum curve)
_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_A = 0
_B = 7
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
_G = (_Gx, _Gy)
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def _inv(a: int, m: int = _P) -> int:
    return pow(a, -1, m)


def _point_add(p1: tuple[int, int] | None, p2: tuple[int, int] | None) -> tuple[int, int] | None:
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 != y2:
        return None
    if x1 == x2:
        m = (3 * x1 * x1 + _A) * _inv(2 * y1, _P) % _P
    else:
        m = (y2 - y1) * _inv(x2 - x1, _P) % _P
    x3 = (m * m - x1 - x2) % _P
    y3 = (m * (x1 - x3) - y1) % _P
    return (x3, y3)


def _point_mul(k: int, p: tuple[int, int]) -> tuple[int, int] | None:
    res = None
    cur = p
    while k > 0:
        if k & 1:
            res = _point_add(res, cur)
        cur = _point_add(cur, cur)
        k >>= 1
    return res


def generate_keypair() -> tuple[str, str]:
    """
    Generate a new ECDSA secp256k1 keypair.
    Returns (private_key_hex, public_key_hex).
    - private_key: 64 hex characters (32 bytes)
    - public_key: 130 hex characters uncompressed format '04' + X + Y
    """
    priv = secrets.randbelow(_N - 1) + 1
    pub_point = _point_mul(priv, _G)
    if pub_point is None:
        return generate_keypair()
    x, y = pub_point
    pub_hex = f"04{x:064x}{y:064x}"
    priv_hex = f"{priv:064x}"
    return priv_hex, pub_hex


def sign_hash(private_key_hex: str, hash_hex: str) -> str:
    """
    Sign a 32-byte hex hash using the private key.
    Returns a 128-hex-character signature (r: 64 hex, s: 64 hex).
    """
    priv = int(private_key_hex, 16)
    z = int(hash_hex, 16)
    while True:
        k = secrets.randbelow(_N - 1) + 1
        rx_point = _point_mul(k, _G)
        if rx_point is None:
            continue
        rx, _ = rx_point
        r = rx % _N
        if r == 0:
            continue
        s = (_inv(k, _N) * (z + r * priv)) % _N
        if s == 0:
            continue
        return f"{r:064x}{s:064x}"


def sign_message(private_key_hex: str, message: str | bytes) -> str:
    """Convenience helper to sign any message (computes SHA-256 first)."""
    if isinstance(message, str):
        message = message.encode('utf-8')
    h = hashlib.sha256(message).hexdigest()
    return sign_hash(private_key_hex, h)


def verify_signature(public_key_hex: str, hash_hex: str, signature_hex: str) -> bool:
    """
    Verify an ECDSA secp256k1 signature against a public key and hash.
    Returns True if valid, False otherwise.
    """
    try:
        if not public_key_hex or not hash_hex or not signature_hex:
            return False
        if len(signature_hex) != 128:
            return False

        r = int(signature_hex[:64], 16)
        s = int(signature_hex[64:], 16)
        if not (1 <= r < _N and 1 <= s < _N):
            return False

        if public_key_hex.startswith('04') and len(public_key_hex) == 130:
            px = int(public_key_hex[2:66], 16)
            py = int(public_key_hex[66:], 16)
        else:
            return False

        pub = (px, py)
        z = int(hash_hex, 16)
        w = _inv(s, _N)
        u1 = (z * w) % _N
        u2 = (r * w) % _N

        point = _point_add(_point_mul(u1, _G), _point_mul(u2, pub))
        if point is None:
            return False
        return (point[0] % _N) == r
    except Exception:
        return False


# Alias for explicit naming
verify_hash_signature = verify_signature

