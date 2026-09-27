"""
Generate Cyber Holographic Shield Icon Suite for Satyameva Aegis.

Generates:
  1. static/favicon.ico (Multi-resolution Windows icon: 16, 32, 48, 64, 128, 256 px)
  2. satyameva.ico (Desktop application icon)
  3. static/img/icon-192.png (192x192 PWA Web App Icon)
  4. static/img/icon-512.png (512x512 High-Res Splash Icon)
  5. static/img/apple-touch-icon.png (180x180 iOS Touch Icon)

Design:
  - 3D Cyber Holographic Shield with quantum cyan, cobalt blue and deep midnight slate.
  - Imperial Gold Jaypee academic torch & crest emblem.
  - Interlinked blockchain nodes with cryptographic security core.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont


def draw_cyber_shield_icon(size: int = 1024) -> Image.Image:
    # 4x Supersampling for ultra-crisp antialiasing
    scale = 2
    dim = size * scale
    canvas = Image.new('RGBA', (dim, dim), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    center_x = dim / 2
    center_y = dim / 2

    # 1. Ambient Holographic Cyber Glow
    glow_radius = dim * 0.46
    for i in range(24):
        t = i / 24.0
        r = glow_radius * (0.6 + 0.4 * t)
        alpha = int(45 * (1.0 - t) ** 1.8)
        draw.ellipse(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            fill=(6, 182, 212, alpha)
        )

    # 2. Outer Hexagonal / Blockchain Data Ring
    node_count = 6
    ring_r = dim * 0.40
    pts = []
    for k in range(node_count):
        ang = math.radians(k * (360 / node_count) - 30)
        px = center_x + ring_r * math.cos(ang)
        py = center_y + ring_r * math.sin(ang)
        pts.append((px, py))

    # Draw polygon border connecting nodes
    for k in range(node_count):
        p1 = pts[k]
        p2 = pts[(k + 1) % node_count]
        draw.line([p1, p2], fill=(6, 182, 212, 160), width=int(5 * scale))

    # Draw nodes
    for px, py in pts:
        nr = 14 * scale
        draw.ellipse([px - nr, px - nr, px + nr, px + nr], fill=(15, 23, 42, 255), outline=(56, 189, 248, 255), width=int(3 * scale))
        draw.ellipse([px - nr * 0.4, py - nr * 0.4, px + nr * 0.4, py + nr * 0.4], fill=(6, 182, 212, 255))

    # 3. Main Cryptographic Shield Geometry
    # Top width, height, curvature points
    sw = dim * 0.28
    s_top = center_y - (dim * 0.30)
    s_mid = center_y + (dim * 0.08)
    s_bot = center_y + (dim * 0.34)

    # Outer Shield (Cyan Neon Border)
    outer_pts = [
        (center_x - sw, s_top),
        (center_x + sw, s_top),
        (center_x + sw, s_mid),
        (center_x, s_bot),
        (center_x - sw, s_mid),
    ]
    # Draw shadow
    shadow_offset = int(12 * scale)
    shadow_pts = [(x, y + shadow_offset) for x, y in outer_pts]
    draw.polygon(shadow_pts, fill=(0, 0, 0, 140))

    # Outer shield border
    draw.polygon(outer_pts, fill=(6, 182, 212, 255))

    # Inner Shield 1: Deep Royal Navy Plate
    pad1 = int(7 * scale)
    shield1_pts = [
        (center_x - sw + pad1, s_top + pad1),
        (center_x + sw - pad1, s_top + pad1),
        (center_x + sw - pad1, s_mid),
        (center_x, s_bot - int(pad1 * 1.4)),
        (center_x - sw + pad1, s_mid),
    ]
    draw.polygon(shield1_pts, fill=(11, 22, 54, 255))

    # Inner Shield 2: Cyber Slate Dark Core
    pad2 = int(18 * scale)
    shield2_pts = [
        (center_x - sw + pad2, s_top + pad2),
        (center_x + sw - pad2, s_top + pad2),
        (center_x + sw - pad2, s_mid - int(pad2 * 0.3)),
        (center_x, s_bot - int(pad2 * 1.5)),
        (center_x - sw + pad2, s_mid - int(pad2 * 0.3)),
    ]
    draw.polygon(shield2_pts, fill=(15, 23, 42, 255), outline=(56, 189, 248, 180), width=int(2.5 * scale))

    # 4. Subtle 3D Glass Surface Shading
    # Left hemisphere highlight
    highlight_pts = [
        (center_x - sw + pad2, s_top + pad2),
        (center_x, s_top + pad2),
        (center_x, s_bot - int(pad2 * 1.5)),
        (center_x - sw + pad2, s_mid - int(pad2 * 0.3)),
    ]
    draw.polygon(highlight_pts, fill=(255, 255, 255, 22))

    # 5. Imperial Gold Academic Torch & Knowledge Flame (Jaypee Emblem)
    torch_base_y = center_y + (dim * 0.14)
    torch_top_y = center_y - (dim * 0.05)
    tw = dim * 0.035

    # Torch handle
    draw.polygon([
        (center_x - tw, torch_base_y),
        (center_x + tw, torch_base_y),
        (center_x + tw * 1.3, torch_top_y),
        (center_x - tw * 1.3, torch_top_y),
    ], fill=(212, 175, 55, 255))

    # Torch cup
    cup_w = tw * 2.2
    cup_h = int(14 * scale)
    draw.rounded_rectangle([
        center_x - cup_w, torch_top_y - cup_h,
        center_x + cup_w, torch_top_y + (4 * scale)
    ], radius=int(4 * scale), fill=(245, 180, 40, 255), outline=(255, 255, 255, 180), width=int(1.5 * scale))

    # Flame of Knowledge (Layered Golden / Amber Glow)
    flame_tip_y = center_y - (dim * 0.17)
    flame_bot_y = torch_top_y - cup_h

    # Outer flame
    draw.polygon([
        (center_x, flame_tip_y),
        (center_x + (tw * 2.0), flame_bot_y + (10 * scale)),
        (center_x, flame_bot_y - (6 * scale)),
        (center_x - (tw * 2.0), flame_bot_y + (10 * scale)),
    ], fill=(245, 158, 11, 255))

    # Inner core flame
    draw.polygon([
        (center_x, flame_tip_y + (10 * scale)),
        (center_x + (tw * 1.1), flame_bot_y + (8 * scale)),
        (center_x, flame_bot_y - (2 * scale)),
        (center_x - (tw * 1.1), flame_bot_y + (8 * scale)),
    ], fill=(254, 240, 138, 255))

    # 6. Cryptographic Chain Links across the lower shield
    chain_y = torch_base_y + (18 * scale)
    link_w = int(22 * scale)
    link_h = int(11 * scale)

    # Left link
    draw.rounded_rectangle([
        center_x - (link_w * 1.4), chain_y - (link_h / 2),
        center_x - (link_w * 0.3), chain_y + (link_h / 2)
    ], radius=int(5 * scale), outline=(212, 175, 55, 255), width=int(3 * scale))

    # Right link
    draw.rounded_rectangle([
        center_x + (link_w * 0.3), chain_y - (link_h / 2),
        center_x + (link_w * 1.4), chain_y + (link_h / 2)
    ], radius=int(5 * scale), outline=(212, 175, 55, 255), width=int(3 * scale))

    # Central lock node
    draw.ellipse([
        center_x - (9 * scale), chain_y - (9 * scale),
        center_x + (9 * scale), chain_y + (9 * scale)
    ], fill=(6, 182, 212, 255), outline=(255, 255, 255, 230), width=int(2 * scale))

    # Downscale smoothly to output size via LANCZOS
    icon = canvas.resize((size, size), Image.LANCZOS)
    return icon


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, 'static')
    img_dir = os.path.join(static_dir, 'img')
    os.makedirs(img_dir, exist_ok=True)

    print('Generating Cyber Holographic Shield Icon Suite...')
    master = draw_cyber_shield_icon(size=1024)

    # 1. 512x512 PWA Splash / Android Icon
    icon_512 = master.resize((512, 512), Image.LANCZOS)
    path_512 = os.path.join(img_dir, 'icon-512.png')
    icon_512.save(path_512, 'PNG')
    print(f' -> Saved {path_512}')

    # 2. 192x192 PWA Web App Icon
    icon_192 = master.resize((192, 192), Image.LANCZOS)
    path_192 = os.path.join(img_dir, 'icon-192.png')
    icon_192.save(path_192, 'PNG')
    print(f' -> Saved {path_192}')

    # 3. 180x180 Apple Touch Icon
    icon_180 = master.resize((180, 180), Image.LANCZOS)
    path_180 = os.path.join(img_dir, 'apple-touch-icon.png')
    icon_180.save(path_180, 'PNG')
    print(f' -> Saved {path_180}')

    # 4. Multi-resolution Windows ICO (16, 32, 48, 64, 128, 256)
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    path_favicon = os.path.join(static_dir, 'favicon.ico')
    path_desktop_ico = os.path.join(base_dir, 'satyameva.ico')

    master.save(path_favicon, format='ICO', sizes=ico_sizes)
    master.save(path_desktop_ico, format='ICO', sizes=ico_sizes)
    print(f' -> Saved multi-resolution {path_favicon}')
    print(f' -> Saved desktop icon {path_desktop_ico}')

    print('Icon generation complete!')


if __name__ == '__main__':
    main()
