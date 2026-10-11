"""
Generate high-quality printable PDF for Shashank Ray's Board Room Pitch Script.
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

def build_pdf():
    out_path = "C:/Users/hp/OneDrive/Desktop/SHASHANK_SPEAKING_SCRIPT.pdf"
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=14*mm,
        rightMargin=14*mm,
        topMargin=12*mm,
        bottomMargin=12*mm,
        title="RIDEHACK'26 - Shashank Ray Speaking Script",
        author="Team CYPHER X",
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
        fontSize=11,
        leading=15,
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
        fontSize=9.5,
        leading=14.5,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY
    )
    s_script_bold = ParagraphStyle(
        "ScriptTextBold",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=14.5,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY
    )
    s_qa_q = ParagraphStyle(
        "QA_Q",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=NAVY
    )
    s_qa_a = ParagraphStyle(
        "QA_A",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY
    )

    story = []

    # --- TOP BANNER ---
    banner_data = [
        [Paragraph("RIDEHACK'26 — JUIT BOARD ROOM PITCH (11:00 AM TODAY)", s_sub)],
        [Paragraph("SPEAKING SCRIPT & ACTION CUES: SHASHANK RAY", s_title)],
        [Paragraph("Co-Founder & Product/Business Lead · Team CYPHER X (Satyameva Aegis)<br/>Before: Hon'ble Vice Chancellor Sir & Senior Faculty Members | Board Room, JUIT", s_meta)]
    ]
    t_banner = Table(banner_data, colWidths=[182*mm])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMBORDER', (0,-1), (-1,-1), 2, GOLD),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 6))

    def make_section(title, cue_text, stage_text, spoken_paragraphs):
        items = []
        hdr_table = Table([[Paragraph(title, s_part_hdr)]], colWidths=[182*mm])
        hdr_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), NAVY),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        items.append(hdr_table)

        box_rows = []
        if cue_text:
            box_rows.append([Paragraph(f"<b>CUE:</b> {cue_text}", s_cue)])
        if stage_text:
            box_rows.append([Paragraph(f"<b>ACTION / STAGE:</b> {stage_text}", s_stage)])
        
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

    # --- PART 1 ---
    story.append(make_section(
        "PART 1: THE CRISIS & THE SOLUTION MATRIX (SLIDES 2 & 3) — ~1.5 MINS",
        "Praneeth finishes Slide 1: <i>'...tested live across the Jaypee multi-campus network. Now I invite my co-founder Shashank to address the real-world crisis we are solving.'</i>",
        "Step forward, stand upright, make respectful eye contact with Hon'ble Vice Chancellor Sir and Faculty. Speak at a measured, confident pace.",
        [
            "“Thank you, Praneeth.",
            "Respected Vice Chancellor Sir and faculty members — every year in India, over <b>40,000 counterfeit degrees</b> and forged marksheets are officially detected. But the unmeasured reality is far worse. When fake degrees falsely claiming to be from premier institutions circulate in the market, they inflict direct reputational damage on top universities like JUIT, and they devalue the hard work of every genuine graduate sitting in this room.",
            "Today, when an employer like Google, Infosys, or a foreign embassy verifies a JUIT candidate's background, they face an agonizing turnaround time of <b>two to four weeks</b>. Background verification agencies spend between <b>₹500 to ₹2,000 per applicant</b> on manual registrar follow-ups. Meanwhile, our administrative staff spends valuable hours manually tracing archive registers. Static paper certificates and scanned PDFs offer zero cryptographic protection — they can be forged using Photoshop in ten minutes.",
            "<i>(Click to Slide 3 — The Solution)</i>",
            "Satyameva Aegis solves this by establishing a complete 360-degree digital trust ecosystem:<br/>"
            "<b>1. For JUIT:</b> We provide the Registrar's office with automated Google Gemini AI extraction and bulk issuance, allowing thousands of credentials to be anchored to the blockchain in seconds — with zero gas fees.<br/>"
            "<b>2. For JUIT Students:</b> Every graduate receives a self-sovereign digital wallet. Their credentials carry a permanent JUIT-crested QR code that never expires, along with downloadable verification-grade stamped PDFs.<br/>"
            "<b>3. For Employers:</b> Recruiters need zero accounts. Scanning the JUIT QR code provides mathematical proof of authenticity in under two seconds.<br/>"
            "Now, Praneeth will walk you through our deep-tech architecture and demonstrate the live software.”",
            "<i>[ACTION: Step back smoothly. Hand control over to Praneeth for Slide 4 & The 4-Minute Live Prototype Demo.]</i>"
        ]
    ))

    # --- PART 2 ---
    story.append(make_section(
        "PART 2: BUSINESS MODEL, UNIT ECONOMICS & NEP 2020 (SLIDE 6) — ~1.0 MIN",
        "Praneeth finishes the Live Demo: <i>'...and that proves our 100% cryptographic anti-tamper engine. Now, Shashank will present our business model and national alignment.'</i>",
        "Step forward. Professional, commercial posture.",
        [
            "“Thank you, Praneeth.",
            "Hon'ble Vice Chancellor Sir, Satyameva Aegis is built not just as engineering research, but as a financially self-sustaining venture. We operate on a <b>Hybrid B2B SaaS Model</b>:<br/>"
            "<b>1. Institutional Subscription for Universities:</b> We charge universities an annual licensing fee of approximately <b>₹1.5 Lakhs per campus</b>. This covers unlimited Gemini AI document extraction, bulk issuance pipelines, and student digital wallet hosting.<br/>"
            "<b>2. Corporate Pay-Per-Verify API:</b> Background screening companies like AuthBridge and FirstAdvantage, along with corporate recruiters, currently spend upwards of ₹1,000 per manual verification check. We offer them an automated cryptographic verification API at just <b>₹25 per check</b> — saving them 97% of their costs while generating recurring revenue for our venture.<br/>"
            "Because our in-house Proof-of-Work blockchain runs locally with zero cryptocurrency gas fees, our operational unit cost is negligible — giving us a gross profit margin <b>exceeding 92%</b>.<br/>"
            "Furthermore, Satyameva directly aligns with the <b>National Education Policy (NEP 2020)</b> and the Academic Bank of Credits.<br/>"
            "To address a common question: <b>Satyameva does not compete with the Government's DigiLocker</b>. DigiLocker is a storage locker. Satyameva is the cryptographic issuance protocol that ensures the documents going into DigiLocker can never be forged. We integrate directly with DigiLocker via standard REST APIs.”"
        ]
    ))

    # --- PART 3 ---
    story.append(make_section(
        "PART 3: IN-HOUSE JUIT PILOT & CLOSING ASK TO VC SIR (SLIDE 7) — ~1.0 MIN",
        "Slide 7 is on the screen.",
        "Look directly at the Hon'ble Vice Chancellor Sir. Sincere, inspiring, and respectful tone.",
        [
            "“Hon'ble Vice Chancellor Sir and esteemed faculty members — today, we bring a concrete, zero-risk proposal to this Board Room:<br/>"
            "We propose running an <b>In-House JUIT Pilot</b> for our graduating batch of 2026. By deploying Satyameva Aegis in parallel with existing registrar operations, <b>JUIT Waknaghat will become the FIRST university in Himachal Pradesh</b> to issue 100% blockchain-verified academic degrees. From JUIT as our innovation hub, we can expand across the entire Jaypee Group — encompassing JIIT Noida and JUET Guna across more than 15,000 students.<br/><br/>"
            "<b>Our Ask from You Today:</b><br/>"
            "<b>1. Selection to represent JUIT Waknaghat at the Grand Finale at JIIT Noida</b>, competing for the ₹1 Crore funding pool.<br/>"
            "<b>2. Incubation support under RIDE JUIT</b> to file our provisional patent for multi-campus cryptographic salting and institutional QR technology.<br/>"
            "<b>3. Administrative approval</b> to test a sandbox batch with the Registrar's office.<br/><br/>"
            "Sir, with your mentorship, guidance, and institutional backing, Team CYPHER X will ensure that JUIT stands at the very forefront of national digital trust and blockchain innovation.<br/><br/>"
            "Thank you, Sir! We are now open for your questions.”"
        ]
    ))

    # --- Q&A CHEAT SHEET ---
    qa_items = []
    qa_hdr = Table([[Paragraph("EMERGENCY CHEAT-SHEET FOR SHASHANK DURING FACULTY Q&A", s_part_hdr)]], colWidths=[182*mm])
    qa_hdr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#065F46")), # Emerald Dark
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    qa_items.append(qa_hdr)

    qa_rows = [
        [Paragraph("<b>Q1: Why should a university buy Satyameva when DigiLocker is free?</b>", s_qa_q)],
        [Paragraph("<b>Answer:</b> “Sir, DigiLocker is a cloud locker; it cannot detect origin fraud. If an insider or compromised account uploads a fake degree, DigiLocker still stamps it as authentic. Satyameva provides mathematical proof of issuance at the university origin point, and foreign employers/embassies can verify in 2 seconds without logging into a citizen's DigiLocker.”", s_qa_a)],
        [Paragraph("<b>Q2: What is the cost for JUIT to implement this pilot?</b>", s_qa_q)],
        [Paragraph("<b>Answer:</b> “Sir, for JUIT, the pilot is completely zero-cost. Processing the entire graduating batch of 5,000 students costs under ₹60 in total computing electricity. In fact, it saves the university thousands in physical paper seals and manual administrative hours.”", s_qa_a)],
        [Paragraph("<b>Q3: Who are your target paying customers?</b>", s_qa_q)],
        [Paragraph("<b>Answer:</b> “Sir, our primary customers are private and state universities seeking to protect their brand reputation, followed by corporate HR departments (TCS, Infosys, Wipro) and background verification agencies who want instant, reliable candidate credential checks.”", s_qa_a)]
    ]
    qa_table = Table(qa_rows, colWidths=[182*mm])
    qa_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.8, BORDER_COL),
    ]))
    qa_items.append(qa_table)
    story.append(KeepTogether(qa_items))

    doc.build(story)
    print(f"[OK] Generated PDF: {out_path}")

    # Copy to Local Desktop & Repos
    targets = [
        "C:/Users/hp/Desktop/SHASHANK_SPEAKING_SCRIPT.pdf",
        "C:/Users/hp/OneDrive/Desktop/Satyameva/SHASHANK_SPEAKING_SCRIPT.pdf",
        "C:/Users/hp/OneDrive/Documents/GitHub/satyameva/SHASHANK_SPEAKING_SCRIPT.pdf"
    ]
    for t in targets:
        shutil.copy2(out_path, t)
        print(f"[OK] Copied to: {t}")

if __name__ == "__main__":
    build_pdf()
