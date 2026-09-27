"""
SIH 2025 Idea Template PDF Generator
Generates a professional hackathon idea document for the SIH submission portal.
"""

import os
import sys

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import PageTemplate, Frame
    from reportlab.platypus.doctemplate import BaseDocTemplate
except ImportError:
    print("ERROR: reportlab not installed. Run: pip install reportlab")
    sys.exit(1)

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "SIH_2025_Satyameva_Aegis_Idea_Template.pdf")

# ── Color Palette ──────────────────────────────────────────────────────────────
NAVY        = colors.HexColor("#0b102b")
CYAN        = colors.HexColor("#06b6d4")
GOLD        = colors.HexColor("#d4af37")
WHITE       = colors.white
LIGHT_CYAN  = colors.HexColor("#e0f7fa")
LIGHT_NAVY  = colors.HexColor("#e8eaf6")
GRAY        = colors.HexColor("#555555")
LIGHT_GRAY  = colors.HexColor("#f5f5f5")
DARK_GRAY   = colors.HexColor("#333333")

def build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=WHITE,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle",
        fontName="Helvetica",
        fontSize=13,
        textColor=LIGHT_CYAN,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    styles["cover_meta"] = ParagraphStyle(
        "cover_meta",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=GOLD,
        leading=14,
        alignment=TA_CENTER,
    )
    styles["section_header"] = ParagraphStyle(
        "section_header",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=WHITE,
        leading=16,
        leftIndent=4,
        spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK_GRAY,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=4,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK_GRAY,
        leading=14,
        leftIndent=12,
        bulletIndent=2,
        spaceAfter=2,
    )
    styles["label"] = ParagraphStyle(
        "label",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=NAVY,
        leading=13,
        spaceAfter=2,
    )
    styles["value"] = ParagraphStyle(
        "value",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK_GRAY,
        leading=13,
        spaceAfter=6,
    )
    styles["table_header"] = ParagraphStyle(
        "table_header",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=WHITE,
        leading=12,
        alignment=TA_CENTER,
    )
    styles["table_cell"] = ParagraphStyle(
        "table_cell",
        fontName="Helvetica",
        fontSize=9,
        textColor=DARK_GRAY,
        leading=12,
    )
    styles["tag"] = ParagraphStyle(
        "tag",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=NAVY,
        leading=12,
    )

    return styles


