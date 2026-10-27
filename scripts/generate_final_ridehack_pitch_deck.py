"""
generate_final_ridehack_pitch_deck.py
Generates the official 8-slide RIDE Hack '26 Grand Finale Pitch Deck (PPTX & PDF)
Strictly covering the 7 mandatory points specified by the organizers:
1. Problem Statement
2. Proposed Solution
3. Unique Value Proposition
4. Market Opportunity
5. Business Model
6. Financials (with Pie Chart, Donut Chart, and ARR Bar Chart)
7. Future Scope
Plus Title/Cover slide.
Also generates the standalone 10-15 minute Pitch Speaking Script PDF.
"""

import os
import sys
import shutil
from PIL import Image
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

import pymupdf
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Segoe UI TrueType fonts for native unicode
pdfmetrics.registerFont(TTFont('SegoeUI', 'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUI-Bold', 'C:/Windows/Fonts/segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUI-Italic', 'C:/Windows/Fonts/segoeuii.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUI-BoldItalic', 'C:/Windows/Fonts/segoeuiz.ttf'))
pdfmetrics.registerFontFamily(
    'SegoeUI',
    normal='SegoeUI',
    bold='SegoeUI-Bold',
    italic='SegoeUI-Italic',
    boldItalic='SegoeUI-BoldItalic'
)

# File Paths
DESKTOP_DIR   = r"C:\Users\hp\OneDrive\Desktop"
SATYAMEVA_DIR = r"C:\Users\hp\OneDrive\Desktop\Satyameva"
SIH_DIR       = r"C:\Users\hp\OneDrive\Desktop\SIH_Aegis"
ARTIFACT_DIR  = r"C:\Users\hp\.gemini\antigravity\brain\898a4eb6-926a-417b-9cac-f6e58897bc1b"

OUT_PPTX   = os.path.join(DESKTOP_DIR, "RIDEHACK26_FINAL_PITCH_DECK.pptx")
OUT_PDF    = os.path.join(DESKTOP_DIR, "RIDEHACK26_FINAL_PITCH_DECK.pdf")
OUT_SCRIPT = os.path.join(DESKTOP_DIR, "RIDEHACK26_PITCH_SPEAKING_SCRIPT_10_15_MIN.pdf")

# Image Assets
IMG_PROBLEM   = r"C:/Users/hp/.gemini/antigravity/brain/898a4eb6-926a-417b-9cac-f6e58897bc1b/problem_statement_credential_forgery_1793031799283.jpg"
IMG_SOLUTION  = r"C:/Users/hp/.gemini/antigravity/brain/898a4eb6-926a-417b-9cac-f6e58897bc1b/blockchain_digital_degree_slide_1793031719875.jpg"
IMG_PIE       = r"C:/Users/hp/OneDrive/Desktop/Satyameva/assets/ask_pie_chart.png"
IMG_COGS      = r"C:/Users/hp/OneDrive/Desktop/Satyameva/assets/cogs_donut_chart.png"
IMG_ARR       = r"C:/Users/hp/OneDrive/Desktop/Satyameva/assets/arr_growth_bar_chart.png"
IMG_TEAM      = r"C:/Users/hp/.gemini/antigravity/brain/898a4eb6-926a-417b-9cac-f6e58897bc1b/.user_uploaded/media_1792562188616_fb3cf0ec.png"

# PPTX Palette
C_BG          = RGBColor(11, 17, 32)     # #0B1120 Midnight Navy
C_CARD        = RGBColor(19, 29, 49)     # #131D31 Card Deep Navy
C_CARD_BORDER = RGBColor(30, 58, 95)     # #1E3A5F Border
C_CYAN        = RGBColor(56, 189, 248)   # #38BDF8 Electric Cyan
C_GOLD        = RGBColor(212, 175, 55)   # #D4AF37 JUIT Academic Gold
C_GREEN       = RGBColor(16, 185, 129)   # #10B981 Emerald Green
C_RED         = RGBColor(239, 68, 68)    # #EF4444 Crimson Alert
C_PURPLE      = RGBColor(192, 132, 252)  # #C084FC Lavender / Electric Purple
C_WHITE       = RGBColor(248, 250, 252)  # #F8FAFC Pure White
C_MUTED       = RGBColor(148, 163, 184)  # #94A3B8 Slate Gray
C_DARK_CARD   = RGBColor(15, 23, 42)     # #0F172A Dark Slate


