"""
generate_summary_images_and_pdf.py
Builds the Satyameva Aegis Executive Summary for RIDEHACK'26 with integrated Pie Charts & Data Visualizations.
Includes:
1. Donut Pie Chart: Unit Cost Breakdown (< ₹0.48 / document)
2. Bar Chart: 3-Year ARR Growth Projection (₹12L -> ₹45L -> ₹1.05 Cr)
3. Pie Chart: ₹25 Lakh RIDE Incubation Seed Ask Deployment Allocation
Renders 300 DPI PNG images for each page and a combined Infographic Poster PNG.
Converts the rendered images directly into high-fidelity PDF documents.
"""

import os
import shutil
from PIL import Image
import pymupdf
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Segoe UI TrueType Fonts
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

# Output Paths
DESKTOP_DIR = r"C:\Users\hp\OneDrive\Desktop"
SATYAMEVA_DIR = r"C:\Users\hp\OneDrive\Desktop\Satyameva"
SIH_DIR = r"C:\Users\hp\OneDrive\Desktop\SIH_Aegis"
ARTIFACT_DIR = r"C:\Users\hp\.gemini\antigravity\brain\898a4eb6-926a-417b-9cac-f6e58897bc1b"
CHARTS_DIR = os.path.join(SATYAMEVA_DIR, "assets")
os.makedirs(CHARTS_DIR, exist_ok=True)

PDF_MASTER = os.path.join(DESKTOP_DIR, "SATYAMEVA_RIDEHACK26_EXECUTIVE_SUMMARY.pdf")
IMG_PAGE1 = os.path.join(DESKTOP_DIR, "SATYAMEVA_RIDEHACK26_EXECUTIVE_SUMMARY_PAGE1.png")
IMG_PAGE2 = os.path.join(DESKTOP_DIR, "SATYAMEVA_RIDEHACK26_EXECUTIVE_SUMMARY_PAGE2.png")
IMG_PAGE3 = os.path.join(DESKTOP_DIR, "SATYAMEVA_RIDEHACK26_EXECUTIVE_SUMMARY_PAGE3.png")
IMG_INFOGRAPHIC = os.path.join(DESKTOP_DIR, "SATYAMEVA_RIDEHACK26_EXECUTIVE_SUMMARY_INFOGRAPHIC.png")

CHART_ASK_PIE = os.path.join(CHARTS_DIR, "ask_pie_chart.png")
CHART_COGS_DONUT = os.path.join(CHARTS_DIR, "cogs_donut_chart.png")
CHART_ARR_BAR = os.path.join(CHARTS_DIR, "arr_growth_bar_chart.png")

# Palette
NAVY       = colors.HexColor("#0B1120")
DARK_NAVY  = colors.HexColor("#070B14")
GOLD       = colors.HexColor("#D4AF37")
CYAN       = colors.HexColor("#0284C7")
CYAN_ACC   = colors.HexColor("#06B6D4")
WHITE      = colors.white
LIGHT_GRAY = colors.HexColor("#F8FAFC")
CARD_BG    = colors.HexColor("#F1F5F9")
BORDER_COL = colors.HexColor("#CBD5E1")
TEXT_DARK  = colors.HexColor("#0F172A")
MUTED_TEXT = colors.HexColor("#475569")
GREEN      = colors.HexColor("#059669")
DARK_GREEN = colors.HexColor("#065F46")
RED        = colors.HexColor("#DC2626")
PURPLE     = colors.HexColor("#6D28D9")


