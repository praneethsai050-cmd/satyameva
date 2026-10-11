"""
Generate executive printable PDF for JUIT Board Room 10-Minute Pitch Playbook.
Covers:
- Pre-Pitch Checklist & Hardware Protocol
- Time Breakdown Table
- 4-Minute Slide Presentation (Slides 1-7 Tag Team)
- 4-Minute Live Prototype Demo (Praneeth Sai Step-by-Step)
- Return to Slides & The JUIT Ask (Shashank Ray)
- VC & Faculty Q&A Playbook
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
            self.drawString(14*mm, 285*mm, "CYPHER X · RIDEHACK'26 · 10-MINUTE BOARD ROOM PITCH PLAYBOOK")
            self.drawRightString(196*mm, 285*mm, "SATYAMEVA AEGIS")
            self.setStrokeColor(BORDER_COL)
            self.setLineWidth(0.5)
            self.line(14*mm, 283*mm, 196*mm, 283*mm)
        
        # Footer
        self.setStrokeColor(BORDER_COL)
        self.setLineWidth(0.5)
        self.line(14*mm, 12*mm, 196*mm, 12*mm)
        self.drawString(14*mm, 8*mm, "CONFIDENTIAL · JUIT Waknaghat Board Room Round · Team CYPHER X (02 CYPHER X)")
        self.drawRightString(196*mm, 8*mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def create_banner():
    title_p = Paragraph(
        "<b>RIDEHACK'26 · BOARD ROOM 10-MINUTE PITCH PLAYBOOK</b>",
        ParagraphStyle("BTitle", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=WHITE, alignment=TA_CENTER)
    )
    sub_p = Paragraph(
        "<b>COMPLETE TAG-TEAM SCRIPT, LIVE DEMO CUES & FACULTY Q&A</b>",
        ParagraphStyle("BSub", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=GOLD, alignment=TA_CENTER)
    )
    meta_p = Paragraph(
        "Team: <b>CYPHER X</b> &nbsp;|&nbsp; Presenters: <b>A Praneeth Sai & Shashank Ray</b> &nbsp;|&nbsp; Date: <b>1 October 2026 (11:00 AM)</b>",
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

def section_hdr(title, subtitle=""):
    p_title = Paragraph(f"<b>{title}</b>", ParagraphStyle("STitle", fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=WHITE))
    data = [[p_title]]
    if subtitle:
        p_sub = Paragraph(subtitle, ParagraphStyle("SSub", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=GOLD))
        data.append([p_sub])
    t = Table(data, colWidths=[182*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SLATE),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    return t

def speech_card(slide_num, title, presenter, time_win, speech_text, visual_cue=""):
    p_meta = Paragraph(
        f"<b>SLIDE {slide_num}: {title}</b> &nbsp;|&nbsp; <b>Presenter:</b> {presenter} &nbsp;|&nbsp; <b>Time:</b> {time_win}",
        ParagraphStyle("SCMeta", fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=NAVY)
    )
    rows = [[p_meta]]
    if visual_cue:
        p_vis = Paragraph(f"<i>Visual Cue:</i> {visual_cue}", ParagraphStyle("SCVis", fontName="Helvetica-Oblique", fontSize=8, leading=11, textColor=MUTED_TEXT))
        rows.append([p_vis])
    p_speech = Paragraph(f"<b>Speech:</b> \"{speech_text}\"", ParagraphStyle("SCSpeech", fontName="Helvetica", fontSize=8.5, leading=12.5, textColor=TEXT_DARK, alignment=TA_JUSTIFY))
    rows.append([p_speech])

    t = Table(rows, colWidths=[182*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def demo_step_card(step_num, title, action_text, narration_text):
    p_hdr = Paragraph(f"<b>DEMO STEP {step_num}: {title}</b>", ParagraphStyle("DSHdr", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=DARK_NAVY))
    p_act = Paragraph(f"<b>Action on Screen:</b> {action_text}", ParagraphStyle("DSAct", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=CYAN))
    p_narr = Paragraph(f"<b>Live Narration (Praneeth Sai):</b> \"{narration_text}\"", ParagraphStyle("DSNarr", fontName="Helvetica", fontSize=8.5, leading=12, textColor=TEXT_DARK, alignment=TA_JUSTIFY))
    t = Table([[p_hdr], [p_act], [p_narr]], colWidths=[182*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_CYAN),
        ('BOX', (0,0), (-1,-1), 1, CYAN),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def build_pdf():
    out_path = "C:/Users/hp/OneDrive/Desktop/JUIT_VC_PITCH_PLAYBOOK_10MIN.pdf"
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=14*mm,
        rightMargin=14*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
        title="RIDEHACK'26 - 10-Minute Board Room Pitch Playbook",
        author="Team CYPHER X",
    )

    body_s = ParagraphStyle("BodyS", fontName="Helvetica", fontSize=8.5, leading=12, textColor=TEXT_DARK)
    body_bold = ParagraphStyle("BodySBold", fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=TEXT_DARK)

    story = []

    # Banner
    story.append(create_banner())
    story.append(Spacer(1, 2.5*mm))

    # Time Schedule Table
    story.append(section_hdr("⏱️ STRICT 10-MINUTE TIME SCHEDULE & PRESENTER ROLES"))
    story.append(Spacer(1, 1.5*mm))

    time_data = [
        [Paragraph("<b>Time Window</b>", body_bold), Paragraph("<b>Phase / Section</b>", body_bold), Paragraph("<b>Lead Presenter</b>", body_bold), Paragraph("<b>Key Objective & Outcome</b>", body_bold)],
        [Paragraph("<b>0:00 – 4:00</b>", body_s), Paragraph("Phase 1: 7-Slide Pitch Deck", body_s), Paragraph("Both (Tag-team)", body_s), Paragraph("Establish Crisis, Satyameva Architecture, Economics & JUIT Ask", body_s)],
        [Paragraph("<b>4:00 – 7:30</b>", body_s), Paragraph("Phase 2: Live Prototype Demo", body_s), Paragraph("Praneeth Sai", body_s), Paragraph("Gemini AI Extraction ➔ Student JUIT QR ➔ Public /verify & Anti-Tamper", body_s)],
        [Paragraph("<b>7:30 – 8:00</b>", body_s), Paragraph("Phase 3: Closing The Ask", body_s), Paragraph("Shashank Ray", body_s), Paragraph("Formal request for JUIT In-House Pilot & Selection for JIIT Noida", body_s)],
        [Paragraph("<b>8:00 – 10:00</b>", body_s), Paragraph("Phase 4: VC & Faculty Q&A", body_s), Paragraph("Both", body_s), Paragraph("Bulletproof defense on Cost, DigiLocker, Hashing, Drawbacks", body_s)]
    ]
    t_time = Table(time_data, colWidths=[26*mm, 50*mm, 36*mm, 70*mm])
    t_time.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_GOLD),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_time)
    story.append(Spacer(1, 3*mm))

    # Phase 1: Slide Presentation
    story.append(section_hdr("PHASE 1: 4-MINUTE SLIDE PRESENTATION (SLIDES 1–7)"))
    story.append(Spacer(1, 1.5*mm))

    story.append(speech_card(
        "1", "Cover & Opening Hook", "Praneeth Sai", "0:00 – 0:40",
        "Respected Vice Chancellor Sir, esteemed faculty members, and IIC coordinators. Good morning! We are Team CYPHER X — I am Praneeth Sai, and with me is my co-founder Shashank Ray. We are honored to present Satyameva Aegis: a decentralized cryptographic trust protocol engineered to transform university credentials into tamper-proof digital assets verified in under two seconds. Our mission is to protect the academic reputation of premier institutions like JUIT, eliminate credential fraud, and provide our graduating students with self-sovereign, lifetime-verified degrees. Our system is fully operational and ready for immediate campus adoption.",
        "Slide 1 on screen: SATYAMEVA AEGIS with JUIT Gold & Navy crest badge."
    ))
    story.append(Spacer(1, 1.5*mm))

    story.append(speech_card(
        "2", "The Problem: Threat to University Brand", "Shashank Ray", "0:40 – 1:20",
        "Sir, India currently faces an unprecedented crisis in academic integrity. Over 40,000 fake degrees are officially uncovered every year, with syndicates openly selling counterfeit credentials. When a fake degree claiming to be from a premier institution circulates, it directly devalues the genuine achievements of every single JUIT graduate and damages our university's brand equity. Furthermore, multinational employers spend between two to four weeks waiting for registrar email verifications, incurring costs of ₹500 to ₹2,000 per candidate. Meanwhile, our administrative staff spends valuable hours manually pulling archive records. Traditional paper certificates and static PDFs offer zero cryptographic tamper-resistance. That is the vulnerability Satyameva Aegis solves.",
        "Slide 2 on screen: Three Crisis Pillars: 40k+ Fake Degrees, 2-4 Weeks Delay, Zero Student Ownership."
    ))
    story.append(Spacer(1, 1.5*mm))

    story.append(speech_card(
        "3", "The Solution: Satyameva Aegis Protocol", "Shashank Ray", "1:20 – 2:00",
        "Satyameva Aegis establishes a 360-degree digital trust ecosystem: First, For JUIT: We empower the Registrar's office with automated Google Gemini AI data extraction. Whether issuing a single degree or a batch of 5,000 via CSV, the process takes seconds, running on an in-house proof-of-work blockchain with zero gas fees. Second, For JUIT Students: Every graduate receives a self-sovereign digital asset wallet. Their credentials carry a permanent institutional QR code embedded with the official JUIT Waknaghat crest that never expires. Third, For Employers: Recruiters at Google, Infosys, or Amazon need zero accounts. Scanning the JUIT QR code provides cryptographic confirmation in under two seconds, with mathematical proof that not a single grade or character has been tampered with.",
        "Slide 3 on screen: Three Solution Pillars: Universities, Students, Employers."
    ))
    story.append(Spacer(1, 1.5*mm))

    story.append(speech_card(
        "4", "Deep-Tech Architecture & IP Moat", "Praneeth Sai", "2:00 – 2:45",
        "Under the hood, Satyameva Aegis is engineered with deep-tech defensibility: 1. Custom Proof-of-Work Blockchain: We built our own SHA-256 ledger (Difficulty 4) dual-persisted across SQLite and JSON. This completely eliminates volatile cryptocurrency gas fees, ensuring zero recurring operational cost for JUIT. 2. Zero-Trust Cryptography: Every credential uses PBKDF2-HMAC-SHA256 with 100,000 iterations and per-document dynamic salting. Our verifier does NOT trust stored database hashes — it re-derives the cryptographic digest from raw payload on every single check. Any direct database tampering results in an immediate TAMPERED verdict. 3. Google Gemini 2.0 Flash AI: Reads scanned certificate PDFs and auto-populates student records with 99%+ accuracy. 4. Permanent JUIT Crest QR: Error Correction Level H QR codes embed JUIT's crest for instant scanning.",
        "Slide 4 on screen: 4 Quadrants: Proof-of-Work Engine, PBKDF2 Salting, Gemini AI, Permanent Crest QR."
    ))
    story.append(Spacer(1, 1.5*mm))

    story.append(speech_card(
        "5", "Live Prototype Demonstration Transition", "Praneeth Sai", "2:45 – 3:15",
        "Rather than presenting theoretical slides, we would like to demonstrate our live, production-ready system right now. We will show you the complete end-to-end lifecycle in three steps: Step 1: The JUIT Registrar issuing a degree with Gemini AI extraction; Step 2: The JUIT Student inspecting their permanent JUIT-crested credential in 3D; Step 3: An employer running an instant public verification and witnessing our live tamper-detection engine in action. Switching now to the live software.",
        "Slide 5 on screen: 3-Step Proof Flow Diagram. Alt-Tab to Satyameva Native App."
    ))

    # Page Break for Phase 2
    story.append(PageBreak())

    # Phase 2: Live Prototype Demo
    story.append(section_hdr("PHASE 2: 4-MINUTE LIVE PROTOTYPE DEMONSTRATION (3:15 – 7:15)"))
    story.append(Spacer(1, 1.5*mm))

    story.append(demo_step_card(
        "1", "Issuer Portal & Google Gemini AI Extraction (3:15 – 4:30)",
        "Log in as issuer / issuer123. Click 'AI Extract & Issue Single Credential'. Upload sample degree PDF. Click 'Anchor Credential to Blockchain'.",
        "We are now logged in as the Registrar. Watch how easy credential issuance becomes. Instead of manual data entry, the registrar uploads a raw degree certificate. Google Gemini 2.0 Flash AI reads the document, automatically extracting student name, roll number, course, and degree title in seconds. When we click Anchor to Blockchain, our Proof-of-Work engine mines a new block, anchors the PBKDF2 hash, and dispatches an automated verification notification directly to the student's email via Gmail SMTP. For mass operations, our Bulk CSV engine supports all-or-nothing atomic batch validation."
    ))
    story.append(Spacer(1, 2*mm))

    story.append(demo_step_card(
        "2", "Student Portal & 3D JUIT Crest QR (4:30 – 5:45)",
        "Log out. Log in as praneethsai050 / student123. Open Degree detail view. Click 'Show Ledger Data' (card flips in 3D). Show permanent JUIT Crest QR code.",
        "Now logging in as a JUIT student. The student has complete self-sovereign ownership. Opening the credential, you see the cryptographic seal stamped on the document. Clicking 'Show Ledger Data' flips the card in 3D, showing the exact block index and proof-of-work hash. Notice our permanent institutional QR code. It embeds the official JUIT Waknaghat crest in the center using Error Correction Level H. Unlike temporary links, this QR code never expires. The student can also download an official verification-grade Stamped PDF certificate for global applications."
    ))
    story.append(Spacer(1, 2*mm))

    story.append(demo_step_card(
        "3", "Public Verification & Anti-Tamper Check (5:45 – 7:15)",
        "Copy hash. Open Incognito browser tab at /verify. Paste hash -> Click Verify (Show Green VALID). Deliberately modify 1 character in hash -> Click Verify (Show Red TAMPERED).",
        "Now imagine an employer at Google or Microsoft verifying this candidate. They open our public verification portal without logging in. Pasting the hash gives an authenticated verdict in under two seconds: Status VALID, issuing university JUIT Waknaghat, with complete blockchain block provenance. And here is our mathematical proof: if an unauthorized person attempts to forge a credential or edit a grade in the database, our re-derivation engine immediately flags it as TAMPERED. There are zero silent passes."
    ))
    story.append(Spacer(1, 3*mm))

    # Phase 3: Return to Slides & The Ask
    story.append(section_hdr("PHASE 3: RETURN TO SLIDES & THE JUIT ASK (7:15 – 8:00)"))
    story.append(Spacer(1, 1.5*mm))

    story.append(speech_card(
        "6", "Business Model, Unit Economics & NEP 2020", "Shashank Ray", "7:15 – 7:40",
        "Switching back to our financials: Satyameva operates as a Hybrid B2B SaaS: 1. Universities pay an annual licensing subscription (₹1.5 Lakhs/year/campus) for unlimited AI issuance, student wallet hosting, and institutional brand protection. 2. Corporate recruiters and background verification firms pay a micro-fee of ₹25 per automated verification API call — saving them over 95% compared to manual checks. Because our in-house ledger cost is virtually ₹0.00, our gross margins exceed 92%. Furthermore, our platform directly advances the National Education Policy 2020 and complements DigiLocker by serving as an unforgeable cryptographic validation engine.",
        "Slide 6 on screen: 4 Metrics (₹1.5L SaaS, ₹25/Check, 92%+ Margin, 40M+ Students) & NEP 2020."
    ))
    story.append(Spacer(1, 1.5*mm))

    story.append(speech_card(
        "7", "In-House JUIT Pilot Proposal & The Ask", "Shashank Ray", "7:40 – 8:00",
        "Hon'ble Vice Chancellor Sir and Faculty Members, we bring a concrete proposal for JUIT Waknaghat today: 1. In-House JUIT Pilot: We propose deploying Satyameva Aegis as a zero-risk parallel pilot for JUIT's graduating batch of 2026. This will make JUIT Waknaghat the FIRST university in Himachal Pradesh to issue 100% blockchain-verified academic degrees. 2. RIDE Incubation: We seek incubation support under RIDE JUIT to file our provisional patent for multi-campus dynamic salting and expand across the Jaypee consortium. 3. Our Ask: We request your selection of Team CYPHER X to represent JUIT Waknaghat at the Grand Finale at JIIT Noida, competing for the ₹1 Crore funding pool. With your mentorship and institutional backing, we will establish JUIT at the absolute forefront of national blockchain innovation. Thank you, Sir! We are ready for your questions.",
        "Slide 7 on screen: JUIT Pilot Proposal & Our Ask from Hon'ble VC Sir & Faculty."
    ))

    # Page Break for Phase 4
    story.append(PageBreak())

    # Phase 4: Quick Q&A Cheat Sheet
    story.append(section_hdr("PHASE 4: RAPID-FIRE FACULTY Q&A CHEAT SHEET (8:00 – 10:00)"))
    story.append(Spacer(1, 1.5*mm))

    qa_quick_data = [
        [
            Paragraph("<b>Q1: Blockchain vs DB Cost?</b>", body_bold),
            Paragraph("<b>Praneeth:</b> \"In-house consortium PoW blockchain has <b>₹0.00 gas fees</b>. Standard DBs allow silent insider tampering (<font name='Courier'>UPDATE degrees</font>). Satyameva pairs SQLite for 10ms queries with blockchain for 100% immutability at &lt; ₹0.50/credential.\"", body_s)
        ],
        [
            Paragraph("<b>Q2: DigiLocker Alternative?</b>", body_bold),
            Paragraph("<b>Shashank:</b> \"DigiLocker requires candidate Aadhaar OTP—foreign recruiters (US/EU) cannot verify resumes without Indian SIM. Satyameva offers &lt; 2s instant verification and pipes verified degrees into DigiLocker via NAD API.\"", body_s)
        ],
        [
            Paragraph("<b>Q3: Total Operational Cost?</b>", body_bold),
            Paragraph("<b>Praneeth:</b> \"Gemini 2.0 Flash is $0.10/1M tokens (~1.2 paise/cert). PoW mining is 0.3s CPU compute. Storage on Cloudflare R2 is ₹0. For JUIT's 1,200 batch, <b>total cost is under ₹60</b>!\"", body_s)
        ],
        [
            Paragraph("<b>Q4: What if Key is Stolen?</b>", body_bold),
            Paragraph("<b>Praneeth:</b> \"Multi-Signature Quorum (2-of-3: Dean + Registrar + COE) and Shamir's Secret Sharing. Zero individual can unilaterally mine an unauthorized degree block.\"", body_s)
        ],
        [
            Paragraph("<b>Q5: Degree Revocation?</b>", body_bold),
            Paragraph("<b>Praneeth:</b> \"On-chain Cryptographic Revocation Registry. Blocks are never deleted (preserving audit trail), but verification immediately displays 'DEGREE REVOKED ON [DATE]' with official reason.\"", body_s)
        ],
        [
            Paragraph("<b>Q6: DPDP Act & Privacy?</b>", body_bold),
            Paragraph("<b>Shashank:</b> \"Zero PII stored on-chain in plaintext. Only one-way irreversible cryptographic hashes reside on the blockchain. Fully compliant with DPDP Act 2023 and GDPR.\"", body_s)
        ]
    ]

    t_qa = Table(qa_quick_data, colWidths=[48*mm, 134*mm])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LIGHT_CYAN),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_qa)
    story.append(Spacer(1, 3*mm))

    # Pre-Pitch Checklist box
    chk_p = Paragraph(
        "<b>✅ FINAL PRE-PITCH CHECKLIST BEFORE ENTERING BOARD ROOM:</b><br/>"
        "• <b>Uniform:</b> Both in official Jaypee University Uniform.<br/>"
        "• <b>Laptop Display:</b> Connect to Board Room HDMI (1920×1080, 16:9).<br/>"
        "• <b>Browser Tabs:</b> Tab 1: Satyameva Native App (`http://127.0.0.1:5000`); Tab 2: Incognito (`/verify`).<br/>"
        "• <b>Time Discipline:</b> Strictly finish slides by 4:00, demo by 7:30, Ask by 8:00. Leave full 2 minutes for VC Q&A.",
        ParagraphStyle("ChkP", fontName="Helvetica", fontSize=8, leading=11.5, textColor=DARK_NAVY)
    )
    t_chk = Table([[chk_p]], colWidths=[182*mm])
    t_chk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GOLD),
        ('BOX', (0,0), (-1,-1), 1, GOLD),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_chk)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generated PDF: {out_path}")

    # Sync
    destinations = [
        "C:/Users/hp/Desktop/JUIT_VC_PITCH_PLAYBOOK_10MIN.pdf",
        "C:/Users/hp/OneDrive/Desktop/Satyameva/JUIT_VC_PITCH_PLAYBOOK_10MIN.pdf",
        "C:/Users/hp/OneDrive/Documents/GitHub/satyameva/JUIT_VC_PITCH_PLAYBOOK_10MIN.pdf"
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