def create_pptx_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.color.rgb = C_BG
        return bg

    def add_top_bar(slide, pill_text, title_text, pill_color=C_GOLD):
        # Category Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(4.5), Inches(0.35))
        pill.fill.solid()
        pill.fill.fore_color.rgb = C_DARK_CARD
        pill.line.color.rgb = pill_color
        pill.line.width = Pt(1.2)
        tf = pill.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = pill_text
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = pill_color
        p.alignment = PP_ALIGN.CENTER

        # Slide Main Title
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.7), Inches(0.7))
        tf_t = tb.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = "Arial"
        p_t.font.size = Pt(20)
        p_t.font.bold = True
        p_t.font.color.rgb = C_WHITE

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 1: TITLE & COVER SLIDE
    # ═══════════════════════════════════════════════════════════════════════════
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1)

    # Mandate Badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.55), Inches(11.733), Inches(0.42))
    badge.fill.solid()
    badge.fill.fore_color.rgb = C_DARK_CARD
    badge.line.color.rgb = C_GOLD
    badge.line.width = Pt(1.5)
    tf = badge.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = "JAYPEE UNIVERSITY OF INFORMATION TECHNOLOGY · IIC RIDEHACK'26 GRAND FINALE · JIIT NOIDA"
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p.alignment = PP_ALIGN.CENTER

    # Left Column: Venture Overview & Pitch Highlights
    card_title = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.15), Inches(5.65), Inches(5.75))
    card_title.fill.solid()
    card_title.fill.fore_color.rgb = C_CARD
    card_title.line.color.rgb = C_CARD_BORDER
    card_title.line.width = Pt(1.2)
    tf_c = card_title.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = Inches(0.35)
    tf_c.margin_right = Inches(0.35)
    tf_c.margin_top = Inches(0.35)
    tf_c.margin_bottom = Inches(0.25)

    p1 = tf_c.paragraphs[0]
    p1.text = "SATYAMEVA AEGIS"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf_c.add_paragraph()
    p2.text = "Decentralized Academic Credential Integrity & Instant Verification Engine"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = C_CYAN
    p2.space_before = Pt(6)

    p3 = tf_c.add_paragraph()
    p3.text = "Eradicating Indian academic credential counterfeiting by compressing verification from 21 days down to 60 seconds with Zero Gas Fees, Google Gemini AI OCR, and 3D Holographic Proofs."
    p3.font.name = "Segoe UI"
    p3.font.size = Pt(10)
    p3.font.color.rgb = C_MUTED
    p3.space_before = Pt(8)

    p4 = tf_c.add_paragraph()
    p4.text = "KEY VENTURE MULTIPLIERS:"
    p4.font.name = "Segoe UI"
    p4.font.size = Pt(10)
    p4.font.bold = True
    p4.font.color.rgb = C_GOLD
    p4.space_before = Pt(14)

    bullets = [
        "•   Turnaround: 14–21 Days ➔ <60 Seconds (99.9% clerical reduction)",
        "•   Institutional Unit Cost: < ₹0.48 / Credential (Gross Margin > 90%)",
        "•   Zero Gas Fees: Private PoW blockchain immune to crypto volatility",
        "•   Market Scope: 1,100+ Indian Universities & 40 Million Higher Ed Students"
    ]
    for b in bullets:
        pb = tf_c.add_paragraph()
        pb.text = b
        pb.font.name = "Segoe UI"
        pb.font.size = Pt(9.5)
        pb.font.color.rgb = C_WHITE
        pb.space_before = Pt(5)

    p_foot = tf_c.add_paragraph()
    p_foot.text = "Tech Incubation: Dept. of CSE, JUIT Waknaghat (Solan, H.P.)\nConsortium Pilot Deployment: JUIT · JIIT · JUET Campuses"
    p_foot.font.name = "Segoe UI"
    p_foot.font.size = Pt(8.5)
    p_foot.font.bold = True
    p_foot.font.color.rgb = C_GOLD
    p_foot.space_before = Pt(16)

    # Right Column Header: Founding Team Tag
    head_right = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.65), Inches(1.15), Inches(5.88), Inches(0.40))
    head_right.fill.solid()
    head_right.fill.fore_color.rgb = C_DARK_CARD
    head_right.line.color.rgb = C_CYAN
    head_right.line.width = Pt(1.2)
    tf_hr = head_right.text_frame
    tf_hr.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_hr = tf_hr.paragraphs[0]
    p_hr.text = "CORE FOUNDING TEAM · TEAM ID: 10 (JUIT WAKNAGHAT)"
    p_hr.font.name = "Segoe UI"
    p_hr.font.size = Pt(10.5)
    p_hr.font.bold = True
    p_hr.font.color.rgb = C_CYAN
    p_hr.alignment = PP_ALIGN.CENTER

    # 4 Dedicated Member Profile Cards
    team_members = [
        {
            "name": "A. Praneeth Sai",
            "role": "FOUNDER & ARCHITECTURE LEAD",
            "role_col": C_CYAN,
            "border_col": C_CYAN,
            "degree": "B.Tech CSE Core (2026–2030) · JUIT Waknaghat",
            "focus": "Zero-Gas Private Blockchain · Web3 Architecture · SHA-256 Merkle Ledger"
        },
        {
            "name": "Anushka Bansal",
            "role": "CO-FOUNDER & DATA LEAD",
            "role_col": C_GOLD,
            "border_col": C_GOLD,
            "degree": "B.Tech CSE Core (2026–2030) · JUIT Waknaghat",
            "focus": "Data Integrity · Academic Record Schema · Institutional Portal Integration"
        },
        {
            "name": "Shashank Ray",
            "role": "CO-FOUNDER & AI MODEL LEAD",
            "role_col": C_GREEN,
            "border_col": C_GREEN,
            "degree": "B.Tech CSE Core (2026–2030) · JUIT Waknaghat",
            "focus": "Gemini AI Vision Engine · Multimodal OCR · Tamper & Pixel Forgery Detection"
        },
        {
            "name": "Sameeksha Chandel",
            "role": "CO-FOUNDER & PRODUCT LEAD",
            "role_col": C_PURPLE,
            "border_col": C_PURPLE,
            "degree": "B.Tech CSE Core (2026–2030) · JUIT Waknaghat",
            "focus": "Product Strategy · UI/UX Verification Portal · BGV Enterprise Workflow"
        }
    ]

    y_start = Inches(1.67)
    card_h = Inches(1.21)
    gap = Inches(0.13)

    for idx, m in enumerate(team_members):
        c_y = y_start + idx * (card_h + gap)
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.65), c_y, Inches(5.88), card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD
        card.line.color.rgb = m["border_col"]
        card.line.width = Pt(1.5)

        tf_m = card.text_frame
        tf_m.word_wrap = True
        tf_m.margin_left = Inches(0.32)
        tf_m.margin_right = Inches(0.25)
        tf_m.margin_top = Inches(0.12)
        tf_m.margin_bottom = Inches(0.10)

        # Line 1: Name and Role
        p_name = tf_m.paragraphs[0]
        p_name.alignment = PP_ALIGN.LEFT
        run_name = p_name.add_run()
        run_name.text = m["name"]
        run_name.font.name = "Segoe UI"
        run_name.font.size = Pt(12)
        run_name.font.bold = True
        run_name.font.color.rgb = C_WHITE

        run_sep = p_name.add_run()
        run_sep.text = "   |   "
        run_sep.font.name = "Segoe UI"
        run_sep.font.size = Pt(10)
        run_sep.font.color.rgb = C_MUTED

        run_role = p_name.add_run()
        run_role.text = m["role"]
        run_role.font.name = "Segoe UI"
        run_role.font.size = Pt(10)
        run_role.font.bold = True
        run_role.font.color.rgb = m["role_col"]

        # Line 2: Degree
        p_deg = tf_m.add_paragraph()
        p_deg.alignment = PP_ALIGN.LEFT
        p_deg.text = m["degree"]
        p_deg.font.name = "Segoe UI"
        p_deg.font.size = Pt(8.5)
        p_deg.font.color.rgb = C_MUTED
        p_deg.space_before = Pt(3)

        # Line 3: Focus
        p_foc = tf_m.add_paragraph()
        p_foc.alignment = PP_ALIGN.LEFT
        run_foc_lbl = p_foc.add_run()
        run_foc_lbl.text = "Core Domain: "
        run_foc_lbl.font.name = "Segoe UI"
        run_foc_lbl.font.size = Pt(8.5)
        run_foc_lbl.font.bold = True
        run_foc_lbl.font.color.rgb = m["role_col"]

        run_foc_val = p_foc.add_run()
        run_foc_val.text = m["focus"]
        run_foc_val.font.name = "Segoe UI"
        run_foc_val.font.size = Pt(8.5)
        run_foc_val.font.color.rgb = C_WHITE
        p_foc.space_before = Pt(2)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 2: PROBLEM STATEMENT (MANDATORY POINT 1)
    # ═══════════════════════════════════════════════════════════════════════════
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_top_bar(s2, "MANDATORY POINT 1 · PROBLEM STATEMENT", "The Crisis in Indian Higher Education: Counterfeits & Delays", C_RED)

    # 3 Problem Cards on Left
    prob_box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(6.8), Inches(5.2))
    prob_box.fill.solid()
    prob_box.fill.fore_color.rgb = C_CARD
    prob_box.line.color.rgb = C_CARD_BORDER
    prob_box.line.width = Pt(1.2)
    tf_pb = prob_box.text_frame
    tf_pb.word_wrap = True
    tf_pb.margin_left = Inches(0.35)
    tf_pb.margin_right = Inches(0.35)
    tf_pb.margin_top = Inches(0.3)

    probs = [
        ("1. ₹1,500 Fake Degree & Telegram Syndicates",
         "Over 40,000 fake degrees are officially detected in India annually. Fraud syndicates sell replica marksheets with duplicate seals in 24 hours. Physical paper ink cannot be distinguished from clones by corporate HR.",
         C_RED),
        ("2. 14–21 Day Verification Bottlenecks",
         "Background verification firms (TCS, Wipro, AuthBridge) rely on physical speed-post inquiries and manual registrar emails. This costs Indian universities ₹12–18 Lakhs annually in clerical overhead and stalls graduates' jobs & foreign visas.",
         C_GOLD),
        ("3. Centralized SQL Single Point of Failure",
         "University relational databases lack mathematical auditability. A compromised password or insider database access (UPDATE students SET cgpa=9.5) alters academic history silently with zero immutable cryptographic trail.",
         C_CYAN)
    ]
    for idx, (head, body, col) in enumerate(probs):
        ph = tf_pb.paragraphs[0] if idx == 0 else tf_pb.add_paragraph()
        ph.text = head
        ph.font.name = "Arial"
        ph.font.size = Pt(12)
        ph.font.bold = True
        ph.font.color.rgb = col
        if idx > 0:
            ph.space_before = Pt(14)

        pbd = tf_pb.add_paragraph()
        pbd.text = body
        pbd.font.name = "Arial"
        pbd.font.size = Pt(10)
        pbd.font.color.rgb = C_WHITE
        pbd.space_before = Pt(4)

    # Right: Embedded Problem Concept Illustration & Callout
    if os.path.exists(IMG_PROBLEM):
        s2.shapes.add_picture(IMG_PROBLEM, Inches(7.9), Inches(1.6), Inches(4.6), Inches(3.4))

    callout2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.9), Inches(5.15), Inches(4.6), Inches(1.65))
    callout2.fill.solid()
    callout2.fill.fore_color.rgb = C_DARK_CARD
    callout2.line.color.rgb = C_RED
    callout2.line.width = Pt(1.5)
    tf_co2 = callout2.text_frame
    tf_co2.word_wrap = True
    tf_co2.margin_left = Inches(0.25)
    tf_co2.margin_right = Inches(0.25)
    tf_co2.margin_top = Inches(0.2)
    p_c1 = tf_co2.paragraphs[0]
    p_c1.text = "CRITICAL PAIN POINT:"
    p_c1.font.name = "Arial"
    p_c1.font.size = Pt(10.5)
    p_c1.font.bold = True
    p_c1.font.color.rgb = C_RED
    p_c2 = tf_co2.add_paragraph()
    p_c2.text = "Paper degrees and centralized PDFs have zero intrinsic origin proof. Indian higher education needs an institutional tamper-evident trust layer that operates at the origin."
    p_c2.font.name = "Arial"
    p_c2.font.size = Pt(9.5)
    p_c2.font.color.rgb = C_WHITE
    p_c2.space_before = Pt(4)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 3: PROPOSED SOLUTION (MANDATORY POINT 2)
    # ═══════════════════════════════════════════════════════════════════════════
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_top_bar(s3, "MANDATORY POINT 2 · PROPOSED SOLUTION", "4-Pillar Deep-Tech Architecture: Zero Gas, AI & 3D Holograms", C_GREEN)

    # Left: Solution Illustration & Key Metrics
    if os.path.exists(IMG_SOLUTION):
        s3.shapes.add_picture(IMG_SOLUTION, Inches(0.8), Inches(1.6), Inches(4.7), Inches(3.4))

    sol_metric = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.15), Inches(4.7), Inches(1.65))
    sol_metric.fill.solid()
    sol_metric.fill.fore_color.rgb = C_CARD
    sol_metric.line.color.rgb = C_GREEN
    sol_metric.line.width = Pt(1.5)
    tf_sm = sol_metric.text_frame
    tf_sm.word_wrap = True
    tf_sm.margin_left = Inches(0.25)
    tf_sm.margin_right = Inches(0.25)
    tf_sm.margin_top = Inches(0.2)
    p_sm1 = tf_sm.paragraphs[0]
    p_sm1.text = "THE DEEP-TECH ADVANTAGE:"
    p_sm1.font.name = "Arial"
    p_sm1.font.size = Pt(10.5)
    p_sm1.font.bold = True
    p_sm1.font.color.rgb = C_GREEN
    p_sm2 = tf_sm.add_paragraph()
    p_sm2.text = "• 100% Zero-Gas Consensus: No Ethereum fees, zero crypto speculation.\n• Dual-Persistence Parity: Relational SQLite synced with immutable JSON.\n• Self-Healing: Any database modification triggers instant peer block repair."
    p_sm2.font.name = "Arial"
    p_sm2.font.size = Pt(9)
    p_sm2.font.color.rgb = C_WHITE
    p_sm2.space_before = Pt(4)

    # Right: 4 Architecture Pillar Cards
    pillars = [
        ("Pillar 1: Zero-Gas-Fee Proof-of-Work Blockchain",
         "Enterprise PoW consensus (Difficulty 4: '0000...'). No Ethereum gas fees. Synchronizes fast SQLite with immutable blockchain.json. Tamper detection in 0.04s.",
         C_CYAN),
        ("Pillar 2: Multimodal Gemini AI OCR Pipeline",
         "Google Gemini Multimodal Vision API directly ingests raw certificate scans and PDFs. In 1.8 seconds, it extracts Student Roll, Program, and DOB into structured JSON, eliminating 95% of typing errors.",
         C_GOLD),
        ("Pillar 3: Dynamic 60s QR & AES-256 DOB Protected PDFs",
         "Student wallet generates an HMAC-salted QR code refreshing every 60 seconds (anti-screenshot). Downloaded stamped PDFs lock via AES-256 with the student's birthdate (DDMMYYYY).",
         C_GREEN),
        ("Pillar 4: 3D WebGL Holographic Verification",
         "In-browser Three.js engine renders a zero-gravity parchment certificate with gold crest and rainbow diffraction. Verifiers can inspect micro-print and flip the certificate 180° to inspect PoW block hashes.",
         C_PURPLE)
    ]

    p_top = 1.6
    for idx, (p_title, p_desc, p_col) in enumerate(pillars):
        p_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.8), Inches(p_top), Inches(6.7), Inches(1.22))
        p_card.fill.solid()
        p_card.fill.fore_color.rgb = C_CARD
        p_card.line.color.rgb = C_CARD_BORDER
        p_card.line.width = Pt(1.2)
        tf_p = p_card.text_frame
        tf_p.word_wrap = True
        tf_p.margin_left = Inches(0.25)
        tf_p.margin_right = Inches(0.25)
        tf_p.margin_top = Inches(0.12)

        pt1 = tf_p.paragraphs[0]
        pt1.text = p_title
        pt1.font.name = "Arial"
        pt1.font.size = Pt(11)
        pt1.font.bold = True
        pt1.font.color.rgb = p_col

        pt2 = tf_p.add_paragraph()
        pt2.text = p_desc
        pt2.font.name = "Arial"
        pt2.font.size = Pt(8.5)
        pt2.font.color.rgb = C_WHITE
        pt2.space_before = Pt(3)

        p_top += 1.32

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 4: UNIQUE VALUE PROPOSITION (MANDATORY POINT 3)
    # ═══════════════════════════════════════════════════════════════════════════
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_top_bar(s4, "MANDATORY POINT 3 · UNIQUE VALUE PROPOSITION", "Strategic Differentiation: Why Not DigiLocker?", C_GOLD)

    # Top VC Metaphor Banner
    vc_banner = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.7), Inches(0.65))
    vc_banner.fill.solid()
    vc_banner.fill.fore_color.rgb = C_DARK_CARD
    vc_banner.line.color.rgb = C_GOLD
    vc_banner.line.width = Pt(1.4)
    tf_vb = vc_banner.text_frame
    tf_vb.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_vb = tf_vb.paragraphs[0]
    p_vb.text = "THE VC METAPHOR: 'DigiLocker is a citizen storage cupboard. Satyameva is the biometric lock, digital seal, and origin proof that guarantees what goes into that cupboard can never be forged.'"
    p_vb.font.name = "Arial"
    p_vb.font.size = Pt(10)
    p_vb.font.bold = True
    p_vb.font.italic = True
    p_vb.font.color.rgb = C_GOLD
    p_vb.alignment = PP_ALIGN.CENTER

    # 6-Row Comparison Matrix Table
    rows = 7
    cols = 3
    left = Inches(0.8)
    top = Inches(2.35)
    width = Inches(11.7)
    height = Inches(3.6)

    table_shape = s4.shapes.add_table(rows, cols, left, top, width, height)
    tbl = table_shape.table
    tbl.columns[0].width = Inches(3.2)
    tbl.columns[1].width = Inches(4.2)
    tbl.columns[2].width = Inches(4.3)

    diff_table_data = [
        ("EVALUATION CRITERIA", "GOVERNMENT DIGILOCKER (C2C)", "SATYAMEVA AEGIS (OUR B2B SOLUTION)"),
        ("Architecture & Role", "Citizen Storage Locker (C2C cloud repository)", "Institutional Security & Verification Engine (B2B SaaS)"),
        ("Verification Speed", "Manual download & inspection (14–21 days)", "Instant in under 60 seconds (Automated Engine)"),
        ("Global Recruiter Access", "FAILS: Requires Indian Aadhaar & active OTP", "FRICTIONLESS: Global recruiters verify in 60s without login"),
        ("Institutional B2B Console", "Zero university telemetry or fraud analytics", "Full governance console: fraud tracking & license management"),
        ("Physical Print Protection", "Printed PDF loses all security features", "Permanent institutional QR + AES-256 DOB password encryption"),
        ("Strategic Alignment", "Generic cloud document repository", "Complementary origin protocol: feeds verified data into DigiLocker & ABC")
    ]

    for r_idx, row_data in enumerate(diff_table_data):
        for c_idx, cell_text in enumerate(row_data):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = cell_text
            p = cell.text_frame.paragraphs[0]
            p.font.name = "Arial"
            if r_idx == 0:
                p.font.size = Pt(9.5)
                p.font.bold = True
                p.font.color.rgb = C_GOLD if c_idx == 2 else C_WHITE
                p.alignment = PP_ALIGN.CENTER
                cell.fill.solid()
                cell.fill.fore_color.rgb = C_DARK_CARD
            else:
                p.font.size = Pt(8.5)
                cell.fill.solid()
                if c_idx == 2:
                    p.font.bold = True
                    p.font.color.rgb = C_CYAN
                    cell.fill.fore_color.rgb = RGBColor(16, 28, 48)
                elif c_idx == 1:
                    p.font.color.rgb = C_MUTED
                    cell.fill.fore_color.rgb = C_CARD
                else:
                    p.font.bold = True
                    p.font.color.rgb = C_WHITE
                    cell.fill.fore_color.rgb = C_DARK_CARD

    # Bottom Benchmarks Strip
    bench = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.75))
    bench.fill.solid()
    bench.fill.fore_color.rgb = C_CARD
    bench.line.color.rgb = C_CYAN
    bench.line.width = Pt(1.2)
    tf_b = bench.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = "FORENSIC SECURITY BENCHMARKS (24/24 PASSED):  • Tamper Detection: 0.04s (40 ms)  • False Positive Rate: Absolute 0.0%  • Salt Collisions: 0/50 with PBKDF2  • Nonce Tampering: Auto-rejected"
    p_b.font.name = "Arial"
    p_b.font.size = Pt(9.5)
    p_b.font.bold = True
    p_b.font.color.rgb = C_WHITE
    p_b.alignment = PP_ALIGN.CENTER

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 5: MARKET OPPORTUNITY (MANDATORY POINT 4)
    # ═══════════════════════════════════════════════════════════════════════════
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5)
    add_top_bar(s5, "MANDATORY POINT 4 · MARKET OPPORTUNITY", "Market Sizing: Capturing India's ₹2,400 Cr Verification Market", C_CYAN)

    # 3 Sizing Cards (TAM, SAM, SOM)
    m_cards = [
        ("TAM: Total Addressable Market",
         "₹2,400+ CRORES",
         "• 1,100+ Recognized Indian Universities\n• 45,000+ Higher Education Colleges\n• 40 Million+ Enrolled Students in India\n• 1.5 Crore degrees & diplomas issued annually\n• Corporate BGV & background checks growing at 14.5% CAGR.",
         C_GOLD),
        ("SAM: Serviceable Addressable Market",
         "₹360 CRORES",
         "• 350+ Tier-1 & Tier-2 Universities\n• Private, Deemed, and State Technical Universities\n• NEP 2020 National Academic Depository mandate\n• NAAC Criterion 2 digitization requirements\n• Institutions with active placement cells & international alumni.",
         C_CYAN),
        ("SOM: Serviceable Obtainable Market",
         "₹12 – 45 LAKHS (Y1-Y2)",
         "• Initial deployment across 3 Jaypee Campuses (JUIT Waknaghat, JIIT Noida, JUET Guna)\n• 15,000+ active student records\n• Expansion to 30 North India Engineering HEIs in Year 2\n• Direct pipeline via university placement cell consortia.",
         C_GREEN)
    ]

    m_left = 0.8
    for idx, (title, stat, details, col) in enumerate(m_cards):
        c_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(m_left), Inches(1.6), Inches(3.7), Inches(4.3))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = C_CARD
        c_box.line.color.rgb = C_CARD_BORDER
        c_box.line.width = Pt(1.2)
        tf_c = c_box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = Inches(0.25)
        tf_c.margin_right = Inches(0.25)
        tf_c.margin_top = Inches(0.25)

        p1 = tf_c.paragraphs[0]
        p1.text = title
        p1.font.name = "Arial"
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = tf_c.add_paragraph()
        p2.text = stat
        p2.font.name = "Arial"
        p2.font.size = Pt(20)
        p2.font.bold = True
        p2.font.color.rgb = C_WHITE
        p2.space_before = Pt(8)

        p3 = tf_c.add_paragraph()
        p3.text = details
        p3.font.name = "Arial"
        p3.font.size = Pt(9)
        p3.font.color.rgb = C_MUTED
        p3.space_before = Pt(12)

        m_left += 4.0

    # Bottom Drivers Strip
    drivers = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.8))
    drivers.fill.solid()
    drivers.fill.fore_color.rgb = C_DARK_CARD
    drivers.line.color.rgb = C_GREEN
    drivers.line.width = Pt(1.2)
    tf_d = drivers.text_frame
    tf_d.word_wrap = True
    tf_d.margin_left = Inches(0.25)
    tf_d.margin_right = Inches(0.25)
    tf_d.margin_top = Inches(0.12)
    pd1 = tf_d.paragraphs[0]
    pd1.text = "KEY GROWTH TAILWINDS:"
    pd1.font.name = "Arial"
    pd1.font.size = Pt(9.5)
    pd1.font.bold = True
    pd1.font.color.rgb = C_GREEN
    pd2 = tf_d.add_paragraph()
    pd2.text = "1. Regulatory Mandate: NEP 2020 pushes mandatory verifiable digital records.  2. Corporate BGV Surge: 50,000+ bulk hires during campus placements demand instant APIs.  3. Global Mobility: Foreign universities & visa consulates reject unverified paper prints."
    pd2.font.name = "Arial"
    pd2.font.size = Pt(8.5)
    pd2.font.color.rgb = C_WHITE
    pd2.space_before = Pt(2)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 6: BUSINESS MODEL (MANDATORY POINT 5)
    # ═══════════════════════════════════════════════════════════════════════════
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_top_bar(s6, "MANDATORY POINT 5 · BUSINESS MODEL", "B2B SaaS Licensing, Verification API & >90% Gross Margin", C_GREEN)

    # Stream 1 Card
    s1_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(3.8))
    s1_card.fill.solid()
    s1_card.fill.fore_color.rgb = C_CARD
    s1_card.line.color.rgb = C_CARD_BORDER
    s1_card.line.width = Pt(1.2)
    tf_s1 = s1_card.text_frame
    tf_s1.word_wrap = True
    tf_s1.margin_left = Inches(0.3)
    tf_s1.margin_right = Inches(0.3)
    tf_s1.margin_top = Inches(0.25)

    p = tf_s1.paragraphs[0]
    p.text = "REVENUE STREAM 1: ANNUAL UNIVERSITY SAAS"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    p = tf_s1.add_paragraph()
    p.text = "₹1.5 Lakhs / campus / year"
    p.font.name = "Arial"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_before = Pt(6)

    p = tf_s1.add_paragraph()
    p.text = "• Bulk CSV Degree Issuance Portal with Gemini AI OCR Parsing\n• Self-Sovereign Student Wallets & 60s Dynamic QR Codes\n• Superadmin Governance: Fraud analytics, license telemetry, node health\n• Unlimited credential issuance & registrar block mining\n• Institutional ROI: Saves ₹8–12 Lakhs in clerical inquiries (5x ROI)."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_MUTED
    p.space_before = Pt(10)

    # Stream 2 Card
    s2_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(3.8))
    s2_card.fill.solid()
    s2_card.fill.fore_color.rgb = C_CARD
    s2_card.line.color.rgb = C_CARD_BORDER
    s2_card.line.width = Pt(1.2)
    tf_s2 = s2_card.text_frame
    tf_s2.word_wrap = True
    tf_s2.margin_left = Inches(0.3)
    tf_s2.margin_right = Inches(0.3)
    tf_s2.margin_top = Inches(0.25)

    p = tf_s2.paragraphs[0]
    p.text = "REVENUE STREAM 2: CORPORATE VERIFICATION API"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    p = tf_s2.add_paragraph()
    p.text = "₹10 to ₹25 / verification check"
    p.font.name = "Arial"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_before = Pt(6)

    p = tf_s2.add_paragraph()
    p.text = "• B2B API access for screening agencies (AuthBridge, TCS, Wipro, Infosys)\n• Instant cryptographic response in <5 seconds (eliminating 21-day delays)\n• High volume during campus hiring (50,000+ checks / enterprise)\n• Official tamper-proof verification audit PDF certificate export\n• Zero clerical burden for the host university."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_MUTED
    p.space_before = Pt(10)

    # Unit Economics Banner
    econ = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.25))
    econ.fill.solid()
    econ.fill.fore_color.rgb = C_DARK_CARD
    econ.line.color.rgb = C_GREEN
    econ.line.width = Pt(1.5)
    tf_e = econ.text_frame
    tf_e.word_wrap = True
    tf_e.margin_left = Inches(0.3)
    tf_e.margin_right = Inches(0.3)
    tf_e.margin_top = Inches(0.15)
    p = tf_e.paragraphs[0]
    p.text = "UNIT ECONOMICS & GROSS MARGIN ADVANTAGE (>90% MARGIN):"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p = tf_e.add_paragraph()
    p.text = "Total Institutional Cost of Goods Sold (COGS) is less than ₹0.48 per credential: Gemini AI OCR (₹0.18) + Cloud Storage (₹0.15) + AES-256 PDF Stamping (₹0.06) + Local CPU PoW Mining (₹0.04) + Buffer (₹0.05). Delivering unmatched SaaS profit margins with zero cryptocurrency exposure."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_WHITE
    p.space_before = Pt(3)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 7: FINANCIALS (MANDATORY POINT 6 - WITH PIE CHART & VISUALS)
    # ═══════════════════════════════════════════════════════════════════════════
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7)
    add_top_bar(s7, "MANDATORY POINT 6 · FINANCIALS & SEED ASK", "Financial Projections & ₹25 Lakh Seed Fund Allocation", C_GOLD)

    # Column 1: Ask Pie Chart
    col1 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.2))
    col1.fill.solid()
    col1.fill.fore_color.rgb = C_CARD
    col1.line.color.rgb = C_GOLD
    col1.line.width = Pt(1.2)
    tf_c1 = col1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = Inches(0.2)
    tf_c1.margin_right = Inches(0.2)
    tf_c1.margin_top = Inches(0.15)
    p = tf_c1.paragraphs[0]
    p.text = "₹25 LAKH SEED ALLOCATION"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p.alignment = PP_ALIGN.CENTER

    if os.path.exists(IMG_PIE):
        s7.shapes.add_picture(IMG_PIE, Inches(0.9), Inches(2.05), Inches(3.5), Inches(2.7))

    tf_c1_bot = col1.text_frame
    p_b1 = tf_c1.add_paragraph()
    p_b1.text = "• 40% (₹10.0L): Multi-Node Infra\n• 30% (₹7.5L): Multi-Campus Pilot\n• 20% (₹5.0L): Cert-In Audit & IP\n• 10% (₹2.5L): Legal & Compliance"
    p_b1.font.name = "Arial"
    p_b1.font.size = Pt(8.5)
    p_b1.font.color.rgb = C_WHITE
    p_b1.space_before = Pt(190)

    # Column 2: COGS Donut Chart
    col2 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.2))
    col2.fill.solid()
    col2.fill.fore_color.rgb = C_CARD
    col2.line.color.rgb = C_GREEN
    col2.line.width = Pt(1.2)
    tf_c2 = col2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = Inches(0.2)
    tf_c2.margin_right = Inches(0.2)
    tf_c2.margin_top = Inches(0.15)
    p = tf_c2.paragraphs[0]
    p.text = "UNIT COST COGS (< ₹0.48)"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.alignment = PP_ALIGN.CENTER

    if os.path.exists(IMG_COGS):
        s7.shapes.add_picture(IMG_COGS, Inches(4.9), Inches(2.05), Inches(3.5), Inches(2.7))

    p_b2 = tf_c2.add_paragraph()
    p_b2.text = "• Gemini AI Extraction: ₹0.18\n• Cloud Storage Alloc: ₹0.15\n• AES-256 PDF Stamping: ₹0.06\n• PoW Mining CPU: ₹0.04\n• Reserve / Buffer: ₹0.05"
    p_b2.font.name = "Arial"
    p_b2.font.size = Pt(8.5)
    p_b2.font.color.rgb = C_WHITE
    p_b2.space_before = Pt(190)

    # Column 3: ARR Bar Chart
    col3 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.2))
    col3.fill.solid()
    col3.fill.fore_color.rgb = C_CARD
    col3.line.color.rgb = C_CYAN
    col3.line.width = Pt(1.2)
    tf_c3 = col3.text_frame
    tf_c3.word_wrap = True
    tf_c3.margin_left = Inches(0.2)
    tf_c3.margin_right = Inches(0.2)
    tf_c3.margin_top = Inches(0.15)
    p = tf_c3.paragraphs[0]
    p.text = "3-YEAR ARR PROJECTION"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.alignment = PP_ALIGN.CENTER

    if os.path.exists(IMG_ARR):
        s7.shapes.add_picture(IMG_ARR, Inches(8.9), Inches(2.05), Inches(3.5), Inches(2.7))

    p_b3 = tf_c3.add_paragraph()
    p_b3.text = "• Year 1 (Pilot): ₹12 Lakhs ARR (8 HEIs)\n• Year 2 (Regional): ₹45 Lakhs ARR (30 HEIs)\n• Year 3 (National): ₹1.05 Crores ARR (70+ HEIs)\n• Cash-flow positive by Month 14."
    p_b3.font.name = "Arial"
    p_b3.font.size = Pt(8.5)
    p_b3.font.color.rgb = C_WHITE
    p_b3.space_before = Pt(190)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 8: FUTURE SCOPE & ROADMAP (MANDATORY POINT 7)
    # ═══════════════════════════════════════════════════════════════════════════
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8)
    add_top_bar(s8, "MANDATORY POINT 7 · FUTURE SCOPE", "Future Scope & Incubation Scaling Roadmap", C_PURPLE)

    # 3 Phase Horizon Cards
    phases = [
        ("PHASE 1: PILOT & JAYPEE HARDENING",
         "MONTHS 1 – 6",
         "• Live Pilot Deployment across JUIT Waknaghat, JIIT Noida, and JUET Guna\n• Onboard 5,000+ real student graduation records\n• Indian Provisional Patent filing for Dynamic 60s Salted QR Protocol\n• Complete official Cert-In government cybersecurity audit.",
         C_GOLD),
        ("PHASE 2: NATIONAL INTEGRATION",
         "MONTHS 7 – 18",
         "• DigiLocker & Academic Bank of Credits (ABC) official API Gateway integration\n• Scale to 30 North India State & Private Universities\n• Enterprise B2B verification partnerships with top screening agencies (AuthBridge, TCS)\n• Achieve operational cash-flow positivity.",
         C_CYAN),
        ("PHASE 3: GLOBAL TRUST BRIDGE",
         "MONTHS 19 – 36",
         "• Cross-Border Verification Gateway for WES, foreign universities & embassies\n• NEP 2020 internationalization trust bridge for Indian scholars abroad\n• Scale to 70+ higher education institutions reaching ₹1.05 Crores ARR\n• Expand to corporate certifications and state skill development councils.",
         C_GREEN)
    ]

    p_left = 0.8
    for idx, (p_title, p_time, p_body, p_col) in enumerate(phases):
        p_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(p_left), Inches(1.6), Inches(3.7), Inches(4.3))
        p_box.fill.solid()
        p_box.fill.fore_color.rgb = C_CARD
        p_box.line.color.rgb = C_CARD_BORDER
        p_box.line.width = Pt(1.2)
        tf_pb = p_box.text_frame
        tf_pb.word_wrap = True
        tf_pb.margin_left = Inches(0.25)
        tf_pb.margin_right = Inches(0.25)
        tf_pb.margin_top = Inches(0.25)

        p = tf_pb.paragraphs[0]
        p.text = p_title
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = p_col

        p = tf_pb.add_paragraph()
        p.text = p_time
        p.font.name = "Arial"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.space_before = Pt(6)

        p = tf_pb.add_paragraph()
        p.text = p_body
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.color.rgb = C_MUTED
        p.space_before = Pt(12)

        p_left += 4.0

    # Closing Ask / Contact Strip
    close_strip = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.8))
    close_strip.fill.solid()
    close_strip.fill.fore_color.rgb = C_DARK_CARD
    close_strip.line.color.rgb = C_GOLD
    close_strip.line.width = Pt(1.4)
    tf_cs = close_strip.text_frame
    tf_cs.word_wrap = True
    tf_cs.margin_left = Inches(0.3)
    tf_cs.margin_right = Inches(0.3)
    tf_cs.margin_top = Inches(0.12)
    p = tf_cs.paragraphs[0]
    p.text = "THE ASK AT RIDE HACK '26: ₹25 Lakhs Incubation & Multi-Node Hardware Deployment"
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p = tf_cs.add_paragraph()
    p.text = "Join us in safeguarding the academic reputation of Indian universities. Live working prototype deployed at JUIT Waknaghat. Thank you!"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.color.rgb = C_WHITE
    p.space_before = Pt(2)

    prs.save(OUT_PPTX)
    print(f"[OK] Official 8-Slide RIDE Hack PPTX saved at: {OUT_PPTX}")


