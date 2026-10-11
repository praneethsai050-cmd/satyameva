"""
JUIT RIDEHACK'26 - Vice Chancellor Board Room Pitch Deck Generator
Creates a 7-slide, 16:9 widescreen presentation deck specifically tailored for:
Vice Chancellor Sir & Senior Faculty Members at JUIT Waknaghat.
"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_vc_deck():
    prs = pptx.Presentation()
    # 16:9 Widescreen standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Executive Academic Palette (JUIT Navy, Gold, Cyan, Emerald)
    C_BG = RGBColor(11, 17, 32)           # #0B1120 Deep Midnight Navy
    C_CARD = RGBColor(19, 29, 49)         # #131D31 Card background
    C_CARD_BORDER = RGBColor(30, 58, 95)  # #1E3A5F Card stroke
    C_CYAN = RGBColor(56, 189, 248)       # #38BDF8 Electric Cyan Accent
    C_GOLD = RGBColor(212, 175, 55)       # #D4AF37 JUIT Academic Gold
    C_GREEN = RGBColor(16, 185, 129)      # #10B981 Emerald Green / Success
    C_RED = RGBColor(239, 68, 68)         # #EF4444 Alert / Threat
    C_WHITE = RGBColor(248, 250, 252)     # #F8FAFC Crisp White
    C_MUTED = RGBColor(148, 163, 184)     # #94A3B8 Slate Gray
    C_DARK_CARD = RGBColor(15, 23, 42)    # #0F172A

    def set_bg(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = C_BG

    def add_card(slide, left, top, width, height, bg=C_CARD, border=C_CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg
        shape.line.color.rgb = border
        shape.line.width = Pt(1)
        return shape

    def add_header(slide, title, category="RIDEHACK'26 | JUIT INTERNAL QUALIFIERS", subtext=""):
        # Category Tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_GOLD
        p_cat.font.name = "Arial"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.55))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_WHITE
        p_title.font.name = "Arial"

        # Subtitle
        if subtext:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.24), Inches(11.7), Inches(0.35))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtext
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = C_MUTED
            p_sub.font.name = "Arial"

    # =========================================================================
    # SLIDE 1: COVER & JUIT HOOK
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    # Top Tag
    t_tag = add_card(s1, Inches(0.8), Inches(0.75), Inches(5.8), Inches(0.42), bg=C_DARK_CARD, border=C_GOLD)
    tf_tag = t_tag.text_frame
    tf_tag.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf_tag.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "🏛️ JUIT WAKNAGHAT | IIC RIDEHACK'26 QUALIFIERS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    # Main Project Title
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.5), Inches(1.3))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = "SATYAMEVA AEGIS"
    p_t.font.size = Pt(44)
    p_t.font.bold = True
    p_t.font.color.rgb = C_WHITE

    p_sub = tf_t.add_paragraph()
    p_sub.text = "Decentralized Cryptographic Trust Protocol for Academic Credentials & Digital Identity"
    p_sub.font.size = Pt(18)
    p_sub.font.bold = True
    p_sub.font.color.rgb = C_CYAN

    # Hook Banner Card
    b_card = add_card(s1, Inches(0.8), Inches(2.9), Inches(11.7), Inches(0.9), bg=C_DARK_CARD, border=C_CARD_BORDER)
    tf_b = b_card.text_frame
    tf_b.margin_left = Inches(0.3)
    tf_b.margin_top = Inches(0.18)
    p_b = tf_b.paragraphs[0]
    p_b.text = "“Transforming university certificates into tamper-proof, self-sovereign blockchain assets — verified in under 2 seconds.”"
    p_b.font.size = Pt(13)
    p_b.font.bold = True
    p_b.font.color.rgb = C_WHITE

    p_b2 = tf_b.add_paragraph()
    p_b2.text = "Protecting institutional reputation · Eliminating background verification friction · Zero gas fee architecture"
    p_b2.font.size = Pt(11)
    p_b2.font.color.rgb = C_GOLD

    # Team & Presentation Context Cards
    team_card = add_card(s1, Inches(0.8), Inches(4.1), Inches(5.6), Inches(2.7), bg=C_CARD, border=C_CARD_BORDER)
    tf_team = team_card.text_frame
    tf_team.margin_left = Inches(0.3)
    tf_team.margin_top = Inches(0.25)
    p1 = tf_team.paragraphs[0]
    p1.text = "FOUNDING TEAM — CYPHER X"
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = C_CYAN

    p2 = tf_team.add_paragraph()
    p2.text = "• A Praneeth Sai — Founder & Lead Architect (CSE-CS)"
    p2.font.size = Pt(12)
    p2.font.bold = True
    p2.font.color.rgb = C_WHITE

    p3 = tf_team.add_paragraph()
    p3.text = "   Full-stack system, cryptographic hashing & PoW engine"
    p3.font.size = Pt(10)
    p3.font.color.rgb = C_MUTED

    p4 = tf_team.add_paragraph()
    p4.text = "• Shashank Ray — Co-Founder & Product/Business Lead"
    p4.font.size = Pt(12)
    p4.font.bold = True
    p4.font.color.rgb = C_WHITE

    p5 = tf_team.add_paragraph()
    p5.text = "   Market validation, B2B university SaaS model & GTM"
    p5.font.size = Pt(10)
    p5.font.color.rgb = C_MUTED

    venue_card = add_card(s1, Inches(6.8), Inches(4.1), Inches(5.7), Inches(2.7), bg=C_CARD, border=C_CARD_BORDER)
    tf_venue = venue_card.text_frame
    tf_venue.margin_left = Inches(0.3)
    tf_venue.margin_top = Inches(0.25)
    pv1 = tf_venue.paragraphs[0]
    pv1.text = "PRESENTATION CONTEXT & OBJECTIVE"
    pv1.font.size = Pt(13)
    pv1.font.bold = True
    pv1.font.color.rgb = C_GOLD

    pv2 = tf_venue.add_paragraph()
    pv2.text = "• Round: JUIT Internal Qualifiers before Hon'ble Vice Chancellor & Faculty"
    pv2.font.size = Pt(11)
    pv2.font.color.rgb = C_WHITE

    pv3 = tf_venue.add_paragraph()
    pv3.text = "• Status: Fully operational working prototype (TRL 6) tested on Jaypee nodes"
    pv3.font.size = Pt(11)
    pv3.font.color.rgb = C_WHITE

    pv4 = tf_venue.add_paragraph()
    pv4.text = "• Goal: Incubation under RIDE & Representing JUIT at the JIIT Noida Grand Finale"
    pv4.font.size = Pt(11)
    pv4.font.bold = True
    pv4.font.color.rgb = C_GREEN

    pv5 = tf_venue.add_paragraph()
    pv5.text = "• Funding Pool Target: ₹1 Crore Innovation & Incubation Fund"
    pv5.font.size = Pt(11)
    pv5.font.color.rgb = C_CYAN

    # =========================================================================
    # SLIDE 2: THE PROBLEM - THREAT TO UNIVERSITY BRAND
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "The Crisis in Academic Trust: A Threat to Institutional Value",
               "RIDEHACK'26 | THE PROBLEM",
               "Why traditional physical certificates and static PDFs fail in the modern digital economy")

    # 3 Column Problem Cards
    col_w = Inches(3.7)
    c1 = add_card(s2, Inches(0.8), Inches(1.8), col_w, Inches(5.0), border=C_RED)
    tf1 = c1.text_frame
    tf1.margin_left = tf1.margin_right = Inches(0.25)
    tf1.margin_top = Inches(0.3)
    p = tf1.paragraphs[0]
    p.text = "40,000+ / Year"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = C_RED

    p = tf1.add_paragraph()
    p.text = "Fake Degrees & Forgery Crisis"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tf1.add_paragraph()
    p.text = "\n• Massive proliferation of counterfeit marksheet syndicates across India.\n\n• Forged degrees devalue genuine student hard work and taint institutional reputation.\n\n• Static PDFs and scanned paper certificates offer ZERO tamper protection."
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    c2 = add_card(s2, Inches(4.8), Inches(1.8), col_w, Inches(5.0), border=C_GOLD)
    tf2 = c2.text_frame
    tf2.margin_left = tf2.margin_right = Inches(0.25)
    tf2.margin_top = Inches(0.3)
    p = tf2.paragraphs[0]
    p.text = "2 to 4 Weeks"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    p = tf2.add_paragraph()
    p.text = "Crippling Verification Delay"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tf2.add_paragraph()
    p.text = "\n• Employers & background verification agencies (BGCs) wait up to a month for registrar email replies.\n\n• Verification fees cost companies ₹500 to ₹2,000 per applicant.\n\n• Registrar administrative staff overwhelmed by manual record tracing."
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    c3 = add_card(s2, Inches(8.8), Inches(1.8), col_w, Inches(5.0), border=C_CYAN)
    tf3 = c3.text_frame
    tf3.margin_left = tf3.margin_right = Inches(0.25)
    tf3.margin_top = Inches(0.3)
    p = tf3.paragraphs[0]
    p.text = "Zero Ownership"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    p = tf3.add_paragraph()
    p.text = "Student Vulnerability"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tf3.add_paragraph()
    p.text = "\n• Students face perpetual anxiety over losing original physical documents.\n\n• No secure self-sovereign digital wallet for instant job applications.\n\n• Existing government portals are slow, unauthenticated, or institution-siloed."
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 3: THE SOLUTION - SATYAMEVA AEGIS
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "The Solution: Satyameva Aegis Protocol",
               "RIDEHACK'26 | THE SOLUTION",
               "A 360° trust architecture connecting universities, students, and employers in real-time")

    sol_w = Inches(3.7)
    s_c1 = add_card(s3, Inches(0.8), Inches(1.8), sol_w, Inches(5.0), border=C_GOLD)
    tfs1 = s_c1.text_frame
    tfs1.margin_left = tfs1.margin_right = Inches(0.25)
    tfs1.margin_top = Inches(0.3)
    p = tfs1.paragraphs[0]
    p.text = "🏛️ For Universities"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    p = tfs1.add_paragraph()
    p.text = "Institutional Brand Shield"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tfs1.add_paragraph()
    p.text = "\n• Google Gemini AI Auto-Extraction: Upload PDF/images — AI extracts student details instantly.\n\n• Bulk CSV Issuance: Atomic all-or-nothing batch issuance (0 orphaned blocks).\n\n• Zero Gas Overhead: In-house PoW ledger eliminates costly public crypto gas fees.\n\n• Automated Gmail SMTP: Instant notifications dispatched on issuance & checks."
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    s_c2 = add_card(s3, Inches(4.8), Inches(1.8), sol_w, Inches(5.0), border=C_CYAN)
    tfs2 = s_c2.text_frame
    tfs2.margin_left = tfs2.margin_right = Inches(0.25)
    tfs2.margin_top = Inches(0.3)
    p = tfs2.paragraphs[0]
    p.text = "🎓 For Students"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    p = tfs2.add_paragraph()
    p.text = "Self-Sovereign Digital Asset Wallet"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tfs2.add_paragraph()
    p.text = "\n• Lifetime Credential Ownership: Permanent access to all degrees & marksheets.\n\n• 3D Ledger Inspector: Flip credential card to inspect block index & proof-of-work hash.\n\n• Permanent JUIT Crest QR: Error Correction Level H QR code that never expires.\n\n• Stamped PDF Download: One-click export of official verification certificates."
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    s_c3 = add_card(s3, Inches(8.8), Inches(1.8), sol_w, Inches(5.0), border=C_GREEN)
    tfs3 = s_c3.text_frame
    tfs3.margin_left = tfs3.margin_right = Inches(0.25)
    tfs3.margin_top = Inches(0.3)
    p = tfs3.paragraphs[0]
    p.text = "🏢 For Employers"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    p = tfs3.add_paragraph()
    p.text = "Instant 2-Second Verification"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tfs3.add_paragraph()
    p.text = "\n• Zero Friction: No login or account required for employers at /verify.\n\n• Real-Time Cryptographic Proof: Returns GENUINE verdict with block proof in <2 seconds.\n\n• 100% Tamper Detection: Re-derives hash from scratch — any database edit returns TAMPERED.\n\n• Audit History: Complete timestamped audit trail of all credential checks."
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 4: DEEP-TECH ARCHITECTURE & IP MOAT
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "Deep-Tech Architecture & Cryptographic Moat",
               "RIDEHACK'26 | TECHNOLOGY & INNOVATION",
               "Engineered with military-grade cryptography, proof-of-work consensus, and multimodal AI")

    # 4 Architecture Quadrants
    q_w = Inches(5.7)
    q_h = Inches(2.4)

    # Q1: Blockchain
    q1 = add_card(s4, Inches(0.8), Inches(1.8), q_w, q_h, border=C_CYAN)
    tf_q1 = q1.text_frame
    tf_q1.margin_left = Inches(0.3)
    tf_q1.margin_top = Inches(0.2)
    p = tf_q1.paragraphs[0]
    p.text = "1. Custom Proof-of-Work Blockchain Engine"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p = tf_q1.add_paragraph()
    p.text = "• SHA-256 Difficulty 4 ledger dual-persisted across SQLite and blockchain.json.\n• Zero gas dependency: Eliminates volatile Ethereum/Polygon public transaction fees.\n• 100% auditability: Every block contains parent hash, nonce, timestamp, and payload."
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_WHITE

    # Q2: Cryptography
    q2 = add_card(s4, Inches(6.8), Inches(1.8), q_w, q_h, border=C_GOLD)
    tf_q2 = q2.text_frame
    tf_q2.margin_left = Inches(0.3)
    tf_q2.margin_top = Inches(0.2)
    p = tf_q2.paragraphs[0]
    p.text = "2. Cryptographic Salting & Dynamic Re-Derivation"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p = tf_q2.add_paragraph()
    p.text = "• PBKDF2-HMAC-SHA256 with 100,000 iterations and per-document random salt.\n• Zero Silent Passes: Verification does NOT trust stored hashes — it recomputes from payload.\n• Altering even a single grade or letter triggers immediate TAMPERED verdict."
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_WHITE

    # Q3: Gemini AI
    q3 = add_card(s4, Inches(0.8), Inches(4.4), q_w, q_h, border=C_GREEN)
    tf_q3 = q3.text_frame
    tf_q3.margin_left = Inches(0.3)
    tf_q3.margin_top = Inches(0.2)
    p = tf_q3.paragraphs[0]
    p.text = "3. Google Gemini 2.0 Flash AI Auto-Extraction"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p = tf_q3.add_paragraph()
    p.text = "• Multimodal document intelligence extracts structured fields from raw certificate scans.\n• Auto-populates student name, roll number, course, CGPA, and degree title in seconds.\n• Slashes registrar administrative workload by 90%."
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_WHITE

    # Q4: JUIT Crest QR
    q4 = add_card(s4, Inches(6.8), Inches(4.4), q_w, q_h, border=C_CYAN)
    tf_q4 = q4.text_frame
    tf_q4.margin_left = Inches(0.3)
    tf_q4.margin_top = Inches(0.2)
    p = tf_q4.paragraphs[0]
    p.text = "4. Permanent JUIT Crest QR & Cyber Radar HUD"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p = tf_q4.add_paragraph()
    p.text = "• High-contrast QR with Error Correction Level H (~30%) embedding JUIT campus crest.\n• 360° rotating radar HUD animation for futuristic student experience.\n• Non-expiring lifetime cryptographic anchor linked to immutable ledger."
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 5: LIVE PROTOTYPE DEMO TRANSITION
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "Live Prototype Demonstration: The 3-Step Proof",
               "RIDEHACK'26 | SYSTEM VALIDATION",
               "Seamlessly moving to live software running on our JUIT multi-campus testbed")

    # Banner
    demo_banner = add_card(s5, Inches(0.8), Inches(1.8), Inches(11.7), Inches(0.7), bg=C_DARK_CARD, border=C_GOLD)
    tf_db = demo_banner.text_frame
    tf_db.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf_db.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "⚡ PRODUCTION-READY SYSTEM (TRL 6) · ALL 11 E2E TEST SUITES PASSED (100%) · LIVE AT 127.0.0.1:5000"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    # 3 Demo Flow Steps
    d_step_w = Inches(3.7)
    d1 = add_card(s5, Inches(0.8), Inches(2.7), d_step_w, Inches(4.2), border=C_GOLD)
    tfd1 = d1.text_frame
    tfd1.margin_left = tfd1.margin_right = Inches(0.25)
    tfd1.margin_top = Inches(0.25)
    p = tfd1.paragraphs[0]
    p.text = "STEP 1"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p = tfd1.add_paragraph()
    p.text = "Issuer Portal (Registrar)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p = tfd1.add_paragraph()
    p.text = "\n• Login as JUIT Registrar\n• Upload sample degree PDF\n• Gemini AI extracts details instantly\n• Click 'Anchor to Blockchain'\n• Mines block & triggers live email via Gmail SMTP"
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    d2 = add_card(s5, Inches(4.8), Inches(2.7), d_step_w, Inches(4.2), border=C_CYAN)
    tfd2 = d2.text_frame
    tfd2.margin_left = tfd2.margin_right = Inches(0.25)
    tfd2.margin_top = Inches(0.25)
    p = tfd2.paragraphs[0]
    p.text = "STEP 2"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p = tfd2.add_paragraph()
    p.text = "Student Portal (Praneeth)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p = tfd2.add_paragraph()
    p.text = "\n• Login as JUIT Student\n• View earned credential cards with 3D tilt\n• Flip card to inspect block & hash\n• View Permanent QR with JUIT crest\n• Download official Stamped PDF certificate"
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    d3 = add_card(s5, Inches(8.8), Inches(2.7), d_step_w, Inches(4.2), border=C_GREEN)
    tfd3 = d3.text_frame
    tfd3.margin_left = tfd3.margin_right = Inches(0.25)
    tfd3.margin_top = Inches(0.25)
    p = tfd3.paragraphs[0]
    p.text = "STEP 3"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p = tfd3.add_paragraph()
    p.text = "Public Verifier (/verify)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p = tfd3.add_paragraph()
    p.text = "\n• Open private tab at /verify (No login)\n• Paste hash / scan QR code\n• Instant VALID verdict in <2 seconds\n• Live Anti-Tamper Test: alter 1 character\n• Immediate TAMPERED alert displayed"
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 6: BUSINESS MODEL & NATIONAL IMPACT (NEP 2020)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "Business Model, Unit Economics & National Policy",
               "RIDEHACK'26 | FEASIBILITY & IMPACT",
               "A financially sustainable venture aligned with National Education Policy (NEP 2020)")

    # 4 Metric Cards across Top
    m_w = Inches(2.7)
    m_h = Inches(1.3)
    m_data = [
        ("₹1.5 Lakhs", "Annual SaaS / Campus", C_CYAN),
        ("₹25 / Check", "Corporate API Fee", C_GOLD),
        ("92%+", "Gross Profit Margin", C_GREEN),
        ("40 Million+", "Addressable Students", C_WHITE)
    ]
    for i, (val, lbl, col) in enumerate(m_data):
        mc = add_card(s6, Inches(0.8 + i * 3.0), Inches(1.8), m_w, m_h, border=col)
        tf_m = mc.text_frame
        tf_m.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf_m.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = val
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = col
        p2 = tf_m.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = lbl
        p2.font.size = Pt(10)
        p2.font.color.rgb = C_MUTED

    # 2 Bottom Panels: Commercial & Policy
    pan_w = Inches(5.7)
    pan_h = Inches(3.6)

    # Panel 1: Commercial Model
    p1_card = add_card(s6, Inches(0.8), Inches(3.3), pan_w, pan_h, border=C_CYAN)
    tf_p1 = p1_card.text_frame
    tf_p1.margin_left = Inches(0.3)
    tf_p1.margin_top = Inches(0.25)
    p = tf_p1.paragraphs[0]
    p.text = "Commercial Model & Unit Economics"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p = tf_p1.add_paragraph()
    p.text = "\n• B2B University SaaS: Annual institutional licensing for unlimited issuance, Gemini AI extraction & student wallet hosting.\n\n• Pay-Per-Verify API: ₹25 per check for background verification firms (AuthBridge, FirstAdvantage) & corporate recruiters (saving ₹1,000+ per check).\n\n• Negligible Operational Cost: In-house ledger execution cost is ₹0.00; Polygon L2 bridge is ₹0.08 per credential."
    p.font.size = Pt(11)
    p.font.color.rgb = C_WHITE

    # Panel 2: NEP 2020 & National Alignment
    p2_card = add_card(s6, Inches(6.8), Inches(3.3), pan_w, pan_h, border=C_GOLD)
    tf_p2 = p2_card.text_frame
    tf_p2.margin_left = Inches(0.3)
    tf_p2.margin_top = Inches(0.25)
    p = tf_p2.paragraphs[0]
    p.text = "National Policy & Digital India Alignment"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p = tf_p2.add_paragraph()
    p.text = "\n• NEP 2020 Accordance: Supports National Academic Depository (NAD) and Academic Bank of Credits (ABC) digital portability.\n\n• DigiLocker Complement: Satyameva acts as a cryptographic validation layer, ensuring documents ingested into government depositories cannot be forged.\n\n• 100% Paperless & Sustainable: Eliminates postal courier overhead, physical paper seals, and travel across university campuses."
    p.font.size = Pt(11)
    p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 7: JUIT IN-HOUSE PILOT & ASK FOR JIIT NOIDA
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "In-House JUIT Pilot & Pathway to JIIT Noida Grand Finale",
               "RIDEHACK'26 | THE ROADMAP & THE ASK",
               "Our commitment to establish JUIT as India's premier blockchain-verified academic institution")

    # Left Card: The JUIT Pilot Proposal
    pilot_card = add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), border=C_GOLD)
    tf_pilot = pilot_card.text_frame
    tf_pilot.margin_left = Inches(0.3)
    tf_pilot.margin_top = Inches(0.3)
    p = tf_pilot.paragraphs[0]
    p.text = "THE JUIT IN-HOUSE PILOT PROPOSAL"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    p = tf_pilot.add_paragraph()
    p.text = "Immediate Campus Deployment for 2026 Batch"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tf_pilot.add_paragraph()
    p.text = "\n1. Zero-Risk University Trial:\n   Deploy Satyameva Aegis in parallel with JUIT registrar's existing degree issuance for the graduating batch.\n\n2. First in Himachal Pradesh:\n   Make JUIT Waknaghat the FIRST university in the region to issue 100% blockchain-verified degrees.\n\n3. Jaypee Consortium Expansion:\n   Demonstrate JUIT as the hub, expanding to JIIT Noida and JUET Guna across 15,000+ students.\n\n4. Intellectual Property:\n   File provisional patent for multi-campus dynamic salting & crest-embedded QR technology under JUIT IIC."
    p.font.size = Pt(11)
    p.font.color.rgb = C_MUTED

    # Right Card: The Ask from Vice Chancellor Sir
    ask_card = add_card(s7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), border=C_GREEN)
    tf_ask = ask_card.text_frame
    tf_ask.margin_left = Inches(0.3)
    tf_ask.margin_top = Inches(0.3)
    p = tf_ask.paragraphs[0]
    p.text = "OUR ASK FROM HON'BLE VC SIR & FACULTY"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    p = tf_ask.add_paragraph()
    p.text = "Selection for RIDE Incubation & JIIT Noida Grand Finale"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tf_ask.add_paragraph()
    p.text = "\n1. Selection to Represent JUIT at JIIT Noida:\n   Qualify Team CYPHER X to represent JUIT Waknaghat at the Grand Finale for the ₹1 Crore funding pool.\n\n2. Incubation under RIDE JUIT:\n   Formal pre-incubation mentorship to refine enterprise B2B corporate sales and legal compliance.\n\n3. Administrative Sandbox Approval:\n   Authorization to run a test issuance sandbox with anonymized registrar sample batches.\n\n“With your blessings and guidance, we will establish JUIT at the forefront of national blockchain innovation.”"
    p.font.size = Pt(11)
    p.font.color.rgb = C_WHITE

    # Save PPTX
    out_pptx = os.path.abspath("C:/Users/hp/OneDrive/Desktop/JUIT_RIDEHACK26_VC_Pitch_Deck.pptx")
    prs.save(out_pptx)
    print(f"[OK] Saved PPTX to: {out_pptx}")

    # Copy to project folders
    import shutil
    shutil.copy2(out_pptx, "C:/Users/hp/OneDrive/Desktop/Satyameva/JUIT_RIDEHACK26_VC_Pitch_Deck.pptx")
    shutil.copy2(out_pptx, "C:/Users/hp/OneDrive/Documents/GitHub/satyameva/JUIT_RIDEHACK26_VC_Pitch_Deck.pptx")

    # Export to PDF via PowerPoint COM
    out_pdf = os.path.abspath("C:/Users/hp/OneDrive/Desktop/JUIT_RIDEHACK26_VC_Pitch_Deck.pdf")
    try:
        import win32com.client
        app = win32com.client.Dispatch("PowerPoint.Application")
        pres = app.Presentations.Open(out_pptx, WithWindow=False)
        pres.SaveAs(out_pdf, 32) # 32 = ppSaveAsPDF
        pres.Close()
        app.Quit()
        print(f"[OK] Exported PDF to: {out_pdf}")
        shutil.copy2(out_pdf, "C:/Users/hp/OneDrive/Desktop/Satyameva/JUIT_RIDEHACK26_VC_Pitch_Deck.pdf")
        shutil.copy2(out_pdf, "C:/Users/hp/OneDrive/Documents/GitHub/satyameva/JUIT_RIDEHACK26_VC_Pitch_Deck.pdf")
    except Exception as e:
        print(f"[WARNING] COM PDF conversion error: {e}")

if __name__ == "__main__":
    build_vc_deck()