def generate_all_charts():
    """Generates 3 brand-aligned high-res charts for the Executive Summary."""
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']

    # 1. Ask Pie Chart (₹25 Lakh Seed Fund Allocation)
    fig, ax = plt.subplots(figsize=(4.2, 3.2), dpi=300)
    labels = [
        'Multi-Node Infra\n(40% · ₹10.0L)',
        'Multi-Campus Pilot\n(30% · ₹7.5L)',
        'Security Audits & IP\n(20% · ₹5.0L)',
        'Legal & B2B Ops\n(10% · ₹2.5L)'
    ]
    sizes = [40, 30, 20, 10]
    colors_pie = ['#0284C7', '#059669', '#D4AF37', '#7C3AED']
    explode = (0.04, 0.03, 0.03, 0.03)

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors_pie,
        autopct='%1.0f%%',
        pctdistance=0.74,
        explode=explode,
        startangle=135,
        textprops={'fontsize': 7.5, 'color': '#0F172A', 'weight': 'bold'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.6, 'antialiased': True}
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontsize(8.5)
        at.set_weight('bold')

    centre_circle = plt.Circle((0, 0), 0.44, fc='white', ec='#CBD5E1', lw=0.8)
    fig.gca().add_artist(centre_circle)
    ax.text(0, 0, '₹25 LAKH\nSEED ASK', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0B1120')
    ax.axis('equal')
    plt.title('₹25 Lakh Seed Fund Allocation', fontsize=9.5, fontweight='bold', color='#0B1120', pad=6)
    plt.tight_layout()
    plt.savefig(CHART_ASK_PIE, bbox_inches='tight', facecolor='#F8FAFC')
    plt.close()

    # 2. COGS Donut Chart (Unit Cost < ₹0.48)
    fig, ax = plt.subplots(figsize=(4.0, 2.7), dpi=300)
    labels_cogs = ['Gemini AI\n(₹0.18)', 'Cloud Store\n(₹0.15)', 'AES-256\n(₹0.06)', 'PoW Node\n(₹0.04)', 'Buffer\n(₹0.05)']
    sizes_cogs = [0.18, 0.15, 0.06, 0.04, 0.05]
    colors_cogs = ['#0284C7', '#059669', '#D4AF37', '#7C3AED', '#64748B']

    wedges, texts, autotexts = ax.pie(
        sizes_cogs,
        labels=labels_cogs,
        colors=colors_cogs,
        autopct='%1.0f%%',
        pctdistance=0.75,
        startangle=120,
        textprops={'fontsize': 7.0, 'color': '#0F172A', 'weight': 'bold'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.4}
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontsize(7.5)
        at.set_weight('bold')

    centre_circle = plt.Circle((0, 0), 0.46, fc='white', ec='#CBD5E1', lw=0.8)
    fig.gca().add_artist(centre_circle)
    ax.text(0, 0, '< ₹0.48\nCOGS\n(>90% GM)', ha='center', va='center', fontsize=7.2, fontweight='bold', color='#065F46')
    ax.axis('equal')
    plt.title('Unit Cost Breakdown (< ₹0.48/doc)', fontsize=9.0, fontweight='bold', color='#0B1120', pad=6)
    plt.tight_layout()
    plt.savefig(CHART_COGS_DONUT, bbox_inches='tight', facecolor='#F8FAFC')
    plt.close()

    # 3. ARR Growth Bar Chart
    fig, ax = plt.subplots(figsize=(4.0, 2.7), dpi=300)
    years = ['Year 1\n(Pilot HEIs)', 'Year 2\n(30 Regional)', 'Year 3\n(70+ National)']
    arr = [12, 45, 105]
    bar_colors = ['#0284C7', '#059669', '#D4AF37']
    bars = ax.bar(years, arr, color=bar_colors, width=0.45, edgecolor='#0F172A', linewidth=0.6)

    for bar in bars:
        height = bar.get_height()
        label = f'₹{height} Lakhs' if height < 100 else '₹1.05 Crores'
        ax.text(bar.get_x() + bar.get_width()/2., height + 2.5, label,
                ha='center', va='bottom', fontsize=7.8, fontweight='bold', color='#0B1120')

    ax.set_ylim(0, 128)
    ax.set_ylabel('ARR (₹ in Lakhs)', fontsize=7.5, fontweight='bold', color='#475569')
    ax.tick_params(axis='both', which='major', labelsize=7.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CBD5E1')
    ax.spines['bottom'].set_color('#CBD5E1')
    ax.set_facecolor('#F8FAFC')
    fig.patch.set_facecolor('#F8FAFC')
    plt.title('3-Year ARR Growth Projection', fontsize=9.0, fontweight='bold', color='#0B1120', pad=6)
    plt.tight_layout()
    plt.savefig(CHART_ARR_BAR, bbox_inches='tight', facecolor='#F8FAFC')
    plt.close()

    print("[OK] All 3 data visualization charts generated successfully!")


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_MASTER,
        pagesize=A4,
        leftMargin=12*mm,
        rightMargin=12*mm,
        topMargin=9*mm,
        bottomMargin=9*mm,
        title="SATYAMEVA AEGIS - Comprehensive RIDEHACK'26 Executive Summary",
        author="Satyameva Aegis (Team ID: 10)",
    )

    s_banner_sub = ParagraphStyle(
        "BannerSub",
        fontName="SegoeUI-Bold",
        fontSize=8.5,
        leading=12,
        textColor=GOLD,
        alignment=TA_CENTER
    )
    s_banner_title = ParagraphStyle(
        "BannerTitle",
        fontName="SegoeUI-Bold",
        fontSize=14.5,
        leading=18,
        textColor=WHITE,
        alignment=TA_CENTER
    )
    s_banner_meta = ParagraphStyle(
        "BannerMeta",
        fontName="SegoeUI",
        fontSize=8,
        leading=11.5,
        textColor=CYAN_ACC,
        alignment=TA_CENTER
    )

    s_page_hdr = ParagraphStyle(
        "PageHdr",
        fontName="SegoeUI-Bold",
        fontSize=8,
        leading=11,
        textColor=CYAN_ACC,
        alignment=TA_CENTER
    )

    s_sec_hdr = ParagraphStyle(
        "SecHdr",
        fontName="SegoeUI-Bold",
        fontSize=9.8,
        leading=13.5,
        textColor=WHITE
    )
    s_body = ParagraphStyle(
        "Body",
        fontName="SegoeUI",
        fontSize=8.2,
        leading=11.8,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY
    )
    s_callout = ParagraphStyle(
        "Callout",
        fontName="SegoeUI-Italic",
        fontSize=8.0,
        leading=11.5,
        textColor=DARK_GREEN,
        alignment=TA_JUSTIFY
    )
    s_tbl_hdr = ParagraphStyle(
        "TblHdr",
        fontName="SegoeUI-Bold",
        fontSize=7.8,
        leading=10.5,
        textColor=WHITE,
        alignment=TA_CENTER
    )
    s_tbl_cell = ParagraphStyle(
        "TblCell",
        fontName="SegoeUI",
        fontSize=7.6,
        leading=10.5,
        textColor=TEXT_DARK
    )
    s_tbl_cell_bold = ParagraphStyle(
        "TblCellBold",
        fontName="SegoeUI-Bold",
        fontSize=7.6,
        leading=10.5,
        textColor=TEXT_DARK
    )
    s_tbl_cell_center = ParagraphStyle(
        "TblCellCenter",
        fontName="SegoeUI",
        fontSize=7.6,
        leading=10.5,
        textColor=TEXT_DARK,
        alignment=TA_CENTER
    )
    s_footer = ParagraphStyle(
        "Footer",
        fontName="SegoeUI",
        fontSize=7.2,
        leading=9.5,
        textColor=MUTED_TEXT,
        alignment=TA_CENTER
    )

    story = []

    def make_section_hdr(title, bg_color=NAVY):
        t = Table([[Paragraph(title, s_sec_hdr)]], colWidths=[186*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    def make_page_header(pg_num):
        t = Table([[Paragraph(f"JAYPEE UNIVERSITY OF INFORMATION TECHNOLOGY · IIC RIDEHACK'26 · SATYAMEVA AEGIS (TEAM ID: 10) · EXECUTIVE SUMMARY — PAGE {pg_num} OF 3", s_page_hdr)]], colWidths=[186*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), DARK_NAVY),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMBORDER', (0,-1), (-1,-1), 1.5, GOLD),
        ]))
        return t

    def make_page_footer(pg_num):
        t = Table([[Paragraph(f"Satyameva Aegis (Team ID: 10) · RIDEHACK'26 Internal Qualifiers @ JUIT Waknaghat · Grand Finale @ JIIT Noida (₹1 Crore Pool) · Page {pg_num} of 3", s_footer)]], colWidths=[186*mm])
        t.setStyle(TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPBORDER', (0,0), (-1,0), 0.5, BORDER_COL),
        ]))
        return t

    # =========================================================================
    # PAGE 1: EXECUTIVE SUMMARY, METRICS, PROBLEM, 4 PILLARS
    # =========================================================================
    banner_rows = [
        [Paragraph("JAYPEE UNIVERSITY OF INFORMATION TECHNOLOGY · IIC RIDEHACK'26", s_banner_sub)],
        [Paragraph("SATYAMEVA AEGIS — COMPREHENSIVE EXECUTIVE SUMMARY", s_banner_title)],
        [Paragraph("Team ID: 10 · Founding Campus: JUIT Waknaghat · Grand Finale: JIIT Noida<br/>Theme: Research, Innovation, Development & Entrepreneurship (RIDE) · ₹1 Crore Funding Pool", s_banner_meta)]
    ]
    t_banner = Table(banner_rows, colWidths=[186*mm])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMBORDER', (0,-1), (-1,-1), 2.5, GOLD),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 3.5))

    # 1. Executive Summary
    story.append(make_section_hdr("1. EXECUTIVE SUMMARY & THE ELEVATOR PITCH", NAVY))
    story.append(Spacer(1, 2.5))
    p_exec = (
        "<b>Satyameva Aegis</b> is an enterprise-grade B2B SaaS and decentralized trust protocol engineered to eradicate "
        "academic credential counterfeiting across Indian universities. While existing government platforms like DigiLocker serve "
        "as citizen-facing <i>storage lockers</i>, Satyameva functions as the <b>institutional origin security and automated verification engine</b>. "
        "Powered by a proprietary <b>Zero-Gas-Fee Proof-of-Work (PoW) private blockchain</b>, <b>Google Gemini Multimodal AI</b>, "
        "and <b>3D WebGL holographic tamper-evident inspection</b>, Satyameva compresses verification turnaround from <b>14–21 days down to 60 seconds</b>, "
        "reducing registrar clerical overhead by 95% at an institutional unit cost of <b>less than ₹0.48 per credential</b>."
    )
    story.append(Paragraph(p_exec, s_body))
    story.append(Spacer(1, 3.5))

    # Metric Value Multiplier Grid
    val_data = [
        [
            Paragraph("<b>Verification Turnaround</b><br/><font color='#059669'><b>14 Days → 60s</b> (99.9% ↓)</font>", s_tbl_cell_center),
            Paragraph("<b>Institutional Unit Cost</b><br/><font color='#059669'><b>&lt; ₹0.48 / Credential</b></font>", s_tbl_cell_center),
            Paragraph("<b>Tamper Detection Speed</b><br/><font color='#059669'><b>0.04s (40 ms)</b></font>", s_tbl_cell_center),
            Paragraph("<b>False Positive Rate</b><br/><font color='#059669'><b>Absolute 0.0%</b></font>", s_tbl_cell_center),
        ],
        [
            Paragraph("<b>Gross Profit Margin</b><br/><font color='#0284C7'><b>&gt; 90% (SaaS Model)</b></font>", s_tbl_cell_center),
            Paragraph("<b>Target Market (India)</b><br/><font color='#0284C7'><b>1,100+ Universities</b></font>", s_tbl_cell_center),
            Paragraph("<b>Year 3 ARR Projection</b><br/><font color='#0284C7'><b>₹1.05 Crores (70 HEIs)</b></font>", s_tbl_cell_center),
            Paragraph("<b>Crypto Gas Fees</b><br/><font color='#0284C7'><b>₹0.00 (Zero Volatility)</b></font>", s_tbl_cell_center),
        ]
    ]
    t_val = Table(val_data, colWidths=[46.5*mm, 46.5*mm, 46.5*mm, 46.5*mm])
    t_val.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_val)
    story.append(Spacer(1, 3.5))

    # 2. Problem Statement
    story.append(make_section_hdr("2. THE PROBLEM STATEMENT: INDIA'S ACADEMIC TRUST DEFICIT", RED))
    story.append(Spacer(1, 2.5))
    prob_data = [
        [
            Paragraph("<b>1. ₹1,500 Counterfeit Syndicates</b>", s_tbl_cell_bold),
            Paragraph("Over 40,000 fake degrees are officially detected in India annually. Telegram and Photoshop syndicates sell replica marksheet prints with duplicate university seals within 24 hours. Physical paper ink cannot be distinguished from high-res forged clones by corporate HR.", s_tbl_cell)
        ],
        [
            Paragraph("<b>2. 14–21 Day Verification Delays</b>", s_tbl_cell_bold),
            Paragraph("Corporate background screeners (TCS, Wipro, AuthBridge) rely on physical speed-post inquiry letters and manual emails to university registrars. This costs universities ₹12–18 Lakhs annually in clerical overhead and severely delays graduating students' foreign visa and job onboarding.", s_tbl_cell)
        ],
        [
            Paragraph("<b>3. Single Point of Failure in SQL</b>", s_tbl_cell_bold),
            Paragraph("Centralized university SQL databases have zero mathematical tamper-detection. A compromised registrar password or insider database access (<code>UPDATE students SET cgpa=9.5</code>) alters academic history silently with zero immutable audit trail.", s_tbl_cell)
        ]
    ]
    t_prob = Table(prob_data, colWidths=[52*mm, 134*mm])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), CARD_BG),
        ('BACKGROUND', (1,0), (1,-1), WHITE),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 3.5))

    # 3. 4-Pillar Architecture
    story.append(make_section_hdr("3. THE SATYAMEVA SOLUTION: 4-PILLAR DEEP-TECH ARCHITECTURE", DARK_GREEN))
    story.append(Spacer(1, 2.5))
    sol_data = [
        [
            Paragraph("<b>Pillar 1: Zero-Gas-Fee Proof-of-Work Blockchain</b><br/>"
                      "Custom enterprise PoW consensus (Difficulty 4: <code>'0000...'</code>). No Ethereum gas fees, no cryptocurrency exposure. "
                      "Dual-Persistence Parity maintains fast relational SQLite synchronized with immutable <code>blockchain.json</code>. Any silent DB alteration is auto-detected and repaired.", s_body),
            Paragraph("<b>Pillar 2: Multimodal Gemini AI OCR Pipeline</b><br/>"
                      "Google Gemini Multimodal Vision API directly ingests raw certificate scans and PDFs. In 1.8 seconds, it extracts Student Name, Roll Number, "
                      "Degree Program, and DOB into structured JSON, eliminating 95% of clerical typing errors.", s_body)
        ],
        [
            Paragraph("<b>Pillar 3: Dynamic 60s QR & AES-256 DOB Protected PDFs</b><br/>"
                      "Student digital wallets generate an HMAC-salted QR code that refreshes every 60 seconds — forwarded screenshots immediately expire. "
                      "Downloaded stamped PDFs are encrypted via AES-256 locking the file with the student's birthdate (<code>DDMMYYYY</code>).", s_body),
            Paragraph("<b>Pillar 4: 3D WebGL Holographic Verification</b><br/>"
                      "In-browser Three.js engine renders a zero-gravity parchment certificate with gold-embossed crest and iridescent rainbow diffraction. "
                      "Recruiters can inspect security micro-print and click to flip the certificate 180° to reveal the cryptographic PoW block hash.", s_body)
        ]
    ]
    t_sol = Table(sol_data, colWidths=[93*mm, 93*mm])
    t_sol.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_sol)
    story.append(Spacer(1, 3.5))
    story.append(make_page_footer(1))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: 4 PORTALS, STRATEGIC DIFFERENTIATION, BUSINESS MODEL WITH CHARTS
    # =========================================================================
    story.append(make_page_header(2))
    story.append(Spacer(1, 3))

    # 4. Operating Portals
    story.append(make_section_hdr("4. THE 4 OPERATING PORTALS (LIVE DEPLOYED PROTOTYPE)", NAVY))
    story.append(Spacer(1, 2.5))
    portals_data = [
        [Paragraph("<b>Portal</b>", s_tbl_hdr), Paragraph("<b>Target User & URL</b>", s_tbl_hdr), Paragraph("<b>Key Enterprise Functionality</b>", s_tbl_hdr)],
        [
            Paragraph("<b>1. Super-Admin</b>", s_tbl_cell_bold),
            Paragraph("System Overseer / Governance<br/><code>/admin/</code>", s_tbl_cell),
            Paragraph("Approves university registrations, manages multi-campus annual licenses, monitors node health, tunes PoW difficulty, and tracks real-time tamper telemetry.", s_tbl_cell)
        ],
        [
            Paragraph("<b>2. University Registrar</b>", s_tbl_cell_bold),
            Paragraph("Controller of Exams / Issuers<br/><code>/issuer/</code>", s_tbl_cell),
            Paragraph("Uploads bulk CSV degree batches, triggers Gemini AI auto-parsing, approves student account requests, mines blockchain blocks, and resolves student correction tickets.", s_tbl_cell)
        ],
        [
            Paragraph("<b>3. Student Wallet</b>", s_tbl_cell_bold),
            Paragraph("Graduating Students & Alumni<br/><code>/student/dashboard</code>", s_tbl_cell),
            Paragraph("Accesses self-sovereign credentials, downloads DOB-encrypted stamped PDFs, generates 60s dynamic anti-screenshot QRs, files correction grievances, and views audit logs.", s_tbl_cell)
        ],
        [
            Paragraph("<b>4. Public Verifier</b>", s_tbl_cell_bold),
            Paragraph("Recruiters, HR & Embassies<br/><code>/verify</code> (Zero-Login)", s_tbl_cell),
            Paragraph("Scans QR or enters hash for 60-second instant validation, views 3D holographic block lock-in, checks SHA-256 Merkle root, and exports official verification audit PDFs.", s_tbl_cell)
        ]
    ]
    t_portals = Table(portals_data, colWidths=[34*mm, 42*mm, 110*mm])
    t_portals.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_portals)
    story.append(Spacer(1, 3))

    # 5. Why Not DigiLocker
    story.append(make_section_hdr("5. STRATEGIC DIFFERENTIATION: WHY NOT DIGILOCKER?", PURPLE))
    story.append(Spacer(1, 2.5))
    diff_data = [
        [Paragraph("<b>Evaluation Metric</b>", s_tbl_hdr), Paragraph("<b>Government DigiLocker</b>", s_tbl_hdr), Paragraph("<b>Satyameva Aegis (Our Solution)</b>", s_tbl_hdr)],
        [
            Paragraph("<b>Architecture & Role</b>", s_tbl_cell_bold),
            Paragraph("Citizen Storage Locker (C2C)", s_tbl_cell),
            Paragraph("<b>Institutional Security & Verification Engine (B2B)</b>", s_tbl_cell_bold)
        ],
        [
            Paragraph("<b>Verification Turnaround</b>", s_tbl_cell_bold),
            Paragraph("Manual download & inspection (14–21 days)", s_tbl_cell),
            Paragraph("<b>Instant in under 60 seconds (Automated Engine)</b>", s_tbl_cell_bold)
        ],
        [
            Paragraph("<b>International Recruiter Access</b>", s_tbl_cell_bold),
            Paragraph("<font color='#DC2626'><b>Fails</b></font> (Requires Indian Aadhaar & OTP)", s_tbl_cell),
            Paragraph("<font color='#059669'><b>Frictionless</b></font> (Global US/UK recruiters verify in 60s without login)", s_tbl_cell_bold)
        ],
        [
            Paragraph("<b>Institutional B2B Dashboard</b>", s_tbl_cell_bold),
            Paragraph("Zero university telemetry or fraud analytics", s_tbl_cell),
            Paragraph("<b>Full governance console: fraud tracking & license management</b>", s_tbl_cell_bold)
        ],
        [
            Paragraph("<b>Physical Print Protection</b>", s_tbl_cell_bold),
            Paragraph("Printed PDF loses all security", s_tbl_cell),
            Paragraph("<b>Permanent institutional QR + AES-256 DOB password encryption</b>", s_tbl_cell_bold)
        ],
        [
            Paragraph("<b>Strategic Positioning</b>", s_tbl_cell_bold),
            Paragraph("Generic cloud document repository", s_tbl_cell),
            Paragraph("<b>Complementary origin protocol: feeds verified data into DigiLocker & ABC</b>", s_tbl_cell_bold)
        ]
    ]
    t_diff = Table(diff_data, colWidths=[42*mm, 68*mm, 76*mm])
    t_diff.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PURPLE),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_diff)
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>The VC Metaphor:</b> <i>'DigiLocker is a citizen storage cupboard. Satyameva is the biometric lock, digital seal, and origin proof that guarantees what goes into that cupboard can never be forged.'</i>", s_callout))
    story.append(Spacer(1, 3))

    # 6. Business Model With Embedded Charts (Donut Pie & Bar Chart)
    story.append(make_section_hdr("6. BUSINESS MODEL, UNIT ECONOMICS & REVENUE PROJECTIONS", DARK_GREEN))
    story.append(Spacer(1, 2.5))

    # Dual Monetization Overview Card
    biz_summary = [
        [
            Paragraph("<b>1. Annual University SaaS: ₹1.5 Lakhs/campus/year</b> — Includes registrar bulk issuance portal, automated Gemini AI parsing, tamper telemetry, and student wallets. Universities save ₹8–12L in manual clerical verification costs (5x ROI).", s_tbl_cell),
            Paragraph("<b>2. Corporate Pay-Per-Verify API: ₹10 – ₹25 per check</b> — B2B API access for high-volume background screening firms (AuthBridge, TCS, Infosys, Wipro). Instant cryptographic response with zero clerical touchpoints.", s_tbl_cell)
        ]
    ]
    t_biz_sum = Table(biz_summary, colWidths=[93*mm, 93*mm])
    t_biz_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_biz_sum)
    story.append(Spacer(1, 2.5))

    # Side-by-Side Visual Charts: Donut Pie Chart (< ₹0.48 COGS) & ARR Bar Chart
    chart_cells = [
        [
            RLImage(CHART_COGS_DONUT, width=91*mm, height=48*mm),
            RLImage(CHART_ARR_BAR, width=91*mm, height=48*mm)
        ]
    ]
    t_charts_p2 = Table(chart_cells, colWidths=[93*mm, 93*mm])
    t_charts_p2.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_charts_p2)
    story.append(Spacer(1, 3))
    story.append(make_page_footer(2))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: TEAM, FORENSIC BENCHMARKS, ₹25L ASK WITH PIE CHART & DIRECTORY
    # =========================================================================
    story.append(make_page_header(3))
    story.append(Spacer(1, 3))

    # 7. Founding Team
    story.append(make_section_hdr("7. FOUNDING TEAM & EXECUTION ROLES (TEAM ID: 10)", NAVY))
    story.append(Spacer(1, 2.5))
    team_data = [
        [Paragraph("<b>Founding Member</b>", s_tbl_hdr), Paragraph("<b>Academic Profile</b>", s_tbl_hdr), Paragraph("<b>Specialized Core Contribution to Satyameva</b>", s_tbl_hdr)],
        [
            Paragraph("<b>A. Praneeth Sai</b><br/>Founder & Chief Architect", s_tbl_cell_bold),
            Paragraph("B.Tech CSE-CS<br/>@ JUIT Waknaghat", s_tbl_cell),
            Paragraph("100% Core Protocol & Backend Engineering: Custom PoW blockchain consensus (zero gas fees), SHA-256 Merkle leaf hashing, PBKDF2 per-document salting, and dual-persistence SQLite ↔ JSON ledger synchronization.", s_tbl_cell)
        ],
        [
            Paragraph("<b>Anushka Bansal</b><br/>Co-Founder & Data Lead", s_tbl_cell_bold),
            Paragraph("B.Tech Bioinformatics<br/>@ JUIT Waknaghat", s_tbl_cell),
            Paragraph("Data integrity heuristics, mathematical data modeling, DigiLocker differentiation strategy, and 24/24 adversarial attack vector stress testing (0.04s detection, 0% false positives).", s_tbl_cell)
        ],
        [
            Paragraph("<b>Shashank Ray</b><br/>Co-Founder & AI Lead", s_tbl_cell_bold),
            Paragraph("B.Tech CSE-AI&ML<br/>@ JUIT Waknaghat", s_tbl_cell),
            Paragraph("Gemini Multimodal Vision OCR prompt pipelines, automated DOB parsing for AES-256 PDF encryption, institutional unit economics modeling (&lt; ₹0.48/doc), and B2B SaaS revenue roadmap.", s_tbl_cell)
        ],
        [
            Paragraph("<b>Sameeksha Chandel</b><br/>Co-Founder & Product Lead", s_tbl_cell_bold),
            Paragraph("B.Tech CSE-AI&ML<br/>@ JUIT Waknaghat", s_tbl_cell),
            Paragraph("Product lifecycle, 4-portal user journeys, 3D WebGL holographic verification with iridescent diffraction, student grievance workflows, NEP 2020 regulatory compliance, and RIDE incubation roadmap.", s_tbl_cell)
        ]
    ]
    t_team = Table(team_data, colWidths=[42*mm, 38*mm, 106*mm])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 3))

    # 8. Forensic Benchmarks & 9. Incubation Ask With PIE CHART
    story.append(make_section_hdr("8. FORENSIC BENCHMARKS & 9. ₹25 LAKH RIDE INCUBATION ASK (WITH PIE CHART)", GOLD))
    story.append(Spacer(1, 2.5))

    # 3-Column Layout: Benchmarks (Col 1), Fund Allocation Bullets (Col 2), Pie Chart (Col 3)
    p_bench = (
        "<b>8. Forensic Security Testing</b><br/>"
        "• <b>Chain Gap Attack:</b> Caught instantly; ledger triggers peer self-healing.<br/>"
        "• <b>Silent SQL Modification:</b> Caught in <b>0.04s (40 ms)</b> with <code>TAMPERED</code> status.<br/>"
        "• <b>Nonce Tampering:</b> Nonces failing PoW Difficulty 4 rejected automatically.<br/>"
        "• <b>Salt Collision Tests:</b> 50 identical credentials produced 50/50 unique hashes with <b>0 collisions</b> and <b>0% false positives</b>."
    )
    p_ask = (
        "<b>9. ₹25 Lakh Seed Fund Allocation</b><br/>"
        "• <b>40% (₹10.0L) — Multi-Node Infra:</b> Server nodes across JUIT, JIIT, and JUET.<br/>"
        "• <b>30% (₹7.5L) — Multi-Campus Pilot:</b> 5,000+ real graduation records in Jaypee system.<br/>"
        "• <b>20% (₹5.0L) — Security Audits & IP:</b> Cert-In certification & provisional patent.<br/>"
        "• <b>10% (₹2.5L) — Legal & Ops:</b> B2B institutional SaaS contracts & NEP compliance."
    )

    ask_chart_img = RLImage(CHART_ASK_PIE, width=64*mm, height=48*mm)

    bot_data = [
        [
            Paragraph(p_bench, s_body),
            Paragraph(p_ask, s_body),
            ask_chart_img
        ]
    ]
    t_bot = Table(bot_data, colWidths=[60*mm, 62*mm, 64*mm])
    t_bot.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_bot)
    story.append(Spacer(1, 3))

    # 10. Deliverables Directory & Repository Ecosystem Mirror
    story.append(make_section_hdr("10. DELIVERABLES DIRECTORY & SYSTEM REPOSITORY ECOSYSTEM", DARK_NAVY))
    story.append(Spacer(1, 2.5))
    repo_data = [
        [
            Paragraph("<b>Master Pitch Deck:</b><br/><code>RIDEHACK26_TEAM_MASTER_DECK.pptx</code><br/>12-Slide 16:9 widescreen presentation deck", s_tbl_cell),
            Paragraph("<b>Presentation PDF:</b><br/><code>RIDEHACK26_TEAM_MASTER_DECK.pdf</code><br/>High-res export with speaker slide notes", s_tbl_cell),
            Paragraph("<b>Anushka Script & Guide:</b><br/><code>ANUSHKA_SPEAKING_SCRIPT_AND_ROLE_GUIDE.pdf</code><br/>Role guide, Q&A defense, and speech", s_tbl_cell)
        ],
        [
            Paragraph("<b>Shashank Speaking Script:</b><br/><code>SHASHANK_SPEAKING_SCRIPT.pdf</code><br/>AI pipeline & unit economics breakdown", s_tbl_cell),
            Paragraph("<b>Business Strategy:</b><br/><code>SATYAMEVA_BUSINESS_STRATEGY.pdf</code><br/>B2B SaaS pricing, sales funnel & ARR", s_tbl_cell),
            Paragraph("<b>Interactive 3D WebGL Engine:</b><br/><code>frontend/threejs_hologram.html</code><br/>Zero-gravity parchment & gold crest", s_tbl_cell)
        ]
    ]
    t_repo = Table(repo_data, colWidths=[62*mm, 62*mm, 62*mm])
    t_repo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_repo)
    story.append(Spacer(1, 3))
    story.append(make_page_footer(3))

    doc.build(story)
    print(f"[OK] Master Executive Summary PDF with Charts created at: {PDF_MASTER}")