def create_presentation_pdf():
    """Generates the 16:9 widescreen PDF presentation matching the 8 slides."""
    # Render from pptx using reportlab 16:9 widescreen pages
    PAGE_W = 11.0 * inch
    PAGE_H = 6.1875 * inch  # 16:9 aspect ratio

    doc = SimpleDocTemplate(
        OUT_PDF,
        pagesize=(PAGE_W, PAGE_H),
        leftMargin=0.4 * inch,
        rightMargin=0.4 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch,
        title="Satyameva Aegis - Official RIDE Hack '26 Grand Finale Pitch Deck",
        author="Satyameva Aegis (Team ID: 10)",
    )

    s_top_pill = ParagraphStyle("TopPill", fontName="SegoeUI-Bold", fontSize=8.5, leading=11, textColor=colors.HexColor("#D4AF37"), alignment=TA_CENTER)
    s_slide_title = ParagraphStyle("SlideTitle", fontName="SegoeUI-Bold", fontSize=15, leading=19, textColor=colors.white, alignment=TA_LEFT)
    s_card_title = ParagraphStyle("CardTitle", fontName="SegoeUI-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#38BDF8"))
    s_card_body = ParagraphStyle("CardBody", fontName="SegoeUI", fontSize=8, leading=11, textColor=colors.HexColor("#F8FAFC"))
    s_muted = ParagraphStyle("CardMuted", fontName="SegoeUI", fontSize=7.5, leading=10.5, textColor=colors.HexColor("#94A3B8"))

    story = []

    def make_header_table(pill_text, title_text, pill_col="#D4AF37"):
        p_pill = Paragraph(f"<b>{pill_text}</b>", ParagraphStyle("Pill", fontName="SegoeUI-Bold", fontSize=8, leading=10, textColor=colors.HexColor(pill_col), alignment=TA_CENTER))
        p_t = Paragraph(f"<b>{title_text}</b>", s_slide_title)
        t = Table([[p_pill], [p_t]], colWidths=[10.2 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0B1120")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
        ]))
        return t

    # Define slide background callback to ensure all slides have dark midnight navy canvas
    def draw_slide_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#0B1120"))
        canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        canvas.restoreState()

    # SLIDE 1: Cover & Core Founding Team
    p_mandate = Paragraph(
        "<b>JAYPEE UNIVERSITY OF INFORMATION TECHNOLOGY &nbsp;&middot;&nbsp; IIC RIDEHACK'26 GRAND FINALE &nbsp;&middot;&nbsp; JIIT NOIDA</b>",
        ParagraphStyle("MandatePill", fontName="SegoeUI-Bold", fontSize=8.5, leading=11, textColor=colors.HexColor("#D4AF37"), alignment=TA_CENTER)
    )
    t_mandate = Table([[p_mandate]], colWidths=[10.2 * inch])
    t_mandate.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#D4AF37")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_mandate)
    story.append(Spacer(1, 6))

    cov_left_text = (
        '<b><font size="16" color="#FFFFFF">SATYAMEVA AEGIS</font></b><br/>'
        '<b><font size="9.5" color="#38BDF8">Decentralized Academic Credential Integrity &amp; Instant Verification Engine</font></b><br/><br/>'
        'Eradicating Indian academic credential counterfeiting by compressing verification from 21 days down to 60 seconds with Zero Gas Fees, Google Gemini AI OCR, and 3D Holographic Proofs.<br/><br/>'
        '<font color="#D4AF37"><b>KEY VENTURE MULTIPLIERS:</b></font><br/>'
        '&bull; <b>Turnaround:</b> 14&ndash;21 Days &rarr; &lt;60 Seconds (99.9% clerical reduction)<br/>'
        '&bull; <b>Institutional Unit Cost:</b> &lt; &#8377;0.48 / Credential (Gross Margin &gt; 90%)<br/>'
        '&bull; <b>Zero Gas Fees:</b> Private PoW blockchain immune to crypto volatility<br/>'
        '&bull; <b>Market Scope:</b> 1,100+ Indian Universities &amp; 40M+ Higher Ed Students<br/><br/>'
        '<font color="#D4AF37"><b>Tech Incubation:</b> Dept. of CSE, JUIT Waknaghat (Solan, H.P.)<br/>'
        '<b>Consortium Deployment:</b> JUIT &middot; JIIT &middot; JUET Campuses</font>'
    )
    p_cov_left = Paragraph(
        cov_left_text,
        ParagraphStyle("CovLeft", fontName="SegoeUI", fontSize=7.8, leading=11.2, textColor=colors.HexColor("#CBD5E1"))
    )
    t_left = Table([[p_cov_left]], colWidths=[4.9 * inch])
    t_left.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#131D31")),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#1E3A5F")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))

    pdf_members = [
        ("A. Praneeth Sai", "FOUNDER & ARCHITECTURE LEAD", "#38BDF8",
         "B.Tech CSE Core (2026–2030) · JUIT Waknaghat",
         "Zero-Gas Private Blockchain · Web3 Architecture · SHA-256 Merkle Ledger"),
        ("Anushka Bansal", "CO-FOUNDER & DATA LEAD", "#D4AF37",
         "B.Tech CSE Core (2026–2030) · JUIT Waknaghat",
         "Data Integrity · Academic Record Schema · Institutional Portal Integration"),
        ("Shashank Ray", "CO-FOUNDER & AI MODEL LEAD", "#10B981",
         "B.Tech CSE Core (2026–2030) · JUIT Waknaghat",
         "Gemini AI Vision Engine · Multimodal OCR · Tamper & Pixel Forgery Detection"),
        ("Sameeksha Chandel", "CO-FOUNDER & PRODUCT LEAD", "#C084FC",
         "B.Tech CSE Core (2026–2030) · JUIT Waknaghat",
         "Product Strategy · UI/UX Verification Portal · BGV Enterprise Workflow"),
    ]

    p_team_hdr = Paragraph(
        '<b>CORE FOUNDING TEAM &nbsp;&middot;&nbsp; TEAM ID: 10 (JUIT WAKNAGHAT)</b>',
        ParagraphStyle('H_Team', fontName='SegoeUI-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#38BDF8'), alignment=TA_CENTER)
    )
    t_hdr = Table([[p_team_hdr]], colWidths=[5.15 * inch])
    t_hdr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor('#38BDF8')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))

    right_flowables = [t_hdr, Spacer(1, 4)]
    for name, role, color, degree, focus in pdf_members:
        card_p = Paragraph(
            f'<b><font color="#FFFFFF" size="8.5">{name}</font></b> &nbsp;&nbsp;|&nbsp;&nbsp; '
            f'<b><font color="{color}" size="8">{role}</font></b><br/>'
            f'<font color="#94A3B8" size="7">{degree}</font><br/>'
            f'<b><font color="{color}" size="7">Core Domain:</font></b> <font color="#F8FAFC" size="7">{focus}</font>',
            ParagraphStyle(f"P_{name.replace(' ', '_')}", fontName='SegoeUI', fontSize=7.2, leading=9.5, textColor=colors.HexColor('#94A3B8'))
        )
        t_card = Table([[card_p]], colWidths=[5.15 * inch])
        t_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#131D31')),
            ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor(color)),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        right_flowables.append(t_card)
        right_flowables.append(Spacer(1, 3))

    t_right = Table([[right_flowables]], colWidths=[5.15 * inch])
    t_right.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 0),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    t_cov = Table([[t_left, t_right]], colWidths=[4.95 * inch, 5.25 * inch])
    t_cov.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_cov)
    story.append(PageBreak())

    # SLIDE 2: Problem Statement
    story.append(make_header_table("MANDATORY POINT 1 · PROBLEM STATEMENT", "India's Academic Trust Deficit: The ₹1,500 Fake Degree Scandal", "#EF4444"))
    story.append(Spacer(1, 6))
    prob_p = Paragraph(
        "<font color='#EF4444'><b>1. ₹1,500 Counterfeit Syndicates:</b></font><br/>"
        "Over 40,000 fake degrees detected annually in India. Telegram syndicates sell replica marksheets with duplicate university seals within 24 hours. Physical paper ink cannot be distinguished from clones by corporate HR.<br/><br/>"
        "<font color='#D4AF37'><b>2. 14–21 Day Verification Bottlenecks:</b></font><br/>"
        "Corporate background screeners (TCS, Wipro, AuthBridge) rely on manual speed-post letters & registrar emails. Costs universities ₹12–18L annually in clerical overhead and severely stalls graduates' jobs & foreign visas.<br/><br/>"
        "<font color='#38BDF8'><b>3. Centralized SQL Single Point of Failure:</b></font><br/>"
        "Centralized relational databases have zero mathematical auditability. A compromised registrar password or insider database access alters academic records silently with zero immutable cryptographic trail.",
        s_card_body
    )
    t_p2 = Table([[prob_p, RLImage(IMG_PROBLEM, width=4.5*inch, height=2.5*inch)]], colWidths=[5.5*inch, 4.7*inch])
    t_p2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#131D31")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A5F")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_p2)
    story.append(PageBreak())

    # SLIDE 3: Proposed Solution
    story.append(make_header_table("MANDATORY POINT 2 · PROPOSED SOLUTION", "4-Pillar Deep-Tech Architecture: Zero Gas, AI & 3D Holograms", "#10B981"))
    story.append(Spacer(1, 6))
    sol_p = Paragraph(
        "<font color='#38BDF8'><b>Pillar 1: Zero-Gas-Fee Proof-of-Work Blockchain</b></font><br/>"
        "Custom enterprise PoW consensus (Difficulty 4). Zero crypto volatility. Dual-Persistence Parity synchronizes SQLite with immutable blockchain.json.<br/><br/>"
        "<font color='#D4AF37'><b>Pillar 2: Multimodal Gemini AI OCR Pipeline</b></font><br/>"
        "Google Gemini Multimodal Vision API directly parses certificate scans in 1.8s into structured JSON, eliminating 95% of clerical typing errors.<br/><br/>"
        "<font color='#10B981'><b>Pillar 3: Dynamic 60s QR & AES-256 DOB Protected PDFs</b></font><br/>"
        "Student digital wallets generate HMAC-salted dynamic QRs (anti-screenshot). Downloaded stamped PDFs lock with student birthdate.<br/><br/>"
        "<font color='#7C3AED'><b>Pillar 4: 3D WebGL Holographic Verification</b></font><br/>"
        "In-browser Three.js engine renders zero-gravity parchment with gold crest, rainbow diffraction, and 180° cryptographic block flip.",
        s_card_body
    )
    t_p3 = Table([[RLImage(IMG_SOLUTION, width=4.5*inch, height=2.5*inch), sol_p]], colWidths=[4.7*inch, 5.5*inch])
    t_p3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#131D31")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A5F")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_p3)
    story.append(PageBreak())

    # SLIDE 4: Unique Value Proposition
    story.append(make_header_table("MANDATORY POINT 3 · UNIQUE VALUE PROPOSITION", "Strategic Differentiation: Why Not DigiLocker?", "#D4AF37"))
    story.append(Spacer(1, 6))
    uvp_table_data = [
        [Paragraph("<b>Criteria</b>", s_top_pill), Paragraph("<b>Government DigiLocker (C2C)</b>", s_top_pill), Paragraph("<b>Satyameva Aegis (Our B2B SaaS)</b>", s_top_pill)],
        [Paragraph("<b>Role</b>", s_card_body), Paragraph("Citizen Storage Locker", s_muted), Paragraph("<b>Institutional Verification Engine</b>", s_card_body)],
        [Paragraph("<b>Turnaround</b>", s_card_body), Paragraph("14–21 Days manual inspection", s_muted), Paragraph("<b>Instant in &lt; 60 seconds</b>", s_card_body)],
        [Paragraph("<b>Global Recruiter</b>", s_card_body), Paragraph("FAILS: Requires Aadhaar & OTP", s_muted), Paragraph("<b>FRICTIONLESS: Zero-Login 60s validation</b>", s_card_body)],
        [Paragraph("<b>B2B Console</b>", s_card_body), Paragraph("Zero university fraud telemetry", s_muted), Paragraph("<b>Full registrar governance dashboard</b>", s_card_body)],
        [Paragraph("<b>Paper Security</b>", s_card_body), Paragraph("Printed PDF loses all security", s_muted), Paragraph("<b>Permanent QR + AES-256 DOB Password</b>", s_card_body)],
    ]
    t_uvp = Table(uvp_table_data, colWidths=[2.2*inch, 3.8*inch, 4.2*inch])
    t_uvp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#131D31")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A5F")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1E3A5F")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_uvp)
    story.append(PageBreak())

    # SLIDE 5: Market Opportunity
    story.append(make_header_table("MANDATORY POINT 4 · MARKET OPPORTUNITY", "Market Sizing: Capturing India's ₹2,400 Cr Verification Market", "#38BDF8"))
    story.append(Spacer(1, 6))
    c_tam = Paragraph("<b>TAM: ₹2,400+ CRORES</b><br/>1,100+ Universities, 45,000+ Colleges, 40 Million+ Higher Ed Students in India. 1.5 Cr degrees issued annually.", s_card_body)
    c_sam = Paragraph("<b>SAM: ₹360 CRORES</b><br/>350+ Tier-1 & Tier-2 Universities, Deemed & Technical Institutes adopting NEP 2020 & NAAC Criterion 2.", s_card_body)
    c_som = Paragraph("<b>SOM: ₹12–45 LAKHS</b><br/>Initial pilot across 3 Jaypee Campuses (JUIT, JIIT, JUET) onboarding 15,000+ records, expanding to 30 HEIs.", s_card_body)
    t_mkt = Table([[c_tam, c_sam, c_som]], colWidths=[3.4*inch, 3.4*inch, 3.4*inch])
    t_mkt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#131D31")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A5F")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_mkt)
    story.append(PageBreak())

    # SLIDE 6: Business Model
    story.append(make_header_table("MANDATORY POINT 5 · BUSINESS MODEL", "B2B SaaS Licensing, Verification API & >90% Gross Margin", "#10B981"))
    story.append(Spacer(1, 6))
    bm_left = Paragraph("<b>STREAM 1: ANNUAL UNIVERSITY SAAS</b><br/><b>₹1.5 Lakhs / campus / year</b><br/>Bulk issuance, Gemini OCR, student wallets, fraud telemetry. Saves universities ₹8–12L in clerical overhead (5x ROI).", s_card_body)
    bm_right = Paragraph("<b>STREAM 2: CORPORATE VERIFICATION API</b><br/><b>₹10 to ₹25 / check</b><br/>B2B API for background screening firms (TCS, Wipro, AuthBridge). Instant validation in &lt;5s with official audit PDF export.", s_card_body)
    t_bm = Table([[bm_left, bm_right]], colWidths=[5.1*inch, 5.1*inch])
    t_bm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#131D31")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A5F")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_bm)
    story.append(PageBreak())

    # SLIDE 7: Financials & Ask (WITH PIE CHART)
    story.append(make_header_table("MANDATORY POINT 6 · FINANCIALS & SEED ASK", "Financial Projections & ₹25 Lakh Seed Fund Allocation (With Charts)", "#D4AF37"))
    story.append(Spacer(1, 4))
    t_fin = Table([[
        RLImage(IMG_PIE, width=3.2*inch, height=2.4*inch),
        RLImage(IMG_COGS, width=3.2*inch, height=2.4*inch),
        RLImage(IMG_ARR, width=3.2*inch, height=2.4*inch)
    ]], colWidths=[3.4*inch, 3.4*inch, 3.4*inch])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#131D31")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A5F")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_fin)
    story.append(PageBreak())

    # SLIDE 8: Future Scope
    story.append(make_header_table("MANDATORY POINT 7 · FUTURE SCOPE", "Future Scope & Incubation Scaling Roadmap", "#7C3AED"))
    story.append(Spacer(1, 6))
    f_p1 = Paragraph("<b>PHASE 1: JAYPEE PILOT (M1-6)</b><br/>Onboard JUIT, JIIT, JUET with 5,000+ graduation records. Provisional patent filing for Dynamic 60s Salted QR & Cert-In security audit.", s_card_body)
    f_p2 = Paragraph("<b>PHASE 2: NATIONAL EXPANSION (M7-18)</b><br/>DigiLocker & ABC API Gateway origin integration. Expand to 30 North India universities. Enterprise BGV corporate contracts.", s_card_body)
    f_p3 = Paragraph("<b>PHASE 3: GLOBAL TRUST BRIDGE (M19-36)</b><br/>Cross-border embassy & WES verification bridge under NEP 2020. Reach ₹1.05 Cr ARR across 70+ higher education institutions.", s_card_body)
    t_fut = Table([[f_p1, f_p2, f_p3]], colWidths=[3.4*inch, 3.4*inch, 3.4*inch])
    t_fut.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#131D31")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A5F")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_fut)

    doc.build(story, onFirstPage=draw_slide_background, onLaterPages=draw_slide_background)
    print(f"[OK] Official 8-Slide RIDE Hack PDF saved at: {OUT_PDF}")


