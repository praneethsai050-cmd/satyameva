"""
Generate comprehensive, executive PDF for Satyameva Aegis Business Strategy & Architecture Guide.
Covers all 19 queries and strategic requirements for RIDEHACK'26 and university adoption.
"""
import os
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

NAVY       = colors.HexColor("#0A192F")
DARK_NAVY  = colors.HexColor("#060D1A")
SLATE      = colors.HexColor("#1E293B")
GOLD       = colors.HexColor("#D97706")
LIGHT_GOLD = colors.HexColor("#FEF3C7")
CYAN       = colors.HexColor("#0284C7")
LIGHT_CYAN = colors.HexColor("#E0F2FE")
WHITE      = colors.white
LIGHT_GRAY = colors.HexColor("#F8FAFC")
BORDER_COL = colors.HexColor("#CBD5E1")
TEXT_DARK  = colors.HexColor("#0F172A")
MUTED_TEXT = colors.HexColor("#475569")
GREEN      = colors.HexColor("#059669")
LIGHT_GREEN= colors.HexColor("#D1FAE5")
CRIMSON    = colors.HexColor("#DC2626")
LIGHT_RED  = colors.HexColor("#FEE2E2")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(14*mm, 285*mm, "SATYAMEVA AEGIS · RIDEHACK'26 STRATEGY & ARCHITECTURE DOSSIER")
            self.drawRightString(196*mm, 285*mm, "CRYPTOGRAPHIC TRUST PROTOCOL")
            self.setStrokeColor(BORDER_COL)
            self.setLineWidth(0.5)
            self.line(14*mm, 283*mm, 196*mm, 283*mm)
        
        # Footer
        self.setStrokeColor(BORDER_COL)
        self.setLineWidth(0.5)
        self.line(14*mm, 12*mm, 196*mm, 12*mm)
        self.drawString(14*mm, 8*mm, "CONFIDENTIAL · Team CYPHER X · Jaypee University of Information Technology")
        self.drawRightString(196*mm, 8*mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def create_banner():
    title_p = Paragraph(
        "<b>SATYAMEVA AEGIS · BUSINESS STRATEGY &amp; ARCHITECTURE</b>",
        ParagraphStyle("BTitle", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=WHITE, alignment=TA_CENTER)
    )
    sub_p = Paragraph(
        "<b>RIDEHACK'26 COMPREHENSIVE DOSSIER: ECONOMICS, COMPETITION &amp; WORKFLOWS</b>",
        ParagraphStyle("BSub", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=GOLD, alignment=TA_CENTER)
    )
    meta_p = Paragraph(
        "Founding Team: <b>CYPHER X (A Praneeth Sai &amp; Shashank Ray)</b> &nbsp;|&nbsp; Jaypee Multi-Campus Network",
        ParagraphStyle("BMeta", fontName="Helvetica", fontSize=8, leading=11, textColor=CYAN, alignment=TA_CENTER)
    )
    t = Table([[title_p], [Spacer(1, 1*mm)], [sub_p], [Spacer(1, 1*mm)], [meta_p]], colWidths=[182*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def section_hdr(num_str, title_str):
    p_num = Paragraph(f"<b>SECTION {num_str}</b>", ParagraphStyle("SNum", fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=GOLD))
    p_title = Paragraph(f"<b>{title_str}</b>", ParagraphStyle("STitle", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=WHITE))
    t = Table([[p_num], [p_title]], colWidths=[182*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SLATE),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    return t

def build_pdf():
    out_path = "C:/Users/hp/OneDrive/Desktop/SATYAMEVA_BUSINESS_STRATEGY.pdf"
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=14*mm,
        rightMargin=14*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
        title="Satyameva Aegis - Business Strategy & Architecture",
        author="Team CYPHER X",
    )

    body_s = ParagraphStyle("BodyS", fontName="Helvetica", fontSize=8.5, leading=12, textColor=TEXT_DARK, alignment=TA_JUSTIFY)
    body_bold = ParagraphStyle("BodySBold", fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=TEXT_DARK)
    bullet_s = ParagraphStyle("BulletS", fontName="Helvetica", fontSize=8.5, leading=12, textColor=TEXT_DARK, leftIndent=10)

    story = []

    # Title Banner
    story.append(create_banner())
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # SECTION 1: How Satyameva Stands Out
    # =========================================================================
    story.append(section_hdr("01", "HOW SATYAMEVA STANDS OUT · UNIQUE VALUE PROPOSITION"))
    story.append(Spacer(1, 1.5*mm))

    story.append(Paragraph(
        "<b>1. Cryptographic Origin Proof (Not Merely Cloud Storage):</b> Unlike traditional depositories that blindly store PDFs provided to them, Satyameva binds document metadata, binary digests, dynamic PBKDF2 salting (100k rounds), and Proof-of-Work blockchain consensus at the exact millisecond of issuance. It is mathematically impossible for an insider to forge a grade without breaking the chain.",
        bullet_s
    ))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph(
        "<b>2. Instant Sub-2-Second Zero-Friction Global Verification:</b> No recruiter account creation, no password logins, and zero OTP friction. A global HR manager in Zurich, Seattle, or Tokyo scans the permanent institutional QR code and receives mathematical confirmation in under 2 seconds.",
        bullet_s
    ))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph(
        "<b>3. 1,000x Cost Reduction:</b> Third-party background verification (BGV) firms charge ₹500 to ₹2,000 per check and take 2 to 4 weeks. Satyameva achieves verified instant proof for less than 50 paise (₹0.50) total compute cost.",
        bullet_s
    ))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph(
        "<b>4. Complete Student Self-Sovereignty:</b> Students own their permanent cryptographic credentials in a 3D digital wallet. Credentials never expire or disappear if a university changes portals.",
        bullet_s
    ))
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # SECTION 2: True Operational Costs
    # =========================================================================
    story.append(section_hdr("02", "REAL OPERATIONAL COSTS · EXACT UNIT ECONOMICS"))
    story.append(Spacer(1, 1.5*mm))

    cost_rows = [
        [Paragraph("<b>Component / Layer</b>", body_bold), Paragraph("<b>Technical Resource Consumption</b>", body_bold), Paragraph("<b>Unit Cost / Certificate</b>", body_bold), Paragraph("<b>Annual Batch (1,200 JUIT Students)</b>", body_bold)],
        [
            Paragraph("<b>Google Gemini 2.0 Flash AI</b>", body_bold),
            Paragraph("Multimodal document parsing (800 in / 150 out tokens at $0.10 / 1M tokens)", body_s),
            Paragraph("<b>$0.00014 (1.2 Paise)</b>", body_s),
            Paragraph("<b>₹14.40</b> (Entire Graduating Batch)", body_s)
        ],
        [
            Paragraph("<b>Consortium PoW Blockchain</b>", body_bold),
            Paragraph("In-house SHA-256 (Diff 4) local node. Zero gas fees ($0.00). 0.3s CPU compute.", body_s),
            Paragraph("<b>₹0.000 (Gas) + ₹0.005 (CPU)</b>", body_s),
            Paragraph("<b>₹6.00</b> (Compute electricity)", body_s)
        ],
        [
            Paragraph("<b>Cloud Storage (Cloudflare R2)</b>", body_bold),
            Paragraph("Zero egress fees. 500 KB per stamped PDF = 600 MB (10 GB Free Tier).", body_s),
            Paragraph("<b>₹0.000</b> (Within Free Tier)", body_s),
            Paragraph("<b>₹0.00</b>", body_s)
        ],
        [
            Paragraph("<b>VPS Hosting & API Server</b>", body_bold),
            Paragraph("Shared Linux Node (t4g.medium or $6/mo VPS = ₹500/mo amortized over 50k calls).", body_s),
            Paragraph("<b>₹0.38</b> per certificate", body_s),
            Paragraph("<b>₹480.00 / month</b> (Handles 50,000 API calls)", body_s)
        ],
        [
            Paragraph("<b>TOTAL OPERATIONAL EXPENSE</b>", body_bold),
            Paragraph("<b>End-to-end AI extraction, cryptographic hashing, and lifetime hosting</b>", body_bold),
            Paragraph("<b>&lt; ₹0.45 per credential</b>", body_bold),
            Paragraph("<b>&lt; ₹500.00 total batch cost</b>", body_bold)
        ]
    ]
    t_cost = Table(cost_rows, colWidths=[42*mm, 68*mm, 36*mm, 36*mm])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_GOLD),
        ('BACKGROUND', (0,-1), (-1,-1), LIGHT_GREEN),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_cost)
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # SECTION 3: Revenue Model: Who Pays & Who Collects
    # =========================================================================
    story.append(section_hdr("03", "REVENUE MODEL · WHO PAYS, WHO COLLECTS &amp; SUSTAINABILITY"))
    story.append(Spacer(1, 1.5*mm))

    rev_rows = [
        [Paragraph("<b>Stakeholder</b>", body_bold), Paragraph("<b>Financial Role &amp; Pricing Structure</b>", body_bold), Paragraph("<b>Value Realized / Justification</b>", body_bold)],
        [
            Paragraph("<b>Universities &amp; Campuses</b><br/>(JUIT, JIIT, JUET)", body_bold),
            Paragraph("<b>Annual B2B SaaS License:</b><br/>₹1,50,000 per campus / year. Managed by Admin via the new Subscription Engine.", body_s),
            Paragraph("Eliminates hundreds of hours spent manually answering employer verification emails; protects brand value; boosts NAAC/NIRF digital governance scores.", body_s)
        ],
        [
            Paragraph("<b>Corporate Employers &amp; BGV Agencies</b><br/>(Infosys, Google, AuthBridge)", body_bold),
            Paragraph("<b>Micro-Fee API Consumption:</b><br/>₹25 per automated verification check (or enterprise bulk volume packages).", body_s),
            Paragraph("Reduces background verification cycle from 3 weeks to 2 seconds and verification expenditure from ₹1,000 to ₹25 (97% savings).", body_s)
        ],
        [
            Paragraph("<b>Graduating Students</b>", body_bold),
            Paragraph("<b>100% Free Forever (₹0.00):</b><br/>No charges for credential storage, QR sharing, or PDF downloads.", body_s),
            Paragraph("Students are empowered with self-sovereign digital ownership of their life's achievements without financial barriers.", body_s)
        ],
        [
            Paragraph("<b>Revenue Collection &amp; Maintenance</b>", body_bold),
            Paragraph("<b>Collected by Satyameva Core Entity:</b><br/>Direct institutional bank billing &amp; automated API gateway billing.", body_s),
            Paragraph("Operating at &gt;92% gross margin, subscription proceeds fund node infrastructure, security audits, and RIDE incubator returns.", body_s)
        ]
    ]
    t_rev = Table(rev_rows, colWidths=[40*mm, 68*mm, 74*mm])
    t_rev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_CYAN),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_rev)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: Competitor Comparison
    # =========================================================================
    story.append(section_hdr("04", "COMPETITIVE LANDSCAPE · BENCHMARK AGAINST ALTERNATIVES"))
    story.append(Spacer(1, 1.5*mm))

    comp_rows = [
        [Paragraph("<b>Feature / Metric</b>", body_bold), Paragraph("<b>DigiLocker / NAD</b>", body_bold), Paragraph("<b>AuthBridge / BGV</b>", body_bold), Paragraph("<b>Blockcerts (MIT)</b>", body_bold), Paragraph("<b>Satyameva Aegis</b>", body_bold)],
        [Paragraph("Verification Speed", body_s), Paragraph("Minutes (OTP wait)", body_s), Paragraph("2–4 Weeks", body_s), Paragraph("10–30 Seconds", body_s), Paragraph("<b>&lt; 2.0 Seconds</b>", body_s)],
        [Paragraph("Cost per Check", body_s), Paragraph("Free (Govt)", body_s), Paragraph("₹500 – ₹2,000", body_s), Paragraph("Ethereum gas fees ($5)", body_s), Paragraph("<b>₹0.00 – ₹25 API</b>", body_s)],
        [Paragraph("Cross-Border Support", body_s), Paragraph("❌ Indian SIM Only", body_s), Paragraph("⚠️ Manual Agents", body_s), Paragraph("✅ Global", body_s), Paragraph("<b>✅ Instant Global</b>", body_s)],
        [Paragraph("Origin Tamper Proofing", body_s), Paragraph("❌ Blind Storage", body_s), Paragraph("❌ Trusts Paper", body_s), Paragraph("✅ Merkle Proof", body_s), Paragraph("<b>✅ PoW + 100k PBKDF2</b>", body_s)],
        [Paragraph("AI OCR Auto-Issuance", body_s), Paragraph("❌ Manual CSV", body_s), Paragraph("❌ Manual Review", body_s), Paragraph("❌ None", body_s), Paragraph("<b>✅ Gemini 2.0 Multimodal</b>", body_s)],
        [Paragraph("Password Security", body_s), Paragraph("Aadhaar OTP", body_s), Paragraph("None", body_s), Paragraph("Crypto Wallet Key", body_s), Paragraph("<b>DOB Encryption (DDMMYYYY)</b>", body_s)]
    ]
    t_comp = Table(comp_rows, colWidths=[36*mm, 36*mm, 36*mm, 36*mm, 38*mm])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_GOLD),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # SECTION 5: End-to-End Portal Workflows
    # =========================================================================
    story.append(section_hdr("05", "COMPLETE 4-PORTAL ARCHITECTURAL WORKFLOW"))
    story.append(Spacer(1, 1.5*mm))

    wf_rows = [
        [Paragraph("<b>Portal</b>", body_bold), Paragraph("<b>Operational Sequence &amp; Permission Gates</b>", body_bold)],
        [
            Paragraph("<b>1. Super-Admin Portal</b>", body_bold),
            Paragraph("<b>Registration Review &rarr; Approval &rarr; Subscription Allocation:</b> Admin reviews pending university signups. Upon approval, sets annual/trial subscription validity. Monitors system-wide health, active licenses, document revocation registry, and audit logs.", body_s)
        ],
        [
            Paragraph("<b>2. University Issuer Portal</b>", body_bold),
            Paragraph("<b>Student Approval &rarr; Gemini AI Extraction &rarr; Blockchain Anchoring:</b> Issuer approves student candidate accounts and dispatches email verification tokens. For issuance, uploads certificate: Gemini extracts Name, Roll No, Degree, and DOB. Proof-of-Work engine mines block, generates JUIT-crested QR, and alerts student via SMTP.", body_s)
        ],
        [
            Paragraph("<b>3. Student Portal</b>", body_bold),
            Paragraph("<b>Self-Sovereign Wallet &rarr; Stamped PDF &rarr; Grievance Tracking:</b> Gated until email verified and issuer approved. Student views credentials in 3D, downloads DOB-password-encrypted Stamped PDF (e.g. <code>01011999</code>), shares dynamic QR, and files credential correction/re-issuance requests with the registrar.", body_s)
        ],
        [
            Paragraph("<b>4. Public Verifier Portal</b>", body_bold),
            Paragraph("<b>Zero-Account Camera Scan &rarr; Instant Mathematical Verification:</b> Employer or embassy officer scans permanent QR or enters document hash. Verifier recomputes digest dynamically and validates against the blockchain: instant green VALID or red TAMPERED.", body_s)
        ]
    ]
    t_wf = Table(wf_rows, colWidths=[42*mm, 140*mm])
    t_wf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LIGHT_CYAN),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_wf)
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # SECTION 6: Role in India & Global Mobility
    # =========================================================================
    story.append(section_hdr("06", "ROLE IN INDIA &amp; GLOBAL MOBILITY (NEP 2020 &amp; WES)"))
    story.append(Spacer(1, 1.5*mm))

    story.append(Paragraph(
        "<b>National Role (India):</b><br/>"
        "• <b>National Education Policy (NEP 2020) Alignment:</b> Satyameva supports the Academic Bank of Credits (ABC) by providing cryptographically verifiable course certificates and degree credits that move with the student.<br/>"
        "• <b>DigiLocker &amp; NAD Integration:</b> Satyameva acts as the upstream cryptographic trust engine that pipes authenticated records directly into the National Academic Depository via standard REST APIs.<br/>"
        "• <b>Zero Administrative Backlog:</b> Automates 100% of inbound verification requests from PSU recruiters, state agencies, and educational boards.",
        bullet_s
    ))
    story.append(Spacer(1, 1.5*mm))
    story.append(Paragraph(
        "<b>Global Role (Worldwide Recruitment &amp; Visas):</b><br/>"
        "• <b>WES (World Education Services) &amp; NACES USA:</b> Foreign evaluation bodies require proof that transcripts originated from authentic university records. Satyameva provides a cryptographic verification URL accepted worldwide without physical mailing.<br/>"
        "• <b>Embassy Visa Verifications:</b> Consular officers verifying student visas for Canada, the US, UK, or Germany verify academic bona fides in 2 seconds with zero Indian SIM / OTP dependency.<br/>"
        "• <b>Multinational Tech Hiring:</b> Enables global recruiters (Google Zurich, Amazon Dublin) to conduct pre-onboarding checks instantly.",
        bullet_s
    ))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 7: Quantifiable Impact: Before vs After
    # =========================================================================
    story.append(section_hdr("07", "QUANTIFIABLE IMPACT · BEFORE VS AFTER SATYAMEVA"))
    story.append(Spacer(1, 1.5*mm))

    impact_rows = [
        [Paragraph("<b>Evaluation Dimension</b>", body_bold), Paragraph("<b>Status Quo (Before Satyameva)</b>", body_bold), Paragraph("<b>Transformed Reality (After Satyameva)</b>", body_bold)],
        [
            Paragraph("<b>Verification Turnaround Time</b>", body_bold),
            Paragraph("<b>2 to 4 Weeks</b> (Manual registrar postal mails &amp; emails)", body_s),
            Paragraph("<b>Under 2 Seconds</b> (Instant camera scan or hash lookup)", body_s)
        ],
        [
            Paragraph("<b>Verification Expenditure</b>", body_bold),
            Paragraph("<b>₹500 to ₹2,000</b> per candidate paid to BGV firms", body_s),
            Paragraph("<b>&lt; 50 Paise compute</b> (₹0 for student / ₹25 corporate API)", body_s)
        ],
        [
            Paragraph("<b>Counterfeiting &amp; Fraud Risk</b>", body_bold),
            Paragraph("<b>High</b> (Over 40,000 forged degrees detected annually in India)", body_s),
            Paragraph("<b>Mathematically Zero</b> (SHA-256 + 100k PBKDF2 salting)", body_s)
        ],
        [
            Paragraph("<b>University Registrar Workload</b>", body_bold),
            Paragraph("Dozens of hours per week manually searching physical archives", body_s),
            Paragraph("<b>100% Automated</b> inbound verification resolution", body_s)
        ],
        [
            Paragraph("<b>Student Document Ownership</b>", body_bold),
            Paragraph("Risk of lost/damaged paper certificates; expensive duplicates", body_s),
            Paragraph("<b>Self-Sovereign Digital Asset Wallet</b> with permanent QR codes", body_s)
        ],
        [
            Paragraph("<b>Document Privacy &amp; Security</b>", body_bold),
            Paragraph("Unencrypted static PDFs forwarded over email attachments", body_s),
            Paragraph("<b>DOB AES-256 Password Encryption</b> (DDMMYYYY auto-lock)", body_s)
        ]
    ]
    t_imp = Table(impact_rows, colWidths=[42*mm, 70*mm, 70*mm])
    t_imp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_GOLD),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_imp)
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # SECTION 8: DigiLocker Synergy
    # =========================================================================
    story.append(section_hdr("08", "DIGILOCKER SYNERGY · ORIGIN PROOF VS CLOUD STORAGE"))
    story.append(Spacer(1, 1.5*mm))

    story.append(Paragraph(
        "<b>The Misconception:</b> <i>\"Why not just use the government's DigiLocker?\"</i><br/>"
        "<b>The Technical Truth:</b> DigiLocker is a citizen-facing document repository (a cloud locker). It is <b>NOT</b> an origin-sealing cryptographic engine. If an unauthorized insider modifies a student's grade inside a university database prior to uploading to DigiLocker, DigiLocker will faithfully store and distribute a fraudulent certificate.<br/><br/>"
        "<b>Satyameva's Upstream Role:</b><br/>"
        "1. <b>Cryptographic Origin Sealing:</b> Satyameva operates at the point of issuance, locking the canonical data into the university's immutable Proof-of-Work blockchain.<br/>"
        "2. <b>API Push to DigiLocker:</b> Through our planned NAD REST bridge, Satyameva pushes cryptographically sealed credentials into the student's DigiLocker account. DigiLocker receives an unforgeable, pre-verified asset.<br/>"
        "3. <b>Cross-Border Employer Access:</b> DigiLocker requires Indian mobile OTP authentication. Satyameva provides the public, instant international verification protocol that DigiLocker cannot fulfill for foreign employers.",
        bullet_s
    ))
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # SECTION 9: 360° Benefits of Verification
    # =========================================================================
    story.append(section_hdr("09", "360° BENEFITS ACROSS ALL STAKEHOLDERS"))
    story.append(Spacer(1, 1.5*mm))

    story.append(Paragraph(
        "<b>• For Students:</b> Immediate lifetime ownership; immune to physical certificate loss; 1-click sharing to LinkedIn; DOB-protected downloaded PDFs prevent identity theft; streamlined international visa and masters admissions.<br/>"
        "<b>• For Employers:</b> 100% confidence in candidate credentials; eliminated 3-week background verification delays; automated HR onboarding via REST API; zero legal liability from credential fraud.<br/>"
        "<b>• For Universities (JUIT / JIIT / JUET):</b> Complete protection of brand prestige and alumni reputation; substantial administrative cost savings; automated grievance &amp; correction workflows; compliance with UGC and NEP 2020 mandates.",
        bullet_s
    ))
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # SECTION 10: Technical Implementations
    # =========================================================================
    story.append(section_hdr("10", "TECHNICAL SPECIFICATIONS OF LIVE PROTOCOL ENHANCEMENTS"))
    story.append(Spacer(1, 1.5*mm))

    tech_p = Paragraph(
        "<b>1. Automated PDF Password Encryption (DOB in DDMMYYYY):</b> Extracted via Gemini 2.0 Flash AI multimodal parsing and encrypted with AES-256 via <code>pikepdf</code>. Protects student privacy upon download.<br/>"
        "<b>2. Mobile LAN QR Scanning:</b> Auto-detects server LAN IPv4 at boot (<code>run.py</code>) and translates localhost URLs so smartphone cameras on campus Wi-Fi instantly open the verification page.<br/>"
        "<b>3. Two-Tier Permission &amp; Approval Architecture:</b> Super-Admin approves universities and sets subscription validity; University Issuers approve individual student accounts and dispatch secure email verification links.<br/>"
        "<b>4. Branded SMTP Notification Engine:</b> Configured as <code>Satyameva • Jaypee Credentials</code> (<code>satyameva-noreply@jaypeecredentials.in</code>) with async background queueing.",
        bullet_s
    )
    story.append(tech_p)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generated Strategy PDF: {out_path}")

    # Copy to Desktop
    desktop_dst = "C:/Users/hp/Desktop/SATYAMEVA_BUSINESS_STRATEGY.pdf"
    try:
        shutil.copyfile(out_path, desktop_dst)
        print(f"[OK] Copied to: {desktop_dst}")
    except Exception as e:
        print(f"[WARN] Failed to copy to {desktop_dst}: {e}")

if __name__ == '__main__':
    build_pdf()
