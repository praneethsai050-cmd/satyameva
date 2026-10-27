"""
generate_anushka_script_pdf.py — Generates comprehensive speaking script and role guide PDF for Anushka Bansal.
Output: C:\\Users\\hp\\OneDrive\\Desktop\\ANUSHKA_SPEAKING_SCRIPT_AND_ROLE_GUIDE.pdf
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

NAVY       = colors.HexColor("#0B1120")
DARK_NAVY  = colors.HexColor("#070B14")
GOLD       = colors.HexColor("#D4AF37")
CYAN       = colors.HexColor("#06B6D4")
WHITE      = colors.white
LIGHT_GRAY = colors.HexColor("#F8FAFC")
BORDER_COL = colors.HexColor("#CBD5E1")
TEXT_DARK  = colors.HexColor("#0F172A")
MUTED_TEXT = colors.HexColor("#475569")
GREEN      = colors.HexColor("#059669")
EMERALD    = colors.HexColor("#065F46")
PURPLE     = colors.HexColor("#7C3AED")

OUT_PDF = r"C:\Users\hp\OneDrive\Desktop\ANUSHKA_SPEAKING_SCRIPT_AND_ROLE_GUIDE.pdf"

def build_pdf():
    doc = SimpleDocTemplate(
        OUT_PDF,
        pagesize=A4,
        leftMargin=14*mm,
        rightMargin=14*mm,
        topMargin=12*mm,
        bottomMargin=12*mm,
        title="RIDEHACK'26 - Anushka Bansal Speaking Script & Role Guide",
        author="Satyameva Aegis (Team ID: 10)",
    )

    styles = getSampleStyleSheet()

    s_title = ParagraphStyle(
        "BannerTitle",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=WHITE,
        alignment=TA_CENTER
    )
    s_sub = ParagraphStyle(
        "BannerSub",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=GOLD,
        alignment=TA_CENTER
    )
    s_meta = ParagraphStyle(
        "BannerMeta",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=CYAN,
        alignment=TA_CENTER
    )

    s_part_hdr = ParagraphStyle(
        "PartHdr",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=WHITE
    )
    s_cue = ParagraphStyle(
        "CueText",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=GOLD
    )
    s_stage = ParagraphStyle(
        "StageText",
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=CYAN
    )
    s_script = ParagraphStyle(
        "ScriptText",
        fontName="Helvetica",
        fontSize=9.2,
        leading=14,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY
    )
    s_qa_q = ParagraphStyle(
        "QA_Q",
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=13,
        textColor=NAVY
    )
    s_qa_a = ParagraphStyle(
        "QA_A",
        fontName="Helvetica",
        fontSize=8.8,
        leading=12.8,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY
    )
    s_note_title = ParagraphStyle(
        "NoteTitle",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=PURPLE
    )
    s_note_body = ParagraphStyle(
        "NoteBody",
        fontName="Helvetica",
        fontSize=8.8,
        leading=12.8,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY
    )

    story = []

    # --- TOP BANNER ---
    banner_data = [
        [Paragraph("RIDEHACK'26 — JUIT BOARD ROOM PITCH & GRAND FINALE JIIT NOIDA", s_sub)],
        [Paragraph("ANUSHKA BANSAL: COMPLETE SPEAKING SCRIPT & ROLE PLAYBOOK", s_title)],
        [Paragraph("Co-Founder & Data Lead · B.Tech Bioinformatics @ JUIT Waknaghat · Team ID: 10 (Satyameva Aegis)<br/>Focus: Data Integrity Heuristics, Forensic Benchmarks & DigiLocker Differentiation", s_meta)]
    ]
    t_banner = Table(banner_data, colWidths=[182*mm])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMBORDER', (0,-1), (-1,-1), 2.5, GOLD),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 6))

    # --- SECTION 0: ROLE & SPECIALIZATION OVERVIEW ---
    role_box = [
        [Paragraph("<b>ANUSHKA'S PROJECT IDENTITY & SUPERPOWER (WHY BIOINFORMATICS MATTERS HERE)</b>", s_part_hdr)],
        [Paragraph(
            "<b>Your Official Designation:</b> Co-Founder & Data Lead (B.Tech Bioinformatics @ JUIT).<br/>"
            "<b>Your Unique Angle before the Board:</b> In Bioinformatics, genomic and biological datasets demand absolute mathematical perfection — if a single nucleotide base pair mutates, an organism's phenotype alters. You apply that exact <b>forensic rigor</b> to institutional credential data! When faculty see a Bioinformatics student anchoring cryptographic data integrity, they realize this is genuine interdisciplinary deep-tech, not just a standard web app.",
            s_script
        )],
        [Paragraph(
            "<b>Your Core Deliverables:</b><br/>"
            "• <b>Slide 5 Anchor:</b> The 'Why Not DigiLocker?' strategic defense (C2C storage locker vs B2B security engine).<br/>"
            "• <b>Slide 6 Anchor:</b> Mathematical data modeling & 24/24 adversarial attack benchmarks (0.04s detection, 0% false positives).<br/>"
            "• <b>Total Stage Time:</b> Exactly 2.0 to 2.5 minutes (Stopwatch: 3:00 to 5:00 in the 10-minute team relay).",
            s_script
        )]
    ]
    t_role = Table(role_box, colWidths=[182*mm])
    t_role.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), EMERALD),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
    ]))
    story.append(t_role)
    story.append(Spacer(1, 7))

    def make_section(title, cue_text, stage_text, spoken_paragraphs, bg_header=NAVY):
        items = []
        hdr_table = Table([[Paragraph(title, s_part_hdr)]], colWidths=[182*mm])
        hdr_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_header),
            ('TOPPADDING', (0,0), (-1,-1), 4.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        items.append(hdr_table)

        box_rows = []
        if cue_text:
            box_rows.append([Paragraph(f"<b>CUE & TIMING:</b> {cue_text}", s_cue)])
        if stage_text:
            box_rows.append([Paragraph(f"<b>ACTION / STAGE BODY LANGUAGE:</b> {stage_text}", s_stage)])
        
        for p_text in spoken_paragraphs:
            box_rows.append([Paragraph(p_text, s_script)])

        box_table = Table(box_rows, colWidths=[182*mm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 0.8, BORDER_COL),
        ]))
        items.append(box_table)
        items.append(Spacer(1, 7))
        return KeepTogether(items)

    # --- PART 1: THE DIGILOCKER DEFENSE (SLIDE 5) ---
    story.append(make_section(
        "PART 1: THE STRATEGIC QUESTION — 'WHY NOT DIGILOCKER?' (SLIDE 5) — ~1.0 MIN",
        "Praneeth finishes Slide 4: <i>'...aur is data ki forensic integrity aur DigiLocker differentiation ko explain karne ke liye, I invite our Data Lead, Anushka Bansal.'</i> (Stopwatch: 3:00)",
        "Step forward smoothly to the center. Stand straight, smile confidently, and look directly at Hon'ble Vice Chancellor Sir and Dean of Academics. Keep voice clear, articulate, and poised.",
        [
            "“Thank you, Praneeth.",
            "Respected Vice Chancellor Sir, Dean Sir, aur esteemed faculty members — jab bhi hum academic credential verification ki baat karte hain, toh sabse pehla question samne aata hai: <b>'Jab Government of India ka DigiLocker already exist karta hai, toh universities Satyameva kyu purchase karengi?'</b>",
            "Sir, iska difference fundamental hai:<br/>"
            "<b>DigiLocker ek digital almari (citizen storage locker) hai</b>, jahan student apni PDF file store karta hai. Par <b>Satyameva us almari ka biometric tamper-evident lock aur institutional verification engine hai!</b>",
            "Isko 3 key points se samajhte hain:<br/>"
            "<b>1. Foreign Recruiters & Global Friction:</b> DigiLocker me document verify karne ke liye student ka Indian Aadhaar aur active mobile OTP mandatory hota hai. Agar USA, UK ya Germany ka koi employer, foreign university, ya WES credential check karna chahe — toh DigiLocker totally fail ho jata hai kyunki unke paas Indian Aadhaar nahi hota. Satyameva me globally koi bhi verifier bina login kiye sirf 60 seconds me cryptographic verification perform kar sakta hai.<br/>"
            "<b>2. B2B Analytics & Institutional Control:</b> DigiLocker universities ko koi B2B dashboard nahi deta. JUIT ko pata hi nahi chalta ki kisne degree verify ki, kitni baar ki, ya kahan fraud attempt hua. Satyameva registrar office ko real-time fraud telemetry aur governance console deta hai.<br/>"
            "<b>3. Physical Stamped Protection:</b> DigiLocker se PDF download karke print karne par uska sara security khatam ho jata hai. Satyameva ka stamped physical print carrying custom cryptographic seal and dynamic QR — jisko phone camera se scan karke directly blockchain se cross-verify kiya ja sakta hai.<br/>"
            "In short, Sir — <b>Hum DigiLocker ke competitor nahi hain, hum DigiLocker ka security aur verification backbone hain!</b>”"
        ],
        bg_header=NAVY
    ))

    # --- PART 2: DATA INTEGRITY & ADVERSARIAL BENCHMARKS (SLIDE 6) ---
    story.append(make_section(
        "PART 2: DATA INTEGRITY HEURISTICS & 24 ATTACK VECTORS (SLIDE 6) — ~1.0 MIN",
        "Slide 5 transitions to Slide 6: Data Integrity Heuristics & Adversarial Benchmarks. (Stopwatch: 4:00)",
        "Point gracefully to the 3 metric cards on Slide 6 (24/24 Attacks, 0.04s Detection, Forensic Accuracy). Project authority on data science.",
        [
            "“<i>(Looking at Slide 6)</i> Ab aate hain hamare core data engineering par.",
            "As a Bioinformatics researcher at JUIT, hum genomic datasets aur forensic data modeling ke sath deal karte hain jahan <b>zero-tolerance for error</b> hamara benchmark hota hai. Agar DNA sequence me ek single nucleotide base pair mutata ho jaye, toh biological error aa jata hai. Humne wahi forensic mathematical rigor Satyameva ke data layer me implement kiya hai.",
            "Humne system ko laboratory me <b>24 aggressive adversarial attack scenarios</b> par stress-test kiya hai:<br/>"
            "• <b>Chain Gap Attack:</b> Agar database se koi block forcefully delete karne ki koshish kare.<br/>"
            "• <b>Silent Row Tampering:</b> Agar koi internal clerk database me jaakar student ka CGPA 7.0 se badha kar 9.0 kar de.<br/>"
            "• <b>Proof Nonce Mutation:</b> Agar koi mathematical puzzle fake solve kare.<br/>"
            "• <b>Salt Collision Tests:</b> Humne 50 identical metadata credentials generate kiye — PBKDF2 salting ne sabhi 50 ko unique cryptographic hash diya with <b>zero collision!</b>",
            "<b>Result?</b> Satyameva ne har single attack vector ko <b>sirf 0.04 seconds (40 milliseconds)</b> me catch kiya with <b>absolute 0% false positives!</b><br/>"
            "Iska matlab: Asli degree kabhi reject nahi hogi, aur nakli degree 1 second bhi survive nahi kar sakti.<br/><br/>"
            "Ab is pure system ke AI automated OCR pipeline aur B2B SaaS revenue model ko present karenge hamare AI Model Lead, <b>Shashank Ray</b>.”",
            "<i>[ACTION: Step back smoothly with a slight nod. Hand control over to Shashank for Slide 7.]</i>"
        ],
        bg_header=EMERALD
    ))

    # --- PART 3: HARD WORDS SIMPLIFIED (CHEAT SHEET FOR ANUSHKA) ---
    hw_rows = [
        [Paragraph("<b>COMPLEX TECHNICAL TERM</b>", s_part_hdr), Paragraph("<b>AASAN HINGLISH EXPLANATION (Dimaag me bithaane ke liye)</b>", s_part_hdr)],
        [
            Paragraph("<b>Canonical Payload Determinism</b>", s_note_title),
            Paragraph("Agar do computers alag-alag tarike se JSON data likhein (jaise spaces ya order ka farq), toh fingerprint badal sakta hai. Canonical ka matlab: <b>Data ko ek standardized strict order me jamana</b> taaki har machine par exact wahi hash nikle.", s_note_body)
        ],
        [
            Paragraph("<b>False Positive vs False Negative</b>", s_note_title),
            Paragraph("<b>False Positive:</b> Asli student ki degree ko galti se fake bol dena (Ye hamara 0% hai — kabhi nahi hoga).<br/><b>False Negative:</b> Fake degree ko galti se pass kar dena (Ye bhi 0% hai — mathematical lock hai).", s_note_body)
        ],
        [
            Paragraph("<b>Salt Collision Resistance</b>", s_note_title),
            Paragraph("Do students ka naam 'Aarav Sharma', branch 'CSE', marks '85%' exact same ho sakta hai. Agar simple hash karein toh dono ka fingerprint same ho jayega. <b>Salt (secret random characters)</b> milane se identical data ke bawajood dono ka hash totally alag banta hai.", s_note_body)
        ],
        [
            Paragraph("<b>Tamper Triangulation (40ms)</b>", s_note_title),
            Paragraph("Jab verifier scan karta hai, system pure chain ko walk karta hai. Agar ek comma ya grade 'A' ka 'B' hua, toh 40 milliseconds me point out kar deta hai ki <b>'Block #3 tampered, payload signature mismatch'</b>.", s_note_body)
        ]
    ]
    t_hw = Table(hw_rows, colWidths=[60*mm, 122*mm])
    t_hw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PURPLE),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
    ]))
    story.append(KeepTogether([
        Paragraph("<b>MASTER TECHNICAL GLOSSARY: ANUSHKA'S DATA SCIENCE CHEAT SHEET</b>", s_sub),
        Spacer(1, 4),
        t_hw,
        Spacer(1, 7)
    ]))

    # --- PART 4: EMERGENCY FACULTY Q&A CROSS-EXAMINATION DEFENSE ---
    qa_rows = [
        [Paragraph("<b>EMERGENCY CHEAT SHEET FOR ANUSHKA DURING FACULTY Q&A ROUND</b>", s_part_hdr)],
        [
            Paragraph("<b>Q1 (From Vice Chancellor / Dean): 'Government DigiLocker jab sabhi colleges ke liye free hai, toh JUIT Satyameva par paisa kyu kharch kare?'</b>", s_qa_q),
            Paragraph("<b>Your Answer:</b> “Respected Sir, DigiLocker student ke document rakhne ke liye hai, par registrar office ka manual burden DigiLocker khatam nahi karta. Foreign universities, US/UK embassies, aur MNC recruiters DigiLocker se verify nahi kar sakte kyunki wahan Indian Aadhaar OTP lagta hai. Satyameva me foreign employer bina kisi login ya OTP ke 60 seconds me verify kar leta hai. Iske alawa, university registrar office har saal ₹8 se ₹12 Lakhs clerical postal letters me kharch karta hai — Satyameva se wo 100% automate ho jata hai. Hum DigiLocker ko complement karte hain, unka security layer bankar.”", s_qa_a)
        ],
        [
            Paragraph("<b>Q2 (From Biotech / Bioinformatics Faculty): 'Aap Bioinformatics student hain, aapne isme biology ya forensic principles kaise use kiye?'</b>", s_qa_q),
            Paragraph("<b>Your Answer:</b> “Respected Sir/Mam, Bioinformatics me hum FASTA/FASTQ sequence alignment aur genomic mutation tracking karte hain, jahan single base-pair change pure organism ko mutate kar deta hai. Wahi principle humne data verification me use kiya hai: SHA-256 cryptographic hashing acting as the digital DNA of the certificate. Agar document me 1 pixel ya 1 character bhi mutate hua, toh hamara canonical heuristic algorithm usko instantly flag kar deta hai with 0% false positives.”", s_qa_a)
        ],
        [
            Paragraph("<b>Q3 (From CSE Faculty): 'Aapne 24 attack vectors bole — kya SQLite database hack hone par blockchain record safe rahega?'</b>", s_qa_q),
            Paragraph("<b>Your Answer:</b> “Yes Sir, absolutely! Humne Dual-Persistence Parity architecture banaya hai. SQLite sirf fast UI queries ke liye hai. Par actual cryptographic proof immutable `blockchain.json` file aur multi-node consensus ledger me rehta hai. Agar koi SQLite me jaakar manually grade update kar de, toh verification engine dono ka cryptographic hash compare karega. 0.04 seconds me mismatch detect hoga aur screen par red alert 'TAMPERED: Digest Mismatch' trigger ho jayega.”", s_qa_a)
        ],
        [
            Paragraph("<b>Q4 (From Faculty): 'False Positive 0% kaise guarantee kar sakte hain? Kya genuine student ka document kabhi fake bol sakta hai?'</b>", s_qa_q),
            Paragraph("<b>Your Answer:</b> “Sir, cryptographic hashing deterministic mathematics hai, koi probabilistic AI guess nahi hai. SHA-256 algorithm me agar input data exact wahi hai, toh output hash hamesha 100% identical hi aayega. Humne canonical serialization use kiya hai jo spaces aur unicode formatting ko lock karta hai. Isliye genuine document me false positive hone ki mathematical probability zero hai.”", s_qa_a)
        ]
    ]
    t_qa = Table(qa_rows, colWidths=[182*mm])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.6, BORDER_COL),
    ]))
    story.append(KeepTogether([t_qa, Spacer(1, 7)]))

    # --- PART 5: STAGE CUES, BODY LANGUAGE & TIMING HANDBOOK ---
    stage_tips = [
        [Paragraph("<b>ANUSHKA'S STAGE PRESENCE, TIMING & BODY LANGUAGE HANDBOOK</b>", s_part_hdr)],
        [Paragraph(
            "<b>1. Entry / Handoff from Praneeth (at 3:00 min):</b><br/>"
            "Jab Praneeth bole: <i>'...I invite our Data Lead, Anushka Bansal'</i> — ek confident smile ke sath step forward karein. VC sir se eye contact banayein. Don't look at the floor. Speak with a steady, natural tone.<br/><br/>"
            "<b>2. Voice Tone & Modulations:</b><br/>"
            "• Slide 5 (DigiLocker): Respectful, convincing tone. Use your hands to contrast: left hand for 'DigiLocker storage locker' and right hand for 'Satyameva biometric verification lock'.<br/>"
            "• Slide 6 (Data Integrity): Scientific, authoritative tone. Proudly mention your Bioinformatics background at JUIT — it creates an instant positive impression on faculty.<br/><br/>"
            "<b>3. Exit / Handoff to Shashank (at 5:00 min):</b><br/>"
            "Smooth transition: <i>'...Ab is pure system ke AI automation aur B2B revenue model ko present karenge hamare AI Model Lead, Shashank Ray.'</i> Turn slightly towards Shashank with an open palm gesture and step back in line.",
            s_script
        )]
    ]
    t_stage = Table(stage_tips, colWidths=[182*mm])
    t_stage.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GOLD),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
    ]))
    story.append(KeepTogether([t_stage]))

    doc.build(story)
    print(f"[OK] Anushka's Speaking Script PDF created successfully at: {OUT_PDF}")

if __name__ == '__main__':
    build_pdf()