def create_standalone_script_pdf():
    """Generates the standalone 10-15 minute Pitch Speaking Script in Hinglish + English."""
    doc = SimpleDocTemplate(
        OUT_SCRIPT,
        pagesize=A4,
        leftMargin=14*mm,
        rightMargin=14*mm,
        topMargin=12*mm,
        bottomMargin=12*mm,
        title="Satyameva Aegis - RIDE Hack '26 Grand Finale Pitch Speaking Script",
        author="Satyameva Aegis (Team ID: 10)",
    )

    s_hdr = ParagraphStyle("ScriptHdr", fontName="SegoeUI-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#0B1120"), alignment=TA_CENTER)
    s_sub = ParagraphStyle("ScriptSub", fontName="SegoeUI-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#0284C7"), alignment=TA_CENTER)
    s_sec = ParagraphStyle("ScriptSec", fontName="SegoeUI-Bold", fontSize=10.5, leading=14, textColor=colors.white)
    s_spk = ParagraphStyle("ScriptSpeaker", fontName="SegoeUI-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#D4AF37"))
    s_body = ParagraphStyle("ScriptBody", fontName="SegoeUI", fontSize=8.5, leading=12.5, textColor=colors.HexColor("#0F172A"), alignment=TA_JUSTIFY)
    s_quote = ParagraphStyle("ScriptQuote", fontName="SegoeUI-Italic", fontSize=8.5, leading=12.5, textColor=colors.HexColor("#065F46"), alignment=TA_JUSTIFY)

    story = []

    def make_sec_hdr(title, bg="#0B1120"):
        t = Table([[Paragraph(title, s_sec)]], colWidths=[182*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg)),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    # Top Banner
    story.append(Paragraph("SATYAMEVA AEGIS · RIDE HACK '26 GRAND FINALE", s_hdr))
    story.append(Paragraph("Official 10–15 Minute Pitch Speaking Script & Role Playbook (Team ID: 10)", s_sub))
    story.append(Paragraph("Grand Finale: Jaypee Institute of Information Technology (JIIT), Noida · 01 Nov 2026", s_sub))
    story.append(Spacer(1, 4))

    # Relay Schedule Table
    relay_data = [
        [Paragraph("<b>Time Window</b>", s_spk), Paragraph("<b>Speaker & Role</b>", s_spk), Paragraph("<b>Mandatory Slide Focus</b>", s_spk)],
        [Paragraph("<b>0:00 – 3:30</b> (3.5m)", s_body), Paragraph("<b>A. Praneeth Sai</b><br/>Founder & Chief Architect", s_body), Paragraph("Slide 1 (Cover & Mandate) + Slide 2 (Problem Statement: ₹1,500 Fake Degree Scandal)", s_body)],
        [Paragraph("<b>3:30 – 6:30</b> (3.0m)", s_body), Paragraph("<b>A. Praneeth Sai & Shashank Ray</b><br/>Architecture & AI Lead", s_body), Paragraph("Slide 3 (Proposed Solution: 4-Pillar Deep-Tech Engine, PoW Blockchain & Gemini AI)", s_body)],
        [Paragraph("<b>6:30 – 9:00</b> (2.5m)", s_body), Paragraph("<b>Anushka Bansal</b><br/>Data Lead", s_body), Paragraph("Slide 4 (Unique Value Proposition: Why Not DigiLocker? 6-Point Comparison Matrix)", s_body)],
        [Paragraph("<b>9:00 – 11:30</b> (2.5m)", s_body), Paragraph("<b>Sameeksha Chandel</b><br/>Product Lead", s_body), Paragraph("Slide 5 (Market Opportunity: TAM/SAM/SOM) + Slide 6 (Business Model: SaaS Licensing)", s_body)],
        [Paragraph("<b>11:30 – 14:00</b> (2.5m)", s_body), Paragraph("<b>Shashank Ray & Praneeth</b><br/>AI Lead & Founder", s_body), Paragraph("Slide 7 (Financials: Pie Chart & ₹25L Ask) + Slide 8 (Future Scope & Roadmap)", s_body)],
        [Paragraph("<b>14:00 – 15:00</b> (1.0m)", s_body), Paragraph("<b>All Team Members</b>", s_body), Paragraph("Closing Callout, Prototype Handoff & Jury Q&A Defense", s_body)]
    ]
    t_relay = Table(relay_data, colWidths=[36*mm, 52*mm, 94*mm])
    t_relay.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B1120")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_relay)
    story.append(Spacer(1, 5))

    # Slide 1 & 2 Script
    story.append(make_sec_hdr("SLIDES 1 & 2: HOOK, MANDATE & PROBLEM STATEMENT (0:00 – 3:30) — PRANEETH SAI", "#DC2626"))
    story.append(Spacer(1, 2))
    p_s1 = (
        "<b>[Slide 1 Transition]:</b> <i>'Respected Jury members, Vice Chancellor Sir, and esteemed faculty — "
        "India ke higher education ecosystem me har saal 1.1 Crore students graduate hote hain. Lekin unke haath me jo physical paper degree aati hai, "
        "uska origin verify karne ka koi tamper-evident mechanism exist nahi karta. "
        "Aaj Telegram syndicates aur Photoshop ke zariye sirf ₹1,500 me replica university marksheet duplicate rubber seals ke sath 24 ghante me deliver ho jati hai.'</i><br/>"
        "<b>[Slide 2 Transition]:</b> <i>'Is problem ke 3 critical dimensions hain: "
        "First, 40,000 se zyada fake degrees har saal officially detect hoti hain. "
        "Second, background verification firms jaise TCS, Wipro aur AuthBridge ko manual speed-post aur registrar emails par depend karna padta hai, "
        "jisme 14 se 21 din ka time lagta hai aur universities ko ₹12–18 Lakhs clerical overhead me kharch karne padte hain. "
        "Third, traditional SQL databases me agar koi clerk database access karke CGPA alter kar de, toh koi cryptographic audit trail nahi banta. "
        "Is crisis ko permanently solve karne ke liye hamne build kiya hai: <b>Satyameva Aegis</b>.'</i>"
    )
    story.append(Paragraph(p_s1, s_body))
    story.append(Spacer(1, 4))

    # Slide 3 Script
    story.append(make_sec_hdr("SLIDE 3: PROPOSED SOLUTION & 4-PILLAR DEEP-TECH (3:30 – 6:30) — PRANEETH & SHASHANK", "#059669"))
    story.append(Spacer(1, 2))
    p_s3 = (
        "<i>'Satyameva Aegis ek enterprise B2B SaaS aur decentralized trust protocol hai jo 4 deep-tech pillars par operate karta hai:<br/>"
        "• <b>Pillar 1: Zero-Gas-Fee Proof-of-Work Blockchain:</b> Hamne ek private PoW consensus engine implement kiya hai jo Difficulty 4 par operate karta hai. "
        "Isme Ethereum jaisi koi gas fees nahi lagti aur zero cryptocurrency exposure hai. Fast relational SQLite aur immutable JSON ledger me dual parity rehti hai.<br/>"
        "• <b>Pillar 2: Google Gemini Multimodal Vision AI:</b> Registrar office me manual data entry ki zaroorat nahi hai. "
        "Gemini Multimodal AI raw certificate scan ko 1.8 seconds me read karke Student Name, Roll Number, Program aur DOB extract karta hai.<br/>"
        "• <b>Pillar 3: Dynamic 60-Second QR & AES-256 DOB Protected PDFs:</b> Student wallet me HMAC-salted QR banta hai jo har 60 seconds me expire hota hai — "
        "koi screenshot forward karke cheat nahi kar sakta! Aur downloaded PDF student ki date of birth se AES-256 encrypted hoti hai.<br/>"
        "• <b>Pillar 4: 3D WebGL Holographic Verification:</b> In-browser Three.js engine zero-gravity parchment render karta hai jisko flip karke cryptographic PoW block hash inspect kiya ja sakta hai.'</i>"
    )
    story.append(Paragraph(p_s3, s_body))
    story.append(Spacer(1, 4))

    # Slide 4 Script
    story.append(make_sec_hdr("SLIDE 4: UNIQUE VALUE PROPOSITION & DIGILOCKER DEFENSE (6:30 – 9:00) — ANUSHKA BANSAL", "#D4AF37"))
    story.append(Spacer(1, 2))
    p_s4 = (
        "<i>'Respected Jury, sabse frequent question yeh aata hai: <b>\"Jab Government of India ka DigiLocker already exist karta hai, toh universities Satyameva kyu purchase karengi?\"</b><br/>"
        "Sir, difference fundamental hai: <b>DigiLocker ek citizen storage locker (cupboard) hai jahan student file store karta hai. "
        "Par Satyameva us almari ka biometric tamper-evident lock aur institutional origin engine hai jo ensure karta hai ki cupboard ke andar kabhi nakli document ja hi na sake!</b><br/>"
        "1. <b>Foreign Recruiters:</b> DigiLocker me verify karne ke liye Indian Aadhaar aur OTP mandatory hota hai. US/UK ke foreign recruiters ya embassies ke paas Indian Aadhaar nahi hota. Satyameva me zero-login 60-second frictionless verification milti hai.<br/>"
        "2. <b>Institutional B2B Console:</b> DigiLocker universities ko koi fraud analytics ya license telemetry nahi deta. Satyameva registrar office ko complete control deta hai.<br/>"
        "3. <b>Forensic Benchmark:</b> Hamne 24 adversarial attack vectors test kiye hain — silent SQL modification ko Satyameva sirf <b>0.04 seconds (40 ms)</b> me catch karta hai with <b>absolute 0% false positives!</b>'</i>"
    )
    story.append(Paragraph(p_s4, s_body))
    story.append(Spacer(1, 4))

    # Slide 5 & 6 Script
    story.append(make_sec_hdr("SLIDES 5 & 6: MARKET OPPORTUNITY & BUSINESS MODEL (9:00 – 11:30) — SAMEEKSHA CHANDEL", "#0284C7"))
    story.append(Spacer(1, 2))
    p_s56 = (
        "<i>'Market opportunity massive hai: India me 1,100+ universities aur 45,000+ colleges hain jo annual ₹2,400 Crore credential verification market represent karte hain. "
        "Hamara initial target 350+ private aur technical universities hain jinhe NEP 2020 aur NAAC Criterion 2 digitization compliance chahiye.<br/>"
        "Hamara business model high-margin dual monetization streams par based hai:<br/>"
        "1. <b>Annual University B2B SaaS:</b> ₹1.5 Lakhs per campus per year. University ke registrar office ka ₹8–12 Lakhs clerical cost save hota hai — generating a direct <b>5x ROI</b> for the institution.<br/>"
        "2. <b>Corporate Pay-Per-Verify API:</b> Background screening agencies (AuthBridge, TCS, Infosys) se ₹10 to ₹25 per automated verification check charge karte hain.<br/>"
        "Hamara unit cost per document sirf <b>₹0.48</b> hai, resulting in an exceptional <b>Gross Margin exceeding 90%!</b>'</i>"
    )
    story.append(Paragraph(p_s56, s_body))
    story.append(Spacer(1, 4))

    # Slide 7 & 8 Script
    story.append(make_sec_hdr("SLIDES 7 & 8: FINANCIALS, PIE CHART & ₹25L INCUBATION ASK (11:30 – 14:30) — SHASHANK & PRANEETH", "#7C3AED"))
    story.append(Spacer(1, 2))
    p_s78 = (
        "<i>'Slide 7 me hamara financial trajectory aur seed capital allocation clear hai:<br/>"
        "• <b>3-Year ARR Projection:</b> Year 1 me ₹12 Lakhs (Jaypee system + 5 regional HEIs), Year 2 me ₹45 Lakhs (30 HEIs), aur Year 3 me <b>₹1.05 Crores ARR</b> across 70+ higher education institutions nationally.<br/>"
        "• <b>₹25 Lakh Seed Fund Allocation (Pie Chart Breakdown):</b><br/>"
        "  - <b>40% (₹10.0 Lakhs):</b> Dedicated Multi-Node Server Infrastructure across JUIT, JIIT, and JUET nodes.<br/>"
        "  - <b>30% (₹7.5 Lakhs):</b> Multi-Campus Real Student Batch Pilot onboarding 5,000+ records.<br/>"
        "  - <b>20% (₹5.0 Lakhs):</b> Cert-In cybersecurity certification aur provisional patent filing.<br/>"
        "  - <b>10% (₹2.5 Lakhs):</b> Legal, NEP 2020 compliance aur institutional B2B contracts.<br/>"
        "Slide 8 me hamara roadmap clear hai: Pilot Phase ➔ DigiLocker & ABC Origin API Gateway ➔ Global Embassy Verification Bridge under NEP 2020.'</i><br/>"
        "<b>[Closing Handshake]:</b> <i>'Satyameva Aegis is ready, deployed on localhost, and verified with 7 blockchain blocks. We invite the RIDE Hack jury to partner with us in securing the academic future of India. Thank you!'</i>"
    )
    story.append(Paragraph(p_s78, s_body))

    doc.build(story)
    print(f"[OK] Standalone Pitch Speaking Script PDF saved at: {OUT_SCRIPT}")


