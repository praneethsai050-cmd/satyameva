"""
Institutional Crest Service for Satyameva Aegis.

Generates high-resolution, anti-aliased circular crest emblems for each
Jaypee campus:
  - JIIT: Jaypee Institute of Information Technology (Royal Navy & Gold)
  - JUIT: Jaypee University of Information Technology (Alpine Emerald & Gold)
  - JUET: Jaypee University of Engineering & Technology (Imperial Crimson & Amber)
  - AEGIS: Universal Satyameva Cryptographic Ledger Crest (Cyber Cyan & Platinum)

Rendered at 4x supersampling with Lanczos downscaling for retina sharpness
when embedded inside QR codes.
"""
from PIL import Image, ImageDraw, ImageFont

# Campus palettes
CAMPUS_THEMES = {
    'JIIT': {
        'primary': (14, 38, 92),        # Deep Royal Navy
        'secondary': (212, 160, 23),    # Imperial Gold
        'accent': (47, 107, 237),       # Cyber Cobalt
        'ring': (230, 180, 34),
        'tag': 'JIIT',
        'sub': 'NOIDA',
    },
    'JUIT': {
        'primary': (12, 68, 48),        # Alpine Pine / Emerald
        'secondary': (212, 175, 55),    # Mountain Gold
        'accent': (16, 185, 129),       # Spring Jade
        'ring': (220, 185, 65),
        'tag': 'JUIT',
        'sub': 'SOLAN',
    },
    'JUET': {
        'primary': (110, 18, 28),       # Engineering Crimson
        'secondary': (235, 155, 30),    # Forge Amber
        'accent': (239, 68, 68),        # Flame Red
        'ring': (245, 170, 45),
        'tag': 'JUET',
        'sub': 'GUNA',
    },
    'AEGIS': {
        'primary': (15, 23, 42),        # Cyber Slate
        'secondary': (6, 182, 212),     # Quantum Cyan
        'accent': (99, 102, 241),       # Indigo Beacon
        'ring': (34, 211, 238),
        'tag': 'AEGIS',
        'sub': 'VERIFIED',
    },
}


def _get_font(size: int, bold: bool = True):
    """Load system font with graceful fallback."""
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


def get_campus_crest(campus_code: str | None, size: int = 120) -> Image.Image:
    """
    Generate a circular institutional crest badge for `campus_code`.
    
    Rendered at 4x resolution (size * 4) and downsampled via LANCZOS for
    smooth curves, vector-sharp typography, and anti-aliased borders.
    """
    code = (campus_code or 'AEGIS').upper().strip()
    theme = CAMPUS_THEMES.get(code, CAMPUS_THEMES['AEGIS'])

    scale = 4
    canvas_dim = size * scale
    canvas = Image.new('RGBA', (canvas_dim, canvas_dim), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    center = canvas_dim / 2
    r_outer = canvas_dim / 2 - (4 * scale)

    # 1. Outer White Isolation Margin (keeps QR modules cleanly separated)
    draw.ellipse(
        [center - r_outer, center - r_outer, center + r_outer, center + r_outer],
        fill=(255, 255, 255, 255)
    )

    # 2. Outer Metallic Accent Ring
    r_ring = r_outer - (2.5 * scale)
    draw.ellipse(
        [center - r_ring, center - r_ring, center + r_ring, center + r_ring],
        fill=theme['primary'],
        outline=theme['ring'],
        width=int(2.5 * scale)
    )

    # 3. Inner Decorative Ring
    r_inner = r_ring - (4 * scale)
    draw.ellipse(
        [center - r_inner, center - r_inner, center + r_inner, center + r_inner],
        outline=theme['secondary'],
        width=int(1.2 * scale)
    )

    # 4. Central Academic Shield / Emblem Motif
    # Shield shape
    sw = 28 * scale
    sh_top = center - (20 * scale)
    sh_bot = center + (16 * scale)

    shield_pts = [
        (center - sw, sh_top),
        (center + sw, sh_top),
        (center + sw, center + (2 * scale)),
        (center, sh_bot),
        (center - sw, center + (2 * scale)),
    ]
    draw.polygon(shield_pts, fill=theme['secondary'])

    # Inner shield accent
    inner_sw = 23 * scale
    inner_sh_top = sh_top + (2.5 * scale)
    inner_sh_bot = sh_bot - (3 * scale)
    inner_shield_pts = [
        (center - inner_sw, inner_sh_top),
        (center + inner_sw, inner_sh_top),
        (center + inner_sw, center + (1 * scale)),
        (center, inner_sh_bot),
        (center - inner_sw, center + (1 * scale)),
    ]
    draw.polygon(inner_shield_pts, fill=theme['primary'])

    # 5. University Letters (e.g. JIIT / JUIT / JUET / AEGIS)
    font_main = _get_font(int(15 * scale), bold=True)
    tag_text = theme['tag']
    bbox = draw.textbbox((0, 0), tag_text, font=font_main)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = center - (tw / 2)
    ty = center - (th / 2) - (4 * scale)
    draw.text((tx, ty), tag_text, fill=(255, 255, 255), font=font_main)

    # 6. Subtitle Ribbon / Location (NOIDA, SOLAN, GUNA, VERIFIED)
    sub_font = _get_font(int(7 * scale), bold=True)
    sub_text = theme['sub']
    sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    stw = sub_bbox[2] - sub_bbox[0]
    sth = sub_bbox[3] - sub_bbox[1]

    # Pill badge for subtitle
    pill_pad_x = 4 * scale
    pill_pad_y = 1.5 * scale
    rx0 = center - (stw / 2) - pill_pad_x
    ry0 = center + (9 * scale)
    rx1 = center + (stw / 2) + pill_pad_x
    ry1 = ry0 + sth + (pill_pad_y * 2)

    draw.rounded_rectangle(
        [rx0, ry0, rx1, ry1],
        radius=int(3 * scale),
        fill=theme['secondary']
    )
    draw.text(
        (center - (stw / 2), ry0 + pill_pad_y - (0.5 * scale)),
        sub_text,
        fill=theme['primary'],
        font=sub_font
    )

    # Downsample cleanly to destination size using Lanczos anti-aliasing
    badge = canvas.resize((size, size), Image.LANCZOS)
    return badge
