"""
generate_comprehensive_summary_pdf.py — Generates the complete, unabridged Executive Summary PDF for RIDEHACK'26.
Output: C:\\Users\\hp\\OneDrive\\Desktop\\SATYAMEVA_RIDEHACK26_EXECUTIVE_SUMMARY.pdf
"""
import os
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

OUT_PDF = r"C:\Users\hp\OneDrive\Desktop\SATYAMEVA_RIDEHACK26_EXECUTIVE_SUMMARY.pdf"

# Color Palette
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

def build_pdf():
    doc = SimpleDocTemplate(
        OUT_PDF,
        pagesize=A4,
        leftMargin=13*mm,
        rightMargin=13*mm,
        topMargin=12*mm,
        bottomMargin=12*mm,
        title="SATYAMEVA AEGIS - Comprehensive RIDEHACK'26 Executive Summary",
        author="Satyameva Aegis (Team ID: 10)",
    )

    styles = getSampleStyleSheet()

    s_banner_sub = ParagraphStyle(
        "BannerSub",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=GOLD,
        alignment=TA_CENTER
    )
    s_banner_title = ParagraphStyle(
        "BannerTitle",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=WHITE,
        alignment=TA_CENTER
    )
    s_banner_meta = ParagraphStyle(
        "BannerMeta",
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=CYAN_ACC,
        alignment=TA_CENTER
    )

    s_sec_hdr = ParagraphStyle(
        "SecHdr",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14.5,
        textColor=WHITE
    )
    s_body = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY
    )
    s_body_bold = ParagraphStyle(
        "BodyBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_DARK
    )
    s_callout = ParagraphStyle(
        "Callout",
        fontName="Helvetica-Oblique",
        fontSize=8.2,
        leading=12,
        textColor=DARK_GREEN,
        alignment=TA_JUSTIFY
    )
    s_tbl_hdr = ParagraphStyle(
        "TblHdr",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=WHITE,
        alignment=TA_CENTER
    )
    s_tbl_cell = ParagraphStyle(
        "TblCell",
        fontName="Helvetica",
        fontSize=7.8,
        leading=11,
        textColor=TEXT_DARK
    )
    s_tbl_cell_bold = ParagraphStyle(
        "TblCellBold",
        fontName="Helvetica-Bold",
        fontSize=7.8,
        leading=11,
        textColor=TEXT_DARK
    )
    s_tbl_cell_center = ParagraphStyle(
        "TblCellCenter",
        fontName="Helvetica",
        fontSize=7.8,
        leading=11,
        textColor=TEXT_DARK,
        alignment=TA_CENTER
    )
    s_badge = ParagraphStyle(
        "BadgeText",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=DARK_GREEN,
        alignment=TA_CENTER
    )

    story = []

    # ── TOP BANNER ─────────────────────────────────────────────────────────────
    banner_rows = [
        [Paragraph("JAYPEE UNIVERSITY OF INFORMATION TECHNOLOGY · IIC RIDEHACK'26", s_banner_sub)],
        [Paragraph("SATYAMEVA AEGIS — COMPREHENSIVE EXECUTIVE SUMMARY", s_banner_title)],
        [Paragraph("Team ID: 10 · Founding Campus: JUIT Waknaghat · Grand Finale: JIIT Noida<br/>Theme: Research, Innovation, Development & Entrepreneurship (RIDE) · ₹1 Crore Funding Pool", s_banner_meta)]
    ]
    t_banner = Table(banner_rows, colWidths=[184*mm])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMBORDER', (0,-1), (-1,-1), 2.5, GOLD),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 5))

    def make_section_hdr(title, bg_color=NAVY):
        t = Table([[Paragraph(title, s_sec_hdr)]], colWidths=[184*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    # ── 1. EXECUTIVE SUMMARY & VALUE MULTIPLIER ────────────────────────────────
    story.append(make_section_hdr("1. EXECUTIVE SUMMARY & THE ELEVATOR PITCH", NAVY))
    story.append(Spacer(1, 3))

    p_exec = (
        "<b>Satyameva Aegis</b> is an enterprise-grade B2B SaaS and decentralized trust protocol engineered to eradicate "
        "academic credential counterfeiting in Indian universities. While existing government platforms like DigiLocker serve "
        "as citizen-facing <i>storage lockers</i>, Satyameva functions as the <b>institutional origin security and automated verification engine</b>. "
        "Powered by a proprietary <b>Zero-Gas-Fee Proof-of-Work (PoW) private blockchain</b>, <b>Google Gemini Multimodal AI</b>, "
        "and <b>3D WebGL holographic tamper-evident inspection</b>, Satyameva compresses verification turnaround from <b>14–21 days down to 60 seconds</b>, "
        "reducing registrar clerical overhead by 95% at an institutional unit cost of <b>less than ₹0.48 per credential</b>."
    )
    story.append(Paragraph(p_exec, s_body))
    story.append(Spacer(1, 4))

    # Metric Value Multiplier Grid
    val_data = [
        [
            Paragraph("<b>Verification Turnaround</b><br/><font color='#059669'><b>14 Days ➔ 60s</b> (99.9% ↓)</font>", s_tbl_cell_center),
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
    t_val = Table(val_data, colWidths=[46*mm, 46*mm, 46*mm, 46*mm])
    t_val.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_val)
    story.append(Spacer(1, 6))

    # ── 2. THE PROBLEM STATEMENT ───────────────────────────────────────────────
    story.append(make_section_hdr("2. THE PROBLEM STATEMENT: INDIA'S ACADEMIC TRUST DEFICIT", RED))
    story.append(Spacer(1, 3))

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
    t_prob = Table(prob_data, colWidths=[52*mm, 132*mm])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), CARD_BG),
        ('BACKGROUND', (1,0), (1,-1), WHITE),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 6))

    # ── 3. THE SATYAMEVA SOLUTION: 4-PILLAR ARCHITECTURE ───────────────────────
    story.append(make_section_hdr("3. THE SATYAMEVA SOLUTION: 4-PILLAR DEEP-TECH ARCHITECTURE", DARK_GREEN))
    story.append(Spacer(1, 3))

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
    t_sol = Table(sol_data, colWidths=[92*mm, 92*mm])
    t_sol.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_sol)
    story.append(Spacer(1, 6))

    # ── 4. THE 4 OPERATING PORTALS ─────────────────────────────────────────────
    story.append(make_section_hdr("4. THE 4 OPERATING PORTALS (LIVE DEPLOYED PROTOTYPE)", NAVY))
    story.append(Spacer(1, 3))

    portals_data = [
        [Paragraph("<b>Portal</b>", s_tbl_hdr), Paragraph("<b>Target User & URL</b>", s_tbl_hdr), Paragraph("<b>Key Enterprise Functionality</b>", s_tbl_hdr)],
        [
            Paragraph("<b>1. Super-Admin</b>", s_tbl_cell_bold),
            Paragraph("System Overseer / JUIT Governance<br/><code>/admin/</code>", s_tbl_cell),
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
    t_portals = Table(portals_data, colWidths=[34*mm, 42*mm, 108*mm])
    t_portals.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_portals)
    story.append(Spacer(1, 6))

    # ── 5. WHY NOT DIGILOCKER? ─────────────────────────────────────────────────
    story.append(make_section_hdr("5. STRATEGIC DIFFERENTIATION: WHY NOT DIGILOCKER?", PURPLE))
    story.append(Spacer(1, 3))

    diff_data = [
        [Paragraph("<b>Evaluation Metric</b>", s_tbl_hdr), Paragraph("<b>Government DigiLocker</b>", s_tbl_hdr), Paragraph("<b>Satyameva Aegis (Our Solution)</b>", s_tbl_hdr)],
        [
            Paragraph("<b>Architecture & Role</b>", s_tbl_cell_bold),
            Paragraph("Citizen Storage Locker (C2C)", s_tbl_cell),
            Paragraph("<b>Institutional Security & Verification Engine (B2B)</b>", s_tbl_cell_bold)
        ],
        [
            Paragraph("<b>Verification Turnaround</b>", s_tbl_cell_bold),
            Paragraph("Manual download & inspection", s_tbl_cell),
            Paragraph("<b>Instant in under 60 seconds (Automated)</b>", s_tbl_cell_bold)
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
    t_diff = Table(diff_data, colWidths=[42*mm, 68*mm, 74*mm])
    t_diff.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PURPLE),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_diff)
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>The VC Metaphor:</b> <i>'DigiLocker is a citizen storage cupboard. Satyameva is the biometric lock, digital seal, and origin proof that guarantees what goes into that cupboard can never be forged.'</i>", s_callout))
    story.append(Spacer(1, 6))

    # ── 6. BUSINESS MODEL, UNIT ECONOMICS & ARR ────────────────────────────────
    story.append(make_section_hdr("6. BUSINESS MODEL, UNIT ECONOMICS & REVENUE PROJECTIONS", DARK_GREEN))
    story.append(Spacer(1, 3))

    biz_data = [
        [
            Paragraph("<b>A. Unit Cost Breakdown (&lt; ₹0.48/doc)</b><br/>"
                      "• Gemini Vision API Extraction: ₹0.18<br/>"
                      "• PoW Blockchain Mining: ₹0.04 (Local CPU)<br/>"
                      "• AES-256 Encryption & Stamping: ₹0.06<br/>"
                      "• Cloud Storage Allocation: ₹0.15<br/>"
                      "<b>TOTAL COGS: ₹0.43 – ₹0.48 / Credential</b><br/>"
                      "<font color='#059669'><b>Gross Margin Exceeds 90%</b></font>", s_body),
            Paragraph("<b>B. Dual Monetization Streams</b><br/>"
                      "<b>1. Annual University SaaS:</b> ₹1.5 Lakhs/campus/year for registrar bulk issuance, student wallets, and admin console.<br/>"
                      "<i>(Universities save ₹8–12L in manual clerical overhead ➔ 5x ROI).</i><br/>"
                      "<b>2. Corporate Pay-Per-Verify API:</b> ₹10 to ₹25 per check charged to background agencies (AuthBridge, TCS, Infosys).", s_body),
            Paragraph("<b>C. 3-Year ARR Growth Roadmap</b><br/>"
                      "• <b>Year 1 (Pilot): ₹12 Lakhs</b><br/>"
                      "  <i>3 Jaypee Campuses (JUIT, JIIT, JUET) + 5 regional HEIs.</i><br/>"
                      "• <b>Year 2 (Regional): ₹45 Lakhs</b><br/>"
                      "  <i>30 Private & State HEIs across North India.</i><br/>"
                      "• <b>Year 3 (National): ₹1.05 Crores ARR</b><br/>"
                      "  <i>70+ Higher Education Institutions nationally.</i>", s_body)
        ]
    ]
    t_biz = Table(biz_data, colWidths=[58*mm, 66*mm, 60*mm])
    t_biz.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_biz)
    story.append(Spacer(1, 6))

    # ── 7. FOUNDING TEAM & EXECUTION ROLES ──────────────────────────────────────
    story.append(make_section_hdr("7. FOUNDING TEAM & EXECUTION ROLES (TEAM ID: 10)", NAVY))
    story.append(Spacer(1, 3))

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
            Paragraph("Gemini Multimodal Vision OCR prompt pipelines, automated DOB parsing for AES-256 PDF encryption, institutional unit economics modeling (< ₹0.48/doc), and B2B SaaS revenue roadmap.", s_tbl_cell)
        ],
        [
            Paragraph("<b>Sameeksha Chandel</b><br/>Co-Founder & Product Lead", s_tbl_cell_bold),
            Paragraph("B.Tech CSE-AI&ML<br/>@ JUIT Waknaghat", s_tbl_cell),
            Paragraph("Product lifecycle, 4-portal user journeys, 3D WebGL holographic verification with iridescent diffraction, student grievance workflows, NEP 2020 regulatory compliance, and RIDE incubation roadmap.", s_tbl_cell)
        ]
    ]
    t_team = Table(team_data, colWidths=[42*mm, 38*mm, 104*mm])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 6))

    # ── 8. ADVERSARIAL SECURITY BENCHMARKS & 9. RIDE INCUBATION ASK ────────────
    story.append(make_section_hdr("8. FORENSIC BENCHMARKS & 9. ₹25 LAKH RIDE INCUBATION ASK", GOLD))
    story.append(Spacer(1, 3))

    bot_data = [
        [
            Paragraph("<b>8. Forensic Security Testing (24/24 Passed)</b><br/>"
                      "• <b>Chain Gap Attack:</b> Caught instantly; ledger triggers peer self-healing.<br/>"
                      "• <b>Silent SQL Modification:</b> Caught in <b>0.04s (40 ms)</b> with <code>TAMPERED</code> status.<br/>"
                      "• <b>Nonce Tampering:</b> Nonces failing PoW Difficulty 4 rejected automatically.<br/>"
                      "• <b>Salt Collision Tests:</b> 50 identical credentials produced 50/50 unique hashes with <b>0 collisions</b> and <b>0% false positives</b>.", s_body),
            Paragraph("<b>9. ₹25 Lakh Seed Funding Allocation</b><br/>"
                      "• <b>40% (₹10.0 Lakhs) — Multi-Node Infrastructure:</b> Dedicated servers across JUIT, JIIT, and JUET nodes.<br/>"
                      "• <b>30% (₹7.5 Lakhs) — Multi-Campus Pilot:</b> Onboarding 5,000+ real graduation batches in Jaypee system.<br/>"
                      "• <b>20% (₹5.0 Lakhs) — Security Audits & IP:</b> Cert-In certification & provisional patenting.<br/>"
                      "• <b>10% (₹2.5 Lakhs) — Legal & Ops:</b> B2B institutional SaaS contracts & NEP compliance.", s_body)
        ]
    ]
    t_bot = Table(bot_data, colWidths=[92*mm, 92*mm])
    t_bot.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_bot)
    story.append(Spacer(1, 6))

    # ── FOOTER REFERENCE SUMMARY ───────────────────────────────────────────────
    foot_text = (
        "<b>Deliverables Mirror:</b> PowerPoint Deck (<code>RIDEHACK26_TEAM_MASTER_DECK.pptx</code>) · "
        "Presentation PDF (<code>RIDEHACK26_TEAM_MASTER_DECK.pdf</code>) · "
        "Anushka Script (<code>ANUSHKA_SPEAKING_SCRIPT_AND_ROLE_GUIDE.pdf</code>) · "
        "Shashank Script (<code>SHASHANK_SPEAKING_SCRIPT.pdf</code>) · "
        "Business Strategy (<code>SATYAMEVA_BUSINESS_STRATEGY.pdf</code>)."
    )
    story.append(Paragraph(foot_text, s_banner_meta))

    doc.build(story)
    print(f"[OK] Comprehensive Executive Summary PDF built successfully at: {OUT_PDF}")

if __name__ == '__main__':
    build_pdf()
