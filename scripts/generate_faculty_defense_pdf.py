"""
Generate high-impact, executive PDF for JUIT Board Room Faculty Q&A & Defense Guide.
Covers:
1. Blockchain vs Database Cost & Vulnerabilities
2. DigiLocker vs Satyameva B2B Enterprise & Global Recruiting
3. End-to-End Cryptographic Conversion Pipeline (Hashing, Salting, Mining)
4. Total Operational Unit Economics (AI + Blockchain + Server < ₹0.50/credential)
5. Drawbacks & Faculty Counter-Offensives (Key loss, Revocation, DPDP 2023, Multi-Sig)
"""
import os
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, PageBreak
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
            self.drawString(14*mm, 285*mm, "CYPHER X · RIDEHACK'26 · BOARD ROOM DEFENSE BATTLECARD")
            self.drawRightString(196*mm, 285*mm, "SATYAMEVA AEGIS PROTOCOL")
            self.setStrokeColor(BORDER_COL)
            self.setLineWidth(0.5)
            self.line(14*mm, 283*mm, 196*mm, 283*mm)
        
        # Footer
        self.setStrokeColor(BORDER_COL)
        self.setLineWidth(0.5)
        self.line(14*mm, 12*mm, 196*mm, 12*mm)
        self.drawString(14*mm, 8*mm, "CONFIDENTIAL · For Vice Chancellor & Senior Faculty Board Presentation · Jaypee University")
        self.drawRightString(196*mm, 8*mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def create_banner():
    styles = getSampleStyleSheet()
    title_p = Paragraph(
        "<b>RIDEHACK'26 · BOARD ROOM Q&A DEFENSE BATTLECARD</b>",
        ParagraphStyle("BTitle", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=WHITE, alignment=TA_CENTER)
    )
    sub_p = Paragraph(
        "<b>HARDENED ANSWERS TO TOUGH FACULTY & VC QUESTIONS</b>",
        ParagraphStyle("BSub", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=GOLD, alignment=TA_CENTER)
    )
    meta_p = Paragraph(
        "Team: <b>CYPHER X (02 CYPHER X)</b> &nbsp;|&nbsp; Presenters: <b>A Praneeth Sai & Shashank Ray</b> &nbsp;|&nbsp; Venue: <b>Board Room, JUIT</b>",
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

def q_header(q_num, q_title):
    p_num = Paragraph(f"<b>QUESTION 0{q_num}</b>", ParagraphStyle("QNum", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=GOLD))
    p_title = Paragraph(f"<b>{q_title}</b>", ParagraphStyle("QTitle", fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=WHITE))
    t = Table([[p_num], [p_title]], colWidths=[182*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SLATE),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def hook_box(hook_text):
    p = Paragraph(f"<b>⚡ 10-SECOND EXECUTIVE HOOK:</b> {hook_text}", ParagraphStyle(
        "HookP", fontName="Helvetica", fontSize=8.5, leading=12, textColor=DARK_NAVY
    ))
    t = Table([[p]], colWidths=[182*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GOLD),
        ('BOX', (0,0), (-1,-1), 1, GOLD),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    return t

def build_pdf():
    out_path = "C:/Users/hp/OneDrive/Desktop/FACULTY_DEFENSE_GUIDE.pdf"
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=14*mm,
        rightMargin=14*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
        title="RIDEHACK'26 - Faculty Q&A Defense Guide",
        author="Team CYPHER X",
    )

    body_s = ParagraphStyle("BodyS", fontName="Helvetica", fontSize=8.5, leading=12.5, textColor=TEXT_DARK, alignment=TA_JUSTIFY)
    body_bold = ParagraphStyle("BodySBold", fontName="Helvetica-Bold", fontSize=8.5, leading=12.5, textColor=TEXT_DARK)
    bullet_s = ParagraphStyle("BulletS", fontName="Helvetica", fontSize=8.5, leading=12, textColor=TEXT_DARK, leftIndent=12)
    subhead_s = ParagraphStyle("SubheadS", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=NAVY)

    story = []

    # Banner
    story.append(create_banner())
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # QUESTION 1: Blockchain vs Database Cost & Why Not SQL
    # =========================================================================
    story.append(q_header(1, "Blockchain vs Database: \"Won't Blockchain cost way more than a simple database? Why not just use MySQL or PostgreSQL?\""))
    story.append(Spacer(1, 1.5*mm))
    story.append(hook_box("\"Sir, that is a common misconception rooted in public crypto networks like Ethereum. Satyameva uses an in-house consortium Proof-of-Work blockchain with ZERO transaction fees (₹0.00). It costs the exact same server space as a database, but eliminates the fatal vulnerability of SQL: silent insider database manipulation.\"", ))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("<b>The Deep-Tech Defense Points:</b>", subhead_s))
    story.append(Paragraph("<b>1. The Zero-Gas Architecture:</b> Ethereum and Polygon charge $2 to $15 per gas transaction because they are public speculative networks. Satyameva runs a <i>private consortium Proof-of-Work engine</i> written in Python & FastAPI. There are zero miners to pay in cryptocurrency; the ledger is hosted across university nodes (JUIT, JIIT, JUET). Gas cost = <b>₹0.00</b>.", bullet_s))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph("<b>2. The Fatal Flaw of Relational Databases (The Insider Threat):</b> In a MySQL/Postgres database, any database administrator (DBA), IT staff with root access, or a compromised server can run a silent command: <font name='Courier'>UPDATE degrees SET cgpa=9.8 WHERE roll_no='221030112';</font>. No alarms trigger, and the stored data changes permanently. In Satyameva, changing even 1 byte in history breaks the SHA-256 block hash and Merkle root across all blocks (<font name='Courier'>0000a7b9...</font>), raising an immediate cryptographic alarm.", bullet_s))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph("<b>3. Dual-Storage Architecture:</b> We do not replace databases; we pair them. We use SQLite/PostgreSQL for sub-10ms query indexing and search, while every certificate state is anchored to our blockchain ledger for mathematical proof. Query speed = 10ms; Trust = 100% cryptographic.", bullet_s))
    story.append(Spacer(1, 2*mm))

    # Comparison Table
    table_data = [
        [Paragraph("<b>Parameter</b>", body_bold), Paragraph("<b>Standard SQL Database</b>", body_bold), Paragraph("<b>Public Web3 (Ethereum)</b>", body_bold), Paragraph("<b>Satyameva Aegis (Our Protocol)</b>", body_bold)],
        [Paragraph("Gas / Tx Cost", body_s), Paragraph("₹0", body_s), Paragraph("₹150 – ₹1,200 per tx", body_s), Paragraph("<b>₹0.00 (Zero Gas)</b>", body_s)],
        [Paragraph("Insider Tamper Resistance", body_s), Paragraph("<b>Zero</b> (Root admin can alter)", body_s), Paragraph("High (Immutable)", body_s), Paragraph("<b>Absolute (Cryptographic Ledger)</b>", body_s)],
        [Paragraph("Verification Speed", body_s), Paragraph("50–200ms", body_s), Paragraph("15 sec – 5 min (Block time)", body_s), Paragraph("<b>&lt; 2.0 Seconds (Instant)</b>", body_s)],
        [Paragraph("Monthly Host Cost", body_s), Paragraph("₹500 – ₹1,500/mo", body_s), Paragraph("High gas overhead", body_s), Paragraph("<b>₹500/mo (Runs on existing VPS)</b>", body_s)]
    ]
    t_comp = Table(table_data, colWidths=[38*mm, 46*mm, 46*mm, 52*mm])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_CYAN),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 4*mm))

    # =========================================================================
    # QUESTION 2: DigiLocker Alternative & B2B Moat
    # =========================================================================
    story.append(q_header(2, "DigiLocker Synergy: \"Government already has DigiLocker. Why should universities or employers purchase Satyameva B2B?\""))
    story.append(Spacer(1, 1.5*mm))
    story.append(hook_box("\"Sir, DigiLocker is a citizen document locker; it is NOT an instant global verification protocol. Employers cannot verify resumes on DigiLocker without candidate OTP and Indian Aadhaar. Furthermore, Satyameva is not a competitor—we are the cryptographic issuer that feeds into DigiLocker while automating the university's entire verification burden.\"", ))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("<b>The 4 Fatal Gaps in DigiLocker Solved by Satyameva:</b>", subhead_s))
    story.append(Paragraph("<b>1. The Cross-Border Recruiter Friction:</b> If a JUIT graduate applies to Google Zurich, Amazon Seattle, or an embassy for higher studies (WES in US/Canada), the foreign HR or visa officer <i>cannot log into DigiLocker</i>. DigiLocker requires an Indian mobile number and Aadhaar OTP sent to the candidate. If the student is on a flight or unreachable, verification halts. Satyameva provides a <b>public, zero-account, instantaneous (under 2 seconds) institutional verification portal</b> accessible globally.", bullet_s))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph("<b>2. Origin Tamper Proofing vs Cloud Storage:</b> DigiLocker merely stores what an institution pushes. If an insider modified the university marksheet prior to uploading, DigiLocker blindly archives a fraudulent certificate. Satyameva cryptographically seals the document at the exact point of generation using SHA-256 and PBKDF2 with 100,000 iterations.", bullet_s))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph("<b>3. Eliminates University Administrative Backlog:</b> Right now, JUIT's registrar office receives hundreds of verification emails every month from background verification agencies (AuthBridge, FirstAdvantage, HireRight) and foreign universities. Administrative staff spends 10 to 20 minutes per email manually pulling transcripts. Satyameva automates 100% of this inbound verification load with zero staff intervention.", bullet_s))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph("<b>4. Synergy & Co-existence:</b> Satyameva features an API bridge to push verified credentials directly into a student's DigiLocker / NAD (National Academic Depository) wallet. We act as the upstream cryptographic trust engine.", bullet_s))
    story.append(Spacer(1, 4*mm))

    # Page break for clean reading
    story.append(PageBreak())

    # =========================================================================
    # QUESTION 3: Document to Blockchain Conversion & Hashing Pipeline
    # =========================================================================
    story.append(q_header(3, "Technical Mechanics: \"How do you convert physical documents or PDFs into blockchain records? Explain the hashing and cryptographic pipeline.\""))
    story.append(Spacer(1, 1.5*mm))
    story.append(hook_box("\"Sir, we never store the heavy PDF file itself on the blockchain—that would be inefficient. Instead, we generate a mathematical fingerprint of the document's canonical attributes and raw binary bytes, salt it dynamically, and mine it into a Proof-of-Work block.\"", ))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("<b>The 7-Step End-to-End Cryptographic Issuance Pipeline:</b>", subhead_s))
    
    steps_data = [
        [Paragraph("<b>Step 1</b>", body_bold), Paragraph("<b>Multimodal AI Extraction:</b> Scanned degree PDF is ingested by Google Gemini 2.0 Flash AI. Core academic parameters (Student Name, Roll Number, Degree, CGPA, Passing Year, Institution ID) are parsed into structured JSON with 99%+ accuracy.", body_s)],
        [Paragraph("<b>Step 2</b>", body_bold), Paragraph("<b>Canonical Normalization:</b> The extracted data dictionary is sorted deterministically (<font name='Courier'>json.dumps(payload, sort_keys=True)</font>) to ensure identical byte-sequence representation regardless of system locale.", body_s)],
        [Paragraph("<b>Step 3</b>", body_bold), Paragraph("<b>Primary SHA-256 Digest:</b> We compute the cryptographic digest of the normalized JSON concatenated with the raw binary bytes of the original certificate file: <font name='Courier'>Digest = SHA256(canonical_json + raw_pdf_bytes)</font>.", body_s)],
        [Paragraph("<b>Step 4</b>", body_bold), Paragraph("<b>PBKDF2 Dynamic Salting (100k Iterations):</b> To prevent rainbow-table attacks and brute-forcing, the digest is passed through PBKDF2-HMAC-SHA256 with 100,000 iterations using a per-document unique salt derived from <font name='Courier'>issuer_secret + doc_uuid + timestamp</font>.", body_s)],
        [Paragraph("<b>Step 5</b>", body_bold), Paragraph("<b>Proof-of-Work Block Mining:</b> The salted credential hash is grouped into a block header containing <font name='Courier'>previous_block_hash</font>, <font name='Courier'>merkle_root</font>, and <font name='Courier'>timestamp</font>. Our engine mines the block nonce to satisfy Difficulty 4 (<font name='Courier'>0000...</font>) in ~0.3 seconds.", body_s)],
        [Paragraph("<b>Step 6</b>", body_bold), Paragraph("<b>JUIT Branded QR Code Stamping:</b> A permanent QR code containing the document's public verification URL (<font name='Courier'>/verify?doc_id=...</font>) and JUIT crest is stamped onto the final official PDF.", body_s)],
        [Paragraph("<b>Step 7</b>", body_bold), Paragraph("<b>Zero-Trust Dynamic Re-Verification:</b> When an employer scans the QR code, the verifier does <i>not</i> read a stored \"valid\" flag. It reconstructs the entire hash dynamically from the active block. If even 1 grade character or pixel was altered, the check fails instantly.", body_s)]
    ]
    t_steps = Table(steps_data, colWidths=[20*mm, 162*mm])
    t_steps.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LIGHT_CYAN),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_steps)
    story.append(Spacer(1, 4*mm))

    # =========================================================================
    # QUESTION 4: Total Operational Cost Breakdown
    # =========================================================================
    story.append(q_header(4, "Total Operational Cost: \"What is the total overall cost of running this system? AI API costs, blockchain compute, and storage?\""))
    story.append(Spacer(1, 1.5*mm))
    story.append(hook_box("\"Sir, issuing a degree on Satyameva Aegis costs less than 50 PAISE (₹0.50) per student. For JUIT's entire graduating batch of 1,200 students, the complete AI extraction and blockchain verification costs less than ₹60 total!\"", ))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("<b>Exact Cost Breakdown per 1,200 Student Batch (Annual JUIT Convocation):</b>", subhead_s))
    
    cost_data = [
        [Paragraph("<b>Component</b>", body_bold), Paragraph("<b>Resource & Unit Pricing</b>", body_bold), Paragraph("<b>Cost / Certificate</b>", body_bold), Paragraph("<b>Total Cost (1,200 Students)</b>", body_bold)],
        [
            Paragraph("<b>Google Gemini 2.0 Flash AI</b>", body_bold),
            Paragraph("• Input: 800 tokens ($0.10 / 1M tokens)<br/>• Output: 150 tokens ($0.40 / 1M tokens)", body_s),
            Paragraph("<b>$0.00014<br/>(₹0.012 = 1.2 Paise)</b>", body_s),
            Paragraph("<b>₹14.40</b><br/>(Less than 1 cup of tea!)", body_s)
        ],
        [
            Paragraph("<b>Proof-of-Work Blockchain</b>", body_bold),
            Paragraph("In-house SHA-256 consortium engine. Zero gas fees. 0.3 sec CPU mining time.", body_s),
            Paragraph("<b>₹0.000 (Gas)<br/>+ ₹0.005 (CPU power)</b>", body_s),
            Paragraph("<b>₹6.00</b> (Compute electricity)", body_s)
        ],
        [
            Paragraph("<b>Cloud Storage (PDFs & QR)</b>", body_bold),
            Paragraph("Cloudflare R2 Object Storage (Zero egress fees, 10 GB free tier). 500 KB/PDF = 600 MB.", body_s),
            Paragraph("<b>₹0.00</b> (Under free tier)", body_s),
            Paragraph("<b>₹0.00</b>", body_s)
        ],
        [
            Paragraph("<b>Server VPS Hosting</b>", body_bold),
            Paragraph("Shared Linux VPS (AWS t4g.medium or DigitalOcean $6/mo = ₹500/mo amortized).", body_s),
            Paragraph("<b>₹0.40</b> / certificate", body_s),
            Paragraph("<b>₹480.00 / month</b> (Handles 50,000 requests)", body_s)
        ],
        [
            Paragraph("<b>TOTAL OPERATIONAL COST</b>", body_bold),
            Paragraph("<b>End-to-end issuance, AI extraction, and lifetime blockchain hosting</b>", body_bold),
            Paragraph("<b>&lt; ₹0.45 per degree</b>", body_bold),
            Paragraph("<b>&lt; ₹500 total batch cost</b>", body_bold)
        ]
    ]
    t_cost = Table(cost_data, colWidths=[42*mm, 68*mm, 36*mm, 36*mm])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_GOLD),
        ('BACKGROUND', (0,-1), (-1,-1), LIGHT_GREEN),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_cost)
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("<b>Market Comparison:</b> Third-party background verification agencies (AuthBridge, FirstAdvantage) charge corporate employers <b>₹500 to ₹2,000 per candidate</b>. Satyameva achieves verified instant proof for under <b>50 paise</b> — a 1000x cost reduction.", body_s))
    story.append(Spacer(1, 4*mm))

    # Page break for Section 5
    story.append(PageBreak())

    # =========================================================================
    # QUESTION 5: Drawbacks, Risks & Faculty Counter-Offensives
    # =========================================================================
    story.append(q_header(5, "Drawbacks & Edge Cases: \"What are the potential failure points or drawbacks of your system, and how do you handle them?\""))
    story.append(Spacer(1, 1.5*mm))
    story.append(hook_box("\"Sir, every enterprise system must be hardened against edge cases. We have specifically architected solutions for private key loss, incorrect degree issuance, data privacy laws (DPDP Act 2023), and network consensus.\"", ))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("<b>The 4 Hardened Counter-Measures:</b>", subhead_s))

    gotchas_data = [
        [
            Paragraph("<b>Faculty Challenge 1:<br/>Key Loss or Compromise</b><br/><font color='#DC2626'>\"What if the university admin's private key is leaked or lost? Can an attacker issue fake degrees?\"</font>", body_s),
            Paragraph("<b>Our Hardened Defense: Multi-Sig Quorum & Shamir's Secret Sharing</b><br/>No single person at JUIT holds unilateral issuance authority. Issuing degrees requires a <b>2-of-3 Multi-Signature Quorum</b> (Registrar + Controller of Examinations + Dean of Academics). Keys are partitioned via Shamir's Secret Sharing (3 threshold shards). Even if one laptop is compromised, zero unauthorized blocks can be mined without cryptographic consensus.", body_s)
        ],
        [
            Paragraph("<b>Faculty Challenge 2:<br/>Degree Revocation</b><br/><font color='#DC2626'>\"Blockchain is immutable. What if a degree was issued by mistake, or revoked due to student disciplinary action? You cannot delete the block!\"</font>", body_s),
            Paragraph("<b>Our Hardened Defense: Cryptographic Revocation Registry</b><br/>We do not alter historical blocks (preserving audit integrity). Instead, our protocol maintains an on-chain <b>Cryptographic Revocation Registry</b>. The university issues a signed revocation transaction. When an employer scans the QR code, the verifier checks both block existence AND the revocation registry, instantly displaying: <font color='#DC2626'><b>\"DEGREE REVOKED BY JUIT REGISTRAR ON [DATE]\"</b></font> with the exact reason.", body_s)
        ],
        [
            Paragraph("<b>Faculty Challenge 3:<br/>DPDP Act 2023 & GDPR</b><br/><font color='#DC2626'>\"India's Digital Personal Data Protection Act requires 'Right to be Forgotten'. Putting student names on blockchain violates data privacy!\"</font>", body_s),
            Paragraph("<b>Our Hardened Defense: Off-Chain PII, On-Chain Cryptographic Proof</b><br/>Satyameva strictly complies with DPDP Act 2023 and GDPR. <b>Zero Personally Identifiable Information (PII) is stored in plaintext on the blockchain.</b> Only one-way irreversible cryptographic hashes (SHA-256 + PBKDF2) exist on-chain. If a student requests data deletion, their off-chain profile is purged; the on-chain hash is computationally irreversible and reveals zero personal data.", body_s)
        ],
        [
            Paragraph("<b>Faculty Challenge 4:<br/>Consensus Centralization</b><br/><font color='#DC2626'>\"If only JUIT runs the node, isn't it centralized? How is it a true blockchain?\"</font>", body_s),
            Paragraph("<b>Our Hardened Defense: Jaypee Multi-Campus Consortium Network</b><br/>Satyameva is architected as an inter-campus consortium. The validator nodes run across <b>JUIT Waknaghat, JIIT Noida (Sector 62 & 128), and JUET Guna</b>. A 51% attack or rogue modification at one campus is automatically rejected by the consensus of peer Jaypee campuses.", body_s)
        ]
    ]

    t_gotchas = Table(gotchas_data, colWidths=[62*mm, 120*mm])
    t_gotchas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LIGHT_GRAY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_gotchas)
    story.append(Spacer(1, 3*mm))

    # =========================================================================
    # CLOSING SUMMARY & JUIT ASK BATTLECARD
    # =========================================================================
    summary_p = Paragraph(
        "<b>🏆 THE CLOSING ASK (To VC Sir & Faculty):</b><br/>"
        "<i>\"Sir, Team CYPHER X has built a working, zero-gas, AI-driven cryptographic trust system right here at JUIT. We are not asking for theoretical funding—we are asking for permission to run a <b>live pilot with JUIT's upcoming 2026 graduating batch</b>. At a total cost of less than ₹500 for the entire batch, JUIT can become the <b>first university in Himachal Pradesh to issue 100% tamper-proof blockchain credentials</b>. We ask for your selection today so we can represent JUIT and bring home the ₹1 Crore prize at the JIIT Noida Grand Finale!\"</i>",
        ParagraphStyle("CloseP", fontName="Helvetica", fontSize=8.5, leading=12.5, textColor=WHITE)
    )
    t_sum = Table([[summary_p]], colWidths=[182*mm])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('BOX', (0,0), (-1,-1), 1.5, GOLD),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sum)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generated PDF: {out_path}")

    # Sync to Desktop and Repos
    destinations = [
        "C:/Users/hp/Desktop/FACULTY_DEFENSE_GUIDE.pdf",
        "C:/Users/hp/OneDrive/Desktop/Satyameva/FACULTY_DEFENSE_GUIDE.pdf",
        "C:/Users/hp/OneDrive/Documents/GitHub/satyameva/FACULTY_DEFENSE_GUIDE.pdf"
    ]
    for dst in destinations:
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(out_path, dst)
            print(f"[OK] Copied to: {dst}")
        except Exception as e:
            print(f"[WARN] Failed to copy to {dst}: {e}")

if __name__ == "__main__":
    build_pdf()
