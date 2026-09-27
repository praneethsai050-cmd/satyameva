"""
Digital stamping.

Produces the downloadable "stamped copy" of a credential:

  * If the student's original upload is an image, the verification stamp is
    composited onto it and a certificate-style verification page is appended.
  * If there is no image (or the upload is a PDF, which Pillow cannot
    rasterise without extra native dependencies), a standalone verification
    certificate page is generated instead.

Everything is drawn with Pillow so the project stays on pure-Python deps —
no reportlab, no wkhtmltopdf, nothing to install on a demo machine.
"""
from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from extensions import utcnow
from services.qr_service import qr_png_bytes

# ---- Palette (mirrors static/css/theme.css) ----
INK = (18, 18, 58)
INDIGO = (47, 107, 237)      # primary blue
PURPLE = (13, 148, 136)      # secondary teal
GREEN = (67, 160, 71)
MUTED = (110, 116, 150)
PAPER = (255, 255, 255)
WASH = (246, 247, 253)

PAGE_W, PAGE_H = 1240, 1754        # A4 at ~150 DPI


def _font(size: int, bold: bool = False):
    """
    Best-effort font lookup.

    Windows ships Segoe UI; the DejaVu fallback covers Linux CI. Pillow's
    default bitmap font is the last resort so stamping never hard-fails.
    """
    candidates = (
        ['segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf']
        if bold else
        ['segoeui.ttf', 'arial.ttf', 'DejaVuSans.ttf']
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _text_width(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    left, _, right, _ = draw.textbbox((0, 0), text, font=font)
    return right - left


def _rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _draw_check(draw, x, y, size, colour, width):
    """
    Draw a checkmark as two strokes.

    The U+2713 glyph is missing from several of the bold faces we fall back
    to (it renders as tofu), so the tick is drawn geometrically instead.
    """
    draw.line(
        [
            (x + size * 0.10, y + size * 0.55),
            (x + size * 0.38, y + size * 0.82),
            (x + size * 0.90, y + size * 0.16),
        ],
        fill=colour, width=width, joint='curve',
    )


def _fit_font(draw, text: str, max_width: int, start: int, bold: bool = True,
              minimum: int = 16):
    """Largest font size at which `text` still fits inside `max_width`."""
    size = start
    while size > minimum:
        font = _font(size, bold=bold)
        if _text_width(draw, text, font) <= max_width:
            return font
        size -= 2
    return _font(minimum, bold=bold)


# ─── The stamp itself ─────────────────────────────────────────────────────────
#: Logical canvas the seal's coordinates are tuned against. The seal is always
#: composed at this size and then scaled to whatever the caller asked for, so
#: the proportions hold identically on a 210px badge and a 500px page stamp.
STAMP_DESIGN_SIZE = 420


def build_stamp(doc_hash: str, stamped_on: datetime, size: int = 420) -> Image.Image:
    """
    Render the rotated "VERIFIED" seal as a transparent RGBA layer.

    Composed at 2x the design size and downsampled, so the rings and text
    edges stay smooth through both the rotation and the final scale.
    """
    scale = 2
    s = STAMP_DESIGN_SIZE * scale
    canvas = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    ring = (67, 160, 71, 230)

    # Double ring — the classic rubber-stamp silhouette.
    draw.ellipse([12 * scale, 12 * scale, s - 12 * scale, s - 12 * scale],
                 outline=ring, width=7 * scale)
    draw.ellipse([26 * scale, 26 * scale, s - 26 * scale, s - 26 * scale],
                 outline=ring, width=3 * scale)

    f_big = _font(46 * scale, bold=True)
    f_mid = _font(21 * scale, bold=True)
    f_small = _font(15 * scale)
    f_tiny = _font(13 * scale)

    def centered(text, y, font, fill):
        draw.text(((s - _text_width(draw, text, font)) / 2, y), text, font=font, fill=fill)

    centered('SATYAMEVA', 68 * scale, f_mid, (67, 160, 71, 235))

    # "✓ VERIFIED" as a centred group: drawn tick + word.
    word = 'VERIFIED'
    word_w = _text_width(draw, word, f_big)
    tick = 52 * scale
    gap = 14 * scale
    group_x = (s - (tick + gap + word_w)) / 2
    _draw_check(draw, group_x, 120 * scale, tick, (67, 160, 71, 245), 7 * scale)
    draw.text((group_x + tick + gap, 118 * scale), word, font=f_big,
              fill=(67, 160, 71, 245))

    draw.line([(70 * scale, 190 * scale), (s - 70 * scale, 190 * scale)],
              fill=(67, 160, 71, 170), width=2 * scale)

    centered('BLOCKCHAIN SECURED', 205 * scale, f_small, (67, 160, 71, 220))
    centered(stamped_on.strftime('%d %b %Y · %H:%M UTC'), 236 * scale, f_tiny, (67, 160, 71, 205))
    centered(f'{doc_hash[:8]}…{doc_hash[-8:]}', 262 * scale, f_tiny, (67, 160, 71, 205))
    centered('TAMPER-PROOF', 300 * scale, f_small, (67, 160, 71, 200))

    canvas = canvas.resize((size, size), Image.LANCZOS)
    return canvas.rotate(-14, resample=Image.BICUBIC, expand=False)


def stamp_image(source: Image.Image, doc_hash: str, stamped_on: datetime) -> Image.Image:
    """Composite the seal onto the lower-right of the student's document."""
    base = source.convert('RGBA')
    # Seal scales with the page so it stays legible on both A4 scans and photos.
    seal_size = max(220, int(min(base.size) * 0.42))
    seal = build_stamp(doc_hash, stamped_on, size=seal_size)

    margin = int(seal_size * 0.10)
    position = (base.width - seal_size - margin, base.height - seal_size - margin)

    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    layer.paste(seal, position, seal)
    return Image.alpha_composite(base, layer).convert('RGB')


# ─── Verification certificate page ────────────────────────────────────────────
def build_certificate_page(doc, student, verify_url: str, campus_code: str | None = None) -> Image.Image:
    """
    A self-contained A4 verification page: identity, blockchain anchor,
    full hash and a scannable QR — everything a verifier needs on paper.
    """
    page = Image.new('RGB', (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)

    f_h = _font(34, bold=True)
    f_body = _font(22, bold=False)
    f_label = _font(17, bold=True)
    f_foot = _font(15, bold=False)

    # ---- Header banner ----
    header_h = 138
    draw.rectangle([0, 0, PAGE_W, header_h], fill=INK)
    # Indigo accent band across the bottom of the header
    draw.rectangle([0, header_h - 8, PAGE_W, header_h], fill=INDIGO)

    draw.text((70, 36), 'SATYAMEVA', font=_font(38, bold=True), fill=PAPER)
    draw.text((320, 48), 'ACADEMIC CREDENTIAL LEDGER', font=_font(18, bold=True),
              fill=(168, 178, 218))
    draw.text((70, 84), 'Cryptographic Proof of Authenticity', font=f_body,
              fill=(190, 198, 230))

    y = header_h + 54

    # ---- Verified banner ----
    _rounded(draw, [70, y, PAGE_W - 70, y + 90], 18, fill=(234, 248, 236),
             outline=GREEN, width=3)
    _draw_check(draw, 100, y + 24, 42, GREEN, 6)
    draw.text((158, y + 17), 'AUTHENTIC CREDENTIAL', font=f_h, fill=GREEN)
    draw.text((160, y + 54), 'Integrity confirmed against the Satyameva ledger',
              font=f_label, fill=(70, 120, 78))
    y += 132

    # ---- Detail rows ----
    # Row metrics are deliberately tight: eleven rows plus the anchor band and
    # the footer all have to fit one A4 page without a second sheet.
    ROW_H, ROW_STEP, SECTION_GAP = 54, 62, 20

    def section(heading, rows):
        nonlocal y
        draw.text((70, y), heading, font=_font(22, bold=True), fill=INDIGO)
        y += 38
        for label, value in rows:
            _rounded(draw, [70, y, PAGE_W - 70, y + ROW_H], 12, fill=WASH)
            draw.text((92, y + 16), label, font=f_label, fill=MUTED)
            text = str(value) if value not in (None, '') else '—'
            # Shrink rather than truncate, so a long institution name stays readable.
            value_font = _fit_font(draw, text, PAGE_W - 70 - 470 - 30,
                                   start=25, bold=True, minimum=17)
            draw.text((470, y + 15), text, font=value_font, fill=INK)
            y += ROW_STEP
        y += SECTION_GAP

    section('CREDENTIAL HOLDER', [
        ('Student Name', student.full_name),
        ('Roll Number', student.roll_number),
        ('Programme', student.program),
        ('Institution', student.institution),
    ])

    section('DOCUMENT', [
        ('Type', doc.type_label),
        ('Title', doc.title),
        ('Issued By', doc.issuer_name),
        ('Issued On', doc.issued_on.strftime('%d %B %Y')),
        ('Valid Until', doc.valid_until.strftime('%d %B %Y') if doc.valid_until else 'No expiry'),
        ('Status', doc.status_label),
    ])

    # ---- Blockchain anchor band: details + seal + QR on one row ----
    draw.text((70, y), 'BLOCKCHAIN ANCHOR', font=_font(22, bold=True), fill=INDIGO)
    y += 38

    band_h = 262
    qr_size = 240
    qr_x = PAGE_W - 70 - qr_size
    qr_img = Image.open(BytesIO(qr_png_bytes(verify_url, campus_code=campus_code, box_size=8, border=1))).convert('RGB')
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    page.paste(qr_img, (qr_x, y + (band_h - qr_size) // 2))
    draw.text((qr_x + 22, y + band_h - 4), 'Scan to verify instantly', font=f_foot, fill=MUTED)

    box_right = qr_x - 34
    _rounded(draw, [70, y, box_right, y + band_h], 14, fill=WASH)

    bx, by = 96, y + 22
    for label, value in [
        ('Block Index', f'#{doc.block_index}' if doc.block_index is not None else '—'),
        ('Transaction', doc.tx_hash or '—'),
        ('Verifications', f'{doc.verification_count} time(s)'),
    ]:
        draw.text((bx, by), label, font=f_label, fill=MUTED)
        value_font = _fit_font(draw, value, 330, start=21, bold=True, minimum=14)
        draw.text((bx, by + 25), value, font=value_font, fill=INK)
        by += 78

    # The seal sits in the band's free right-hand space — reads like a stamp
    # applied over the ledger details, and costs no extra vertical room.
    seal_size = 210
    seal = build_stamp(doc.doc_hash, doc.stamp_date or doc.issued_on, size=seal_size)
    seal_layer = Image.new('RGBA', page.size, (0, 0, 0, 0))
    seal_layer.paste(seal, (box_right - seal_size - 30, y + (band_h - seal_size) // 2), seal)
    page = Image.alpha_composite(page.convert('RGBA'), seal_layer).convert('RGB')
    draw = ImageDraw.Draw(page)

    y += band_h + 40

    # ---- Full hash, across the page ----
    draw.text((70, y), 'DOCUMENT HASH (SHA-256)', font=_font(19, bold=True), fill=MUTED)
    hash_font = _fit_font(draw, doc.doc_hash, PAGE_W - 140, start=22, bold=False, minimum=13)
    draw.text((70, y + 26), doc.doc_hash, font=hash_font, fill=INK)

    # ---- Footer ----
    draw.line([(70, PAGE_H - 118), (PAGE_W - 70, PAGE_H - 118)], fill=(224, 227, 240), width=2)
    draw.text((70, PAGE_H - 96),
              'This certificate is cryptographically anchored to the Satyameva blockchain.',
              font=f_foot, fill=MUTED)
    draw.text((70, PAGE_H - 68),
              f'Any alteration invalidates the hash above. Verify at: {verify_url[:78]}',
              font=f_foot, fill=MUTED)
    draw.text((70, PAGE_H - 40),
              f'Generated {utcnow().strftime("%d %B %Y at %H:%M UTC")}',
              font=f_foot, fill=MUTED)

    return page


# ─── Public entry point ───────────────────────────────────────────────────────
def generate_stamped_pdf(doc, student, verify_url: str, campus_code: str | None = None) -> bytes:
    """
    Build the downloadable stamped PDF.

    Page 1 is the original document with the seal composited on (when the
    upload is an image); the verification certificate always follows, so the
    file is useful even for PDF or file-less credentials.
    """
    pages: list[Image.Image] = []

    if doc.file_data and doc.is_previewable_image:
        try:
            original = Image.open(BytesIO(doc.file_data))
            original.load()
            pages.append(stamp_image(original, doc.doc_hash, doc.stamp_date or doc.issued_on))
        except Exception:
            # A corrupt or unsupported upload must not block the download —
            # the certificate page below still proves the credential.
            pass

    pages.append(build_certificate_page(doc, student, verify_url, campus_code=campus_code))

    buffer = BytesIO()
    pages[0].save(buffer, format='PDF', save_all=True,
                  append_images=pages[1:], resolution=150.0)
    return buffer.getvalue()


def generate_stamped_image(doc) -> bytes | None:
    """Stamped PNG of the original upload, or None when there is no image."""
    if not (doc.file_data and doc.is_previewable_image):
        return None
    try:
        original = Image.open(BytesIO(doc.file_data))
        original.load()
    except Exception:
        return None

    stamped = stamp_image(original, doc.doc_hash, doc.stamp_date or doc.issued_on)
    buffer = BytesIO()
    stamped.save(buffer, format='PNG')
    return buffer.getvalue()