def section_block(title, content_flowables, styles):
    """Returns a KeepTogether block with a navy header bar and content."""
    header_table = Table(
        [[Paragraph(f"◆  {title}", styles["section_header"])]],
        colWidths=[170*mm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    items = [header_table, Spacer(1, 6)]
    items.extend(content_flowables)
    items.append(Spacer(1, 10))
    return KeepTogether(items)


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
        title="Satyameva Aegis — SIH 2025 Idea Template",
        author="Team Satyameva",
        subject="Blockchain-Based Secure Platform for Identity, Access Control, and Digital Asset Management",
        creator="Satyameva Aegis Generator",
    )

    styles = build_styles()
    story = []

    # ── COVER BANNER ──────────────────────────────────────────────────────────
    cover_data = [[
        Paragraph("SATYAMEVA AEGIS", styles["cover_title"]),
    ]]
    cover = Table(cover_data, colWidths=[170*mm])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(cover)

    sub_data = [[
        Paragraph("Blockchain-Based Secure Platform for Identity, Access Control,<br/>and Digital Asset Management", styles["cover_subtitle"]),
    ]]
    sub_cover = Table(sub_data, colWidths=[170*mm])
    sub_cover.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(sub_cover)

    gold_bar = Table([[""]], colWidths=[170*mm], rowHeights=[4])
    gold_bar.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), GOLD)]))
    story.append(gold_bar)

    meta_data = [[
        Paragraph("Smart India Hackathon 2025  ·  Ministry of Education's Innovation Cell  ·  Technology Bucket: Blockchain &amp; Cybersecurity", styles["cover_meta"]),
    ]]
    meta_cover = Table(meta_data, colWidths=[170*mm])
    meta_cover.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(meta_cover)
    story.append(Spacer(1, 16))

    # ── 1. IDEA OVERVIEW ──────────────────────────────────────────────────────
    overview_items = [
        Paragraph(
            "Satyameva Aegis is a production-ready, full-stack blockchain credential verification platform built to "
            "eliminate academic document fraud and enable instant digital identity verification across Indian universities. "
            "The platform combines a proof-of-work blockchain ledger, AI-assisted document data extraction (Google Gemini), "
            "cryptographic PBKDF2-HMAC-SHA256 hashing, institutional QR code branding, and a multi-role web portal "
            "(Student · Issuer · Verifier · Admin) — all backed by a scalable Flask + SQLAlchemy backend.",
            styles["body"]
        ),
        Spacer(1, 4),
        Paragraph(
            "Developed as a live prototype for the Jaypee Group of Institutions (JIIT Noida · JUIT Waknaghat · JUET Guna), "
            "the system is immediately deployable and has passed a comprehensive 11-suite E2E automated test battery and "
            "full-coverage smoke tests across all routes and credential states.",
            styles["body"]
        ),
    ]
    story.append(section_block("1. Idea Overview", overview_items, styles))

    # ── 2. PROBLEM STATEMENT ──────────────────────────────────────────────────
    problem_items = [
        Paragraph(
            "<b>The Core Challenge:</b> India produces over 38 million students annually. Academic document fraud — "
            "forged marksheets, fake degrees, and tampered certificates — costs employers, institutions, and the government "
            "billions in verification overhead and fraudulent hires. Traditional paper-based credentials are trivially "
            "forged, and existing digital verification portals are institution-siloed, slow, and unauthenticated.",
            styles["body"]
        ),
        Spacer(1, 4),
        Paragraph("<b>Specific gaps this platform addresses:</b>", styles["label"]),
        Paragraph("• No tamper-proof, immutable record trail for issued academic documents.", styles["bullet"]),
        Paragraph("• Verification requires manual email/call to the issuing registrar — taking days.", styles["bullet"]),
        Paragraph("• No real-time public credential verification link usable by employers in under 5 seconds.", styles["bullet"]),
        Paragraph("• No multi-campus institutional QR code standard with cryptographic anchoring.", styles["bullet"]),
        Paragraph("• No AI-assisted batch issuance pipeline for registrar offices handling thousands of credentials.", styles["bullet"]),
    ]
    story.append(section_block("2. Problem Statement", problem_items, styles))

    # ── 3. PROPOSED SOLUTION ─────────────────────────────────────────────────
    solution_items = [
        Paragraph(
            "Satyameva Aegis solves this with a tri-layer architecture:",
            styles["body"]
        ),
        Spacer(1, 4),
    ]

    tech_data = [
        [
            Paragraph("Layer", styles["table_header"]),
            Paragraph("Component", styles["table_header"]),
            Paragraph("Technology", styles["table_header"]),
            Paragraph("Function", styles["table_header"]),
        ],
        [
            Paragraph("1 — Trust", styles["table_cell"]),
            Paragraph("Blockchain Ledger", styles["table_cell"]),
            Paragraph("Proof-of-Work (SHA-256, Difficulty 4)", styles["table_cell"]),
            Paragraph("Immutable credential anchoring — any tampering breaks the chain.", styles["table_cell"]),
        ],
        [
            Paragraph("2 — Identity", styles["table_cell"]),
            Paragraph("Cryptographic Hashing", styles["table_cell"]),
            Paragraph("PBKDF2-HMAC-SHA256, 100,000 iter.", styles["table_cell"]),
            Paragraph("Per-doc salted hash; re-derived on every verify — no silent pass for edited rows.", styles["table_cell"]),
        ],
        [
            Paragraph("3 — Access", styles["table_cell"]),
            Paragraph("Role-Based Access Control", styles["table_cell"]),
            Paragraph("Flask Blueprints + JWT-like session", styles["table_cell"]),
            Paragraph("Student / Issuer / Verifier / Admin isolation with ownership checks.", styles["table_cell"]),
        ],
        [
            Paragraph("4 — Intelligence", styles["table_cell"]),
            Paragraph("AI Extraction", styles["table_cell"]),
            Paragraph("Google Gemini 2.0 Flash", styles["table_cell"]),
            Paragraph("Auto-extracts credential metadata from uploaded PDFs/images for bulk issuance.", styles["table_cell"]),
        ],
        [
            Paragraph("5 — Verification", styles["table_cell"]),
            Paragraph("QR + Public Link", styles["table_cell"]),
            Paragraph("HMAC-signed URL + Error-Correction H QR", styles["table_cell"]),
            Paragraph("Permanent, campus-branded verification QR — lifetime valid, cryptographically anchored.", styles["table_cell"]),
        ],
    ]

    tech_table = Table(tech_data, colWidths=[22*mm, 30*mm, 45*mm, 67*mm])
    tech_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT_GRAY, WHITE]),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    solution_items.append(tech_table)
    story.append(section_block("3. Proposed Solution", solution_items, styles))

    # ── 4. KEY FEATURES ───────────────────────────────────────────────────────
    features_items = [
        Paragraph("🔐 <b>Blockchain Credential Anchoring</b> — Every issued credential is hashed and mined into a proof-of-work chain. Employers get a 6-verdict answer (VALID / EXPIRED / REVOKED / TAMPERED / NOT_FOUND / QR_EXPIRED) in under 2 seconds.", styles["bullet"]),
        Paragraph("🤖 <b>Gemini AI Auto-Extraction</b> — Upload a PDF/image; Gemini extracts structured credential data automatically, eliminating manual entry for bulk issuance.", styles["bullet"]),
        Paragraph("📦 <b>Bulk CSV Issuance</b> — All-or-nothing atomic batch validator: register thousands of credentials from a spreadsheet. Any single row error aborts the entire batch — 0 partial writes.", styles["bullet"]),
        Paragraph("🎓 <b>Multi-Campus Institutional QR</b> — Campus-specific QR codes embed JIIT / JUIT / JUET crests with Error Correction Level H. Permanent, lifetime-valid verification links with no expiration.", styles["bullet"]),
        Paragraph("📧 <b>Automated Email Notifications</b> — Students receive instant Gmail SMTP notifications on issuance and verification results (hackathonsage@gmail.com).", styles["bullet"]),
        Paragraph("🛡️ <b>Stamped PDF Certificates</b> — Download verification-grade stamped PDFs with embedded QR, blockchain metadata, and institutional branding.", styles["bullet"]),
        Paragraph("📊 <b>Admin Control Center</b> — Master admin manages all institutions, users, documents, and the live blockchain ledger from a dedicated admin portal.", styles["bullet"]),
        Paragraph("🖥️ <b>Native Desktop App Mode</b> — Silent VBScript launcher opens the platform in frameless Chrome/Edge app window with a custom Cyber Shield desktop icon.", styles["bullet"]),
    ]
    story.append(section_block("4. Key Features", features_items, styles))

    # ── 5. TECH STACK ─────────────────────────────────────────────────────────
    stack_items = []

    stack_data = [
        [Paragraph("Component", styles["table_header"]), Paragraph("Technology", styles["table_header"]), Paragraph("Purpose", styles["table_header"])],
        [Paragraph("Backend", styles["table_cell"]), Paragraph("Python 3.14 + Flask 3.0", styles["table_cell"]), Paragraph("Web framework, blueprint routing, session management", styles["table_cell"])],
        [Paragraph("Database", styles["table_cell"]), Paragraph("SQLite + Flask-SQLAlchemy", styles["table_cell"]), Paragraph("Credential, block, user, verification log storage", styles["table_cell"])],
        [Paragraph("Blockchain", styles["table_cell"]), Paragraph("Custom PoW (SHA-256)", styles["table_cell"]), Paragraph("Immutable tamper-proof credential ledger (blockchain.py)", styles["table_cell"])],
        [Paragraph("Cryptography", styles["table_cell"]), Paragraph("PBKDF2-HMAC-SHA256", styles["table_cell"]), Paragraph("Per-document salted hashing (security.py)", styles["table_cell"])],
        [Paragraph("AI Engine", styles["table_cell"]), Paragraph("Google Gemini 2.0 Flash", styles["table_cell"]), Paragraph("Document data extraction from PDF/image uploads", styles["table_cell"])],
        [Paragraph("Auth", styles["table_cell"]), Paragraph("Flask-Login + Google OAuth 2.0", styles["table_cell"]), Paragraph("Role-based access control, institutional login", styles["table_cell"])],
        [Paragraph("QR Engine", styles["table_cell"]), Paragraph("qrcode + Pillow (ECL-H)", styles["table_cell"]), Paragraph("Branded QR generation with institutional crests", styles["table_cell"])],
        [Paragraph("Email", styles["table_cell"]), Paragraph("Flask-Mail + Gmail SMTP", styles["table_cell"]), Paragraph("Real-time credential and verification notifications", styles["table_cell"])],
        [Paragraph("Frontend", styles["table_cell"]), Paragraph("HTML5 + CSS3 + Three.js (WebGL)", styles["table_cell"]), Paragraph("3D blockchain hero, holographic UI, radar HUD animations", styles["table_cell"])],
        [Paragraph("Containerization", styles["table_cell"]), Paragraph("Docker + docker-compose", styles["table_cell"]), Paragraph("Production deployment configuration", styles["table_cell"])],
    ]
    stack_table = Table(stack_data, colWidths=[30*mm, 52*mm, 82*mm])
    stack_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT_GRAY, WHITE]),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    stack_items.append(stack_table)
    story.append(section_block("5. Technology Stack", stack_items, styles))

    # ── 6. ARCHITECTURE DIAGRAM (text-based) ─────────────────────────────────
    arch_items = [
        Paragraph(
            "The platform follows a 5-layer security architecture:",
            styles["body"]
        ),
        Spacer(1, 4),
    ]

    arch_data = [
        [Paragraph("Layer 5 — Presentation", styles["table_header"]), Paragraph("Holographic 3D Web UI (Three.js WebGL + CSS3 Animations)", styles["table_cell"])],
        [Paragraph("Layer 4 — Application", styles["table_header"]), Paragraph("Flask Blueprints: auth · student · issuer · verifier · admin · public", styles["table_cell"])],
        [Paragraph("Layer 3 — Intelligence", styles["table_header"]), Paragraph("Gemini AI Extraction  ·  QR Code Engine  ·  Email Notification Service", styles["table_cell"])],
        [Paragraph("Layer 2 — Cryptographic", styles["table_header"]), Paragraph("PBKDF2-HMAC-SHA256 Hashing  ·  Per-Document Salting  ·  HMAC-Signed QR Tokens", styles["table_cell"])],
        [Paragraph("Layer 1 — Blockchain", styles["table_header"]), Paragraph("Proof-of-Work Ledger (Difficulty 4)  ·  Dual-Persisted (SQLite + blockchain.json)", styles["table_cell"])],
    ]

    colors_list = [NAVY, colors.HexColor("#0d1a4a"), colors.HexColor("#1a2e6b"), colors.HexColor("#0a3d62"), colors.HexColor("#006064")]
    arch_table = Table(arch_data, colWidths=[42*mm, 122*mm])
    arch_style = [
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#aaaaaa")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TEXTCOLOR", (0,0), (0,-1), WHITE),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (0,-1), 9),
    ]
    for i, c in enumerate(colors_list):
        arch_style.append(("BACKGROUND", (0,i), (0,i), c))
    arch_table.setStyle(TableStyle(arch_style))
    arch_items.append(arch_table)
    story.append(section_block("6. Architecture Overview", arch_items, styles))

    # ── 7. SCALABILITY & IMPACT ───────────────────────────────────────────────
    impact_items = [
        Paragraph("<b>Phase 1 (Current Prototype):</b> Deployed for Jaypee Group of Institutions — JIIT (Noida), JUIT (Waknaghat), JUET (Guna). Live Gmail SMTP, Gemini AI, Google OAuth, and permanent QR verification.", styles["body"]),
        Spacer(1, 4),
        Paragraph("<b>Phase 2 (National Scale):</b> Extend to NIT, IIT, and state universities via institution onboarding portal. REST API exposure for government DigiLocker and National Academic Depository (NAD) integration.", styles["body"]),
        Spacer(1, 4),
        Paragraph("<b>Phase 3 (Digital Identity Platform):</b> Expand beyond academic credentials to government identity documents, professional certifications, and digital asset provenance — creating a Universal Indian Digital Trust Ledger.", styles["body"]),
        Spacer(1, 6),
        Paragraph("<b>Estimated Impact:</b>", styles["label"]),
        Paragraph("• Eliminate document fraud for 38M+ Indian students annually.", styles["bullet"]),
        Paragraph("• Reduce employer credential verification time from days → under 5 seconds.", styles["bullet"]),
        Paragraph("• Provide registrar offices AI-assisted bulk issuance for 10,000+ credential batch operations.", styles["bullet"]),
        Paragraph("• Interoperate with DigiLocker / NAD via API bridge for national digital ID ecosystem.", styles["bullet"]),
    ]
    story.append(section_block("7. Scalability & National Impact", impact_items, styles))

    # ── 8. PROTOTYPE STATUS & TESTING ────────────────────────────────────────
    test_items = [
        Paragraph("The prototype is <b>fully functional and production-ready</b> as of SIH 2025 submission date.", styles["body"]),
        Spacer(1, 4),
    ]

    test_data = [
        [Paragraph("Test Suite", styles["table_header"]), Paragraph("Coverage", styles["table_header"]), Paragraph("Result", styles["table_header"])],
        [Paragraph("_smoke.py — Route Smoke Test", styles["table_cell"]), Paragraph("All routes: login, dashboard, credential detail, QR, download, public verify", styles["table_cell"]), Paragraph("✅ ALL PASS", styles["table_cell"])],
        [Paragraph("test_e2e.py — E2E Integration", styles["table_cell"]), Paragraph("11 full integration suites across all user roles and credential states", styles["table_cell"]), Paragraph("✅ 11/11 PASS (100%)", styles["table_cell"])],
        [Paragraph("_assert.py — Behavioral Test", styles["table_cell"]), Paragraph("6-verdict logic, QR freshness/staleness, RBAC blocking, idle timeout", styles["table_cell"]), Paragraph("✅ ALL PASS", styles["table_cell"])],
        [Paragraph("test_bulk_issue_e2e.py", styles["table_cell"]), Paragraph("4-tier bulk issuance: CSV parsing, atomic all-or-nothing validation, batch mining", styles["table_cell"]), Paragraph("✅ ALL PASS", styles["table_cell"])],
    ]

    test_table = Table(test_data, colWidths=[45*mm, 85*mm, 34*mm])
    test_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT_GRAY, WHITE]),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TEXTCOLOR", (-1,1), (-1,-1), colors.HexColor("#1a7a1a")),
        ("FONTNAME", (-1,1), (-1,-1), "Helvetica-Bold"),
    ]))
    test_items.append(test_table)
    story.append(section_block("8. Prototype Status & Testing", test_items, styles))

    # ── 9. LIVE DEMO ──────────────────────────────────────────────────────────
    demo_items = [
        Paragraph("<b>Live Prototype Demo:</b> http://127.0.0.1:5000 (Local deployment — run <font face='Courier'>python run.py</font> from project root)", styles["body"]),
        Spacer(1, 4),
        Paragraph("<b>Walkthrough Demo Sequence (5 minutes):</b>", styles["label"]),
        Paragraph("1. Sign in as a student — see the live 3D blockchain rendered in WebGL on the dashboard.", styles["bullet"]),
        Paragraph("2. Open a credential — view the cryptographic seal pressed onto the certificate, flip to see live blockchain ledger data.", styles["bullet"]),
        Paragraph("3. Scan the permanent QR code — verify the credential on a public link in under 2 seconds.", styles["bullet"]),
        Paragraph("4. Open the Issuer portal — use Gemini AI extraction to auto-fill a credential from a PDF upload, then bulk-issue via CSV.", styles["bullet"]),
        Paragraph("5. Check the Admin panel — view all institutions, users, documents, and the live blockchain block explorer.", styles["bullet"]),
    ]
    story.append(section_block("9. Live Demo & Access", demo_items, styles))

    # ── FOOTER BAR ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 6))
    footer_data = [[
        Paragraph(
            "Satyameva Aegis  ·  Smart India Hackathon 2025  ·  Blockchain &amp; Cybersecurity  "
            "·  JIIT Noida  ·  Team Satyameva",
            ParagraphStyle("footer", fontName="Helvetica", fontSize=8, textColor=WHITE,
                           alignment=TA_CENTER, leading=12)
        )
    ]]
    footer = Table(footer_data, colWidths=[170*mm])
    footer.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(footer)

    # ── BUILD ─────────────────────────────────────────────────────────────────
    doc.build(story)
    print(f"[OK] PDF generated successfully: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    build_pdf()
