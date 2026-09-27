"""
QR code rendering with Institutional Jaypee Branding.

QR payloads are always a full verification URL carrying a time-boxed token,
so a verifier only has to point a phone camera at the screen — no typing a
64-character hash, and a stale screenshot stops working once the token ages
out (see `security.make_qr_token`).

Features:
- High Error Correction (Level H ~30%) ensures instant camera scan resilience.
- Cyber Navy (#0b102b) on Crisp White (#ffffff) modules for high-contrast scanning.
- Dynamic Central Campus Crests (JIIT, JUIT, JUET, AEGIS) embedded with anti-aliasing
  and isolation buffer.
"""
import base64
from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_H

from services.crest_service import get_campus_crest


def qr_png_bytes(payload: str, campus_code: str | None = None, box_size: int = 10, border: int = 2,
                 fill: str = '#0b102b', back: str = '#ffffff', embed_crest: bool = True) -> bytes:
    """
    Render `payload` as a branded PNG with institutional central crest.

    High error correction (~30%) keeps the code scannable even when it is
    printed small, photographed off a screen at an angle, or partially occluded
    by the central institutional emblem.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    image = qr.make_image(fill_color=fill, back_color=back).convert('RGBA')

    if embed_crest:
        # Emblem size: ~22% of total QR dimension (covers under ~5% area, well within 30% Level H tolerance)
        crest_size = int(image.width * 0.23)
        # Ensure crest_size is even for pixel-perfect centering
        if crest_size % 2 != 0:
            crest_size += 1

        crest = get_campus_crest(campus_code, size=crest_size)
        pos = ((image.width - crest.width) // 2, (image.height - crest.height) // 2)
        image.paste(crest, pos, crest)

    final_image = image.convert('RGB')
    buffer = BytesIO()
    final_image.save(buffer, format='PNG')
    return buffer.getvalue()


def qr_data_uri(payload: str, campus_code: str | None = None, **kwargs) -> str:
    """Inline-able `data:` URI with embedded institutional branding."""
    encoded = base64.b64encode(qr_png_bytes(payload, campus_code=campus_code, **kwargs)).decode('ascii')
    return f'data:image/png;base64,{encoded}'