def render_images_and_convert_to_pdf():
    # 1. Open generated Master PDF with PyMuPDF
    doc = pymupdf.open(PDF_MASTER)
    print(f"Total pages in Master PDF: {len(doc)}")
    assert len(doc) == 3, f"Expected 3 pages, got {len(doc)}"

    page_images = []
    page_img_paths = [IMG_PAGE1, IMG_PAGE2, IMG_PAGE3]

    # Render each page at 300 DPI
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        out_path = page_img_paths[i]
        pix.save(out_path)
        print(f"[OK] Saved Page {i+1} Image ({pix.width}x{pix.height} px): {out_path}")
        im = Image.open(out_path).convert('RGB')
        page_images.append(im)

    # 3. Create Unified Infographic Poster Image (Stitched Vertically)
    w = max(img.width for img in page_images)
    total_h = sum(img.height for img in page_images)
    divider_h = 24

    poster_img = Image.new('RGB', (w, total_h + (len(page_images) - 1) * divider_h), color=(11, 17, 32))
    current_y = 0
    for idx, img in enumerate(page_images):
        poster_img.paste(img, (0, current_y))
        current_y += img.height
        if idx < len(page_images) - 1:
            current_y += divider_h

    poster_img.save(IMG_INFOGRAPHIC, format="PNG", quality=95)
    print(f"[OK] Saved Unified Infographic Poster Image ({poster_img.width}x{poster_img.height} px): {IMG_INFOGRAPHIC}")

    # 4. Mirror all artifacts to Satyameva, SIH_Aegis, and brain artifact folder
    targets = [SATYAMEVA_DIR, SIH_DIR, ARTIFACT_DIR]
    all_files = [
        PDF_MASTER,
        IMG_PAGE1,
        IMG_PAGE2,
        IMG_PAGE3,
        IMG_INFOGRAPHIC,
        CHART_ASK_PIE,
        CHART_COGS_DONUT,
        CHART_ARR_BAR
    ]

    for target_dir in targets:
        if os.path.exists(target_dir):
            for src_file in all_files:
                dest = os.path.join(target_dir, os.path.basename(src_file))
                try:
                    shutil.copy2(src_file, dest)
                except Exception as e:
                    print(f"Warning copying {src_file} to {dest}: {e}")
            print(f"[OK] Mirrored all files to: {target_dir}")


if __name__ == '__main__':
    generate_all_charts()
    build_pdf()
    render_images_and_convert_to_pdf()