def render_previews():
    """Renders high-resolution slide previews (150 DPI) from the generated presentation PDF
    and script previews from the generated pitch script PDF into ARTIFACT_DIR."""
    try:
        if os.path.exists(OUT_PDF):
            pdf_doc = pymupdf.open(OUT_PDF)
            for i, page in enumerate(pdf_doc):
                pix = page.get_pixmap(dpi=150)
                out_img = os.path.join(ARTIFACT_DIR, f"slide_preview_{i+1}.png")
                pix.save(out_img)
            print(f"[OK] Rendered {len(pdf_doc)} slide previews to: {ARTIFACT_DIR}")

        if os.path.exists(OUT_SCRIPT):
            script_doc = pymupdf.open(OUT_SCRIPT)
            for i, page in enumerate(script_doc):
                pix = page.get_pixmap(dpi=150)
                out_img = os.path.join(ARTIFACT_DIR, f"script_preview_{i+1}.png")
                pix.save(out_img)
            print(f"[OK] Rendered {len(script_doc)} script previews to: {ARTIFACT_DIR}")
    except Exception as e:
        print(f"[Warning] Failed to render previews: {e}")


def mirror_artifacts():
    targets = [SATYAMEVA_DIR, SIH_DIR, ARTIFACT_DIR]
    files = [OUT_PPTX, OUT_PDF, OUT_SCRIPT]

    for t in targets:
        if os.path.exists(t):
            for f in files:
                dest = os.path.join(t, os.path.basename(f))
                try:
                    shutil.copy2(f, dest)
                except Exception as e:
                    print(f"Warning copying {f} to {dest}: {e}")
            print(f"[OK] Mirrored all final deliverables to: {t}")


if __name__ == '__main__':
    create_pptx_deck()
    create_presentation_pdf()
    create_standalone_script_pdf()
    render_previews()
    mirror_artifacts()

