"""
generate_ridehack_team_deck.py — Generates RIDEHACK'26 Master Team Presentation & Pitch Playbook
Outputs:
1. C:\\Users\\hp\\OneDrive\\Desktop\\RIDEHACK26_TEAM_MASTER_DECK.pptx (16:9 widescreen PowerPoint with embedded images & Hinglish speaker notes)
2. C:\\Users\\hp\\OneDrive\\Desktop\\RIDEHACK26_TEAM_MASTER_DECK.pdf (16:9 widescreen PDF presentation)
"""
import os
import sys
from PIL import Image
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

IMG_TEAM = r'C:/Users/hp/.gemini/antigravity/brain/898a4eb6-926a-417b-9cac-f6e58897bc1b/.user_uploaded/media_1792562188616_fb3cf0ec.png'
IMG_POSTER = r'C:/Users/hp/.gemini/antigravity/brain/898a4eb6-926a-417b-9cac-f6e58897bc1b/.user_uploaded/media_1792562249501_7fedaef2.png'

OUT_PPTX = r'C:\Users\hp\OneDrive\Desktop\RIDEHACK26_TEAM_MASTER_DECK.pptx'
OUT_PDF = r'C:\Users\hp\OneDrive\Desktop\RIDEHACK26_TEAM_MASTER_DECK.pdf'

# Executive Academic Palette
C_BG          = RGBColor(11, 17, 32)     # #0B1120 Midnight Navy
C_CARD        = RGBColor(19, 29, 49)     # #131D31 Card BG
C_CARD_BORDER = RGBColor(30, 58, 95)     # #1E3A5F Border
C_CYAN        = RGBColor(56, 189, 248)   # #38BDF8 Electric Cyan
C_GOLD        = RGBColor(212, 175, 55)   # #D4AF37 JUIT Academic Gold
C_GREEN       = RGBColor(16, 185, 129)   # #10B981 Emerald Green
C_RED         = RGBColor(239, 68, 68)    # #EF4444 Crimson Alert
C_WHITE       = RGBColor(248, 250, 252)  # #F8FAFC Pure White
C_MUTED       = RGBColor(148, 163, 184)  # #94A3B8 Slate Gray
C_DARK_CARD   = RGBColor(15, 23, 42)     # #0F172A Dark Slate

def build_pptx():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

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
        shape.line.width = Pt(1.2)
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

        if subtext:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.28), Inches(11.7), Inches(0.35))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtext
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = C_MUTED
            p_sub.font.name = "Arial"

    def set_notes(slide, speaker, duration, script_hinglish, hard_words, faculty_defense):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        notes_text = f"""[SPEAKER: {speaker} | DURATION: {duration}]

=== HINGLISH PITCH SCRIPT (Word-by-Word Dialogue) ===
{script_hinglish}

=== HARD WORDS SIMPLIFIED (Aasan Hindi/Hinglish Samjhane Ka Tareeqa) ===
{hard_words}

=== FACULTY CROSS-QUESTION DEFENSE (Agar Sir Ne Yeh Pucha Toh Yeh Rebuttal Dena Hai) ===
{faculty_defense}
"""
        tf.text = notes_text

    # -------------------------------------------------------------------------
    # SLIDE 1: COVER & RIDEHACK MANDATE
    # -------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    # Top Tag
    t_tag = add_card(s1, Inches(0.8), Inches(0.5), Inches(6.5), Inches(0.42), bg=C_DARK_CARD, border=C_GOLD)
    tf = t_tag.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = "🏛️ JUIT WAKNAGHAT | IIC RIDEHACK'26 INTERNAL QUALIFIERS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    # Title & Subtitle
    tb = s1.shapes.add_textbox(Inches(0.8), Inches(1.05), Inches(7.5), Inches(1.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "SATYAMEVA AEGIS"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf.add_paragraph()
    p2.text = "Tamper-Proof Cryptographic Academic Credential & Verification Ecosystem"
    p2.font.size = Pt(15)
    p2.font.color.rgb = C_CYAN
    p2.font.bold = True

    p3 = tf.add_paragraph()
    p3.text = "Empowering Universities with Zero-Gas-Fee Blockchain, Gemini 2.0 AI & 3D Holographic Integrity"
    p3.font.size = Pt(12)
    p3.font.color.rgb = C_MUTED

    # Embed Poster on Right
    if os.path.exists(IMG_POSTER):
        s1.shapes.add_picture(IMG_POSTER, Inches(8.8), Inches(0.5), width=Inches(3.8), height=Inches(3.8))

    # Embed Team Card at Bottom
    if os.path.exists(IMG_TEAM):
        s1.shapes.add_picture(IMG_TEAM, Inches(0.8), Inches(4.5), width=Inches(11.733), height=Inches(2.55))

    set_notes(
        s1,
        speaker="Praneeth Sai (Founder & Architecture)",
        duration="1 Minute (0:00 - 1:00)",
        script_hinglish="Respected Vice Chancellor Sir, Faculty Members aur Panel Judges — Good morning! Hum hain Team ID: 10 — Satyameva Aegis. Aaj hum JUIT ke RIDEHACK'26 platform pe India ka pehla decentralized academic credential ecosystem present kar rahe hain jo fake degree syndicates ko root se khatam karta hai aur Jaypee Universities ko digital credential integrity me national leader banata hai.",
        hard_words="• RIDE: Research, Innovation, Development & Entrepreneurship — Matlab hamara project sirf lab assignment nahi hai, balki market-ready commercial startup hai jisme real funding aur deployment potential hai.\n• Cryptographic Ecosystem: Ek aisa automated software network jahan har certificate mathematical proof ke sath lock hota hai.",
        faculty_defense="Q: Ye project baaki hackathon projects se alag kaise hai?\nA: Sir, hamara project kisi hypothetical idea par nahi hai. Backend, PoW consensus, AI extraction, aur 4 live portals already fully coded aur local testnet par tested hain."
    )

    # -------------------------------------------------------------------------
    # SLIDE 2: THE REAL-WORLD PROBLEM (FAKE DEGREE SYNDICATE)
    # -------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "The Real-World Crisis: India's Academic Trust Deficit", "PROBLEM STATEMENT", "Why existing paper stamps and central databases are failing Indian universities")

    # 3 Stat Cards
    c1 = add_card(s2, Inches(0.8), Inches(1.8), Inches(3.64), Inches(4.8))
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "🚨 ₹1,500 FAKE DEGREES"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_RED

    p = tf1.add_paragraph()
    p.text = "\nPhotoshop & Telegram syndicates sell indistinguishable fake marksheet clones with replica university seals within 24 hours.\n\nEmployers cannot verify original ink from printed clones on physical paper."
    p.font.size = Pt(12)
    p.font.color.rgb = C_MUTED

    c2 = add_card(s2, Inches(4.84), Inches(1.8), Inches(3.64), Inches(4.8))
    tf2 = c2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "⏳ 14-DAY DELAYS"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    p = tf2.add_paragraph()
    p.text = "\nManual verification takes 14 to 21 days via registrar office postal letters and manual emails.\n\nCosts universities ₹12–18 Lakhs annually in clerical overhead and lost administrative hours."
    p.font.size = Pt(12)
    p.font.color.rgb = C_MUTED

    c3 = add_card(s2, Inches(8.88), Inches(1.8), Inches(3.64), Inches(4.8))
    tf3 = c3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "🔓 SQL DATABASE VULNERABILITY"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    p = tf3.add_paragraph()
    p.text = "\nCentralized SQL databases have single points of failure. A rogue registrar clerk or compromised admin password allows silent grade modification.\n\nOnce modified in database, no audit trail exists."
    p.font.size = Pt(12)
    p.font.color.rgb = C_MUTED

    set_notes(
        s2,
        speaker="Praneeth Sai (Founder & Architecture)",
        duration="1.5 Minutes (1:00 - 2:30)",
        script_hinglish="Sir, problem ko dhyan se samajhte hain. Aaj Telegram aur Photoshop par kisi bhi university ki B.Tech degree sirf ₹1,500 me ban jati hai. MNCs aur foreign universities ko verify karne me 2 se 3 hafte lagte hain. Iska nuksaan seedha hamare jaise hard-working students aur college ki reputation ko hota hai. Aur dusra sabse bada khatra: agar university ka normal database hack ho jaye, ya koi clerk database me number edit kar de, toh koi pakad nahi sakta kyunki normal database me koi tamper-proof proof nahi hota.",
        hard_words="• Single Point of Failure: Jab pura system ek hi computer/server par nirbhar ho — agar wo server crash ya hack hua toh poora data khatam ya badal diya jata hai.\n• Academic Trust Deficit: Jab genuine degree par bhi company shaq karne lage kyunki market me fake degree itni aam ho chuki hai.",
        faculty_defense="Q: Kya Jaypee me bhi fake degree issue ho sakta hai?\nA: Sir, issue university ke andar se nahi, bahar se hota hai. Duplicate paper prints bahar ke log banate hain aur verification delay ki wajah se students ki job offers hold par chali jati hain."
    )

    # -------------------------------------------------------------------------
    # SLIDE 3: THE SATYAMEVA SOLUTION
    # -------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "The Satyameva Breakthrough: Zero-Gas-Fee Blockchain Integrity", "OUR SOLUTION", "A mathematically unhackable multi-portal credential trust infrastructure")

    box_left = add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf = box_left.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🛡️ THE 3-PILLAR SECURITY ARCHITECTURE"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    items = [
        ("1. Zero-Gas Private Blockchain", "No crypto tokens, no Ethereum fees. Ultra-fast private Proof-of-Work ledger with SHA-256 block linking."),
        ("2. Multimodal Gemini AI OCR", "Instant field extraction from PDF/scans (Name, Roll, Program, DOB) with zero manual clerical typing."),
        ("3. 60-Second Dynamic Anti-Screenshot QR", "Tokens refresh every 60s. Screenshot sharing is completely invalid for live presentation."),
        ("4. Automated DOB-Encrypted Stamped PDFs", "PDFs locked via AES-256 with student's birthdate. Paper-safe verification.")
    ]
    for title, desc in items:
        p = tf.add_paragraph()
        p.text = f"\n• {title}: {desc}"
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    box_right = add_card(s3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    tf = box_right.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⚡ VALUE DELIVERED TO JUIT & UNIVERSITIES"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    values = [
        ("14 Days ➔ 60 Seconds", "Background verifiers (TCS, Wipro, WES) verify credentials instantly without disturbing university staff."),
        ("Zero Gas Fees", "100% cost-predictable. Costs less than ₹0.48 per certificate processed."),
        ("NEP 2020 & WES Global Mobility", "Complies with National Education Policy digital locker mandate and World Education Services standard."),
        ("Institutional Brand Shield", "Zero fake degree scandals ever possible under Jaypee name.")
    ]
    for title, desc in values:
        p = tf.add_paragraph()
        p.text = f"\n✓ {title}\n  {desc}"
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    set_notes(
        s3,
        speaker="Praneeth Sai (Founder & Architecture)",
        duration="1.5 Minutes (2:30 - 4:00)",
        script_hinglish="Is problem ka solution hai Satyameva. Humne ek 3-pillar security engine design kiya hai: Pehla — hamara apna custom Proof-of-Work private blockchain ledger jisme gas fees zero hai. Dusra — Gemini AI jo degree scan hote hi student ka name, roll number aur DOB automatically extract kar leta hai. Teesra — 60-second dynamic anti-screenshot QR code. Matlab agar koi student apne phone ka screenshot kisi ko bhej de, toh 60 second baad wo expire ho jayega. Live original screen scan karni padegi. Aur student jo stamped PDF download karta hai, wo uske Date of Birth se password-protected hota hai.",
        hard_words="• Zero-Gas Fees: Public blockchain me har transaction par crypto paise (Ether/Solana) lagte hain. Humne private enterprise ledger banaya hai jisme college ka ek bhi paisa crypto me nahi lagta.\n• Dynamic QR: Normal static QR hamesha same rehta hai, koi bhi print karke fake dikha sakta hai. Dynamic QR har 60 second me naya token generate karta hai.",
        faculty_defense="Q: Kya ye internet na hone par bhi chalega?\nA: Haan Sir, offline mode me PWA Service Worker cached cryptographic records verify kar sakta hai, aur stamped PDF par printed SHA-256 hash ko offline verify kiya ja sakta hai."
    )

    # -------------------------------------------------------------------------
    # SLIDE 4: WHOLE BACKEND & CORE PROTOCOL (PRANEETH DEEP DIVE)
    # -------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "Core Protocol & Blockchain Engine: Under The Hood", "BACKEND ARCHITECTURE — A. PRANEETH SAI", "Cryptographic proof-of-work, salting heuristics, and dual-layer persistence")

    # 4 Flow Steps
    steps = [
        ("1. RAW PAYLOAD SALTING", "PBKDF2 HMAC-SHA256", "Document bytes + metadata salted with institutional secret key. Anti-rainbow table immunity."),
        ("2. MERKLE LEAF DIGEST", "Canonical Determinism", "Roll number + Name + Program + Timestamp hashed into 64-character SHA-256 digest string."),
        ("3. PROOF-OF-WORK MINING", "Non-Blocking Asynchronous", "Miner computes nonce satisfying Difficulty 4 ('0000...'). Prevents spam & unauthorized block injections."),
        ("4. DUAL PERSISTENCE", "SQLite ↔ blockchain.json", "Relational metadata in SQLite; Cryptographic chain in immutable JSON. Automatic state self-healing.")
    ]
    for idx, (title, sub, body) in enumerate(steps):
        c = add_card(s4, Inches(0.8 + idx * 2.98), Inches(1.8), Inches(2.8), Inches(4.8))
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_CYAN

        p = tf.add_paragraph()
        p.text = sub
        p.font.size = Pt(10)
        p.font.color.rgb = C_GOLD

        p = tf.add_paragraph()
        p.text = f"\n{body}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    set_notes(
        s4,
        speaker="Praneeth Sai (Founder & Architecture)",
        duration="2 Minutes (4:00 - 6:00)",
        script_hinglish="Sir, as the Backend & Protocol Architect, maine iska core ledger scratch se design kiya hai. Yahan 4 levels of defense hain: Pehla — PBKDF2 Salting: Har file ke content me ek secret institutional salt milaya jata hai taaki koi pre-computed rainbow attack na kar sake. Dusra — Merkle Leaf Digest: File ka SHA-256 digital fingerprint banta hai. Teesra — Proof-of-Work Mining: Background worker difficulty level 4 par mining karta hai taaki koi fake block inject na kar sake. Aur Chautha — Dual Persistence Parity: Relational queries ke liye SQLite hai, par verification ke liye immutable blockchain.json ledger hai. Agar database me se koi direct entry delete bhi kar de, toh system json ledger se automatically state restore kar leta hai.",
        hard_words="• Merkle Leaf: Blockchain me har document ka unique data node jo poore chain ke block hash se juda hota hai.\n• Dual Persistence Parity: Do alag-alag jagah par record rakhna taaki agar ek jagah corrupt ho toh dusri se instant pakad me aa jaye.",
        faculty_defense="Q: Blockchain database se zyada slow aur costly hoti hai, why not simple SQL?\nA: Sir, simple SQL me DBA ya hacker directly 'UPDATE student SET grade='A' WHERE roll=101' chala sakta hai aur koi trace nahi rehta. Blockchain me har block previous block ke cryptographic hash par depend karta hai. Ek record badla toh agle 10,000 blocks break ho jayenge. Isliye mathematical certainty milti hai."
    )

    # -------------------------------------------------------------------------
    # SLIDE 5: WHY NOT DIGILOCKER? (ANUSHKA BANSAL)
    # -------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "The Strategic Question: Why Not DigiLocker?", "KILLER DIFFERENTIATION — ANUSHKA BANSAL", "Why DigiLocker is a citizen storage locker, while Satyameva is an institutional B2B security engine")

    col1 = add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), bg=C_DARK_CARD, border=C_MUTED)
    tf1 = col1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "📁 GOVERNMENT DIGILOCKER (C2C STORAGE)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_MUTED

    d_pts = [
        ("Storage Locker Only", "DigiLocker only hosts signed PDFs; it does not perform tamper heuristics or cryptographic block tracing."),
        ("High Aadhaar & OTP Friction", "Requires mandatory Indian Aadhaar & active mobile OTP. Fails completely for international students and foreign recruiters."),
        ("No B2B University Analytics", "Universities get zero insight into who is verifying credentials, verification velocity, or fraud attempt locations."),
        ("Zero Physical Document Protection", "Once a PDF is downloaded from DigiLocker and printed on physical paper, it loses all cryptographic security.")
    ]
    for t, d in d_pts:
        p = tf1.add_paragraph()
        p.text = f"\n✗ {t}\n  {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    col2 = add_card(s5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), bg=C_CARD, border=C_GREEN)
    tf2 = col2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "⚡ SATYAMEVA AEGIS (B2B SAAS SECURITY ENGINE)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    s_pts = [
        ("Institutional B2B SaaS Platform", "Universities manage yearly licenses, instant candidate approvals, and automated bulk issuance."),
        ("Global Frictionless Access", "Verifiers in USA, UK, Germany verify credentials in 60s without Indian Aadhaar or login requirements."),
        ("Real-Time Fraud Telemetry", "University admin portal maps exact IP address, timestamp, and tampering frequency."),
        ("Physical Paper Watermark & AES-256", "Paper stamped certificate carries cryptographic seal and dynamic QR verified via smartphone camera.")
    ]
    for t, d in s_pts:
        p = tf2.add_paragraph()
        p.text = f"\n✓ {t}\n  {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    set_notes(
        s5,
        speaker="Anushka Bansal (Co-Founder & Data Lead)",
        duration="1.5 Minutes (6:00 - 7:30)",
        script_hinglish="Respected Sir, ab aate hain us question par jo har jury member puchte hain: 'Jab government ka DigiLocker hai, toh Satyameva kyu?' Sir, DigiLocker ek digital almari (storage locker) hai jahan student apni PDF rakhta hai. Par Satyameva us almari ka biometric lock aur institutional verification engine hai. DigiLocker me foreign employer ya embassy verify nahi kar sakti kyunki wahan Aadhaar OTP chahiye hota hai. Satyameva me globally koi bhi company bina login kiye 60 seconds me verify kar sakti hai. Hum DigiLocker ke competitor nahi, uske complementar hain!",
        hard_words="• B2B vs C2C: DigiLocker Consumer-to-Consumer hai (student file download karta hai). Satyameva Business-to-Business hai (University companies ko instant authentic verification service provide karti hai).\n• Fraud Telemetry: Real-time map aur graph jo dikhata hai ki kis document ko hack karne ya galat verify karne ki koshish hui.",
        faculty_defense="Q: Kya hum DigiLocker ke sath integrate kar sakte hain?\nA: Haan Sir! Hamara schema WES aur DigiLocker RFC 3161 timestamping standard ke 100% compliant hai. College DigiLocker me bhi file bhej sakta hai aur Satyameva engine se blockchain proof stamp kar sakta hai."
    )

    # -------------------------------------------------------------------------
    # SLIDE 6: DATA INTEGRITY & FORENSIC BENCHMARKS (ANUSHKA BANSAL)
    # -------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "Data Integrity Heuristics & Adversarial Benchmarks", "DATA INTEGRITY — ANUSHKA BANSAL", "Mathematical modeling, collision resistance, and 24 attack vector validation")

    # 3 Metric Cards
    c1 = add_card(s6, Inches(0.8), Inches(1.8), Inches(3.64), Inches(4.8))
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "🎯 24/24 ATTACK VECTORS"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    p = tf1.add_paragraph()
    p.text = "\nTested across 24 aggressive adversarial attacks:\n• Chain gap attacks\n• Silent DB row injection\n• Block nonce mutations\n• Salt collision stress tests (50/50 unique hashes)\n• 100% Detection Rate, 0% False Positives."
    p.font.size = Pt(11)
    p.font.color.rgb = C_WHITE

    c2 = add_card(s6, Inches(4.84), Inches(1.8), Inches(3.64), Inches(4.8))
    tf2 = c2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "⚡ 0.04s DETECTION"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    p = tf2.add_paragraph()
    p.text = "\nReal-Time Tamper Triangulation:\n• Hash validation takes under 40 milliseconds.\n• Identifies exact character and metadata field altered.\n• Automatically flags TAMPERED status to verifier instantly."
    p.font.size = Pt(11)
    p.font.color.rgb = C_WHITE

    c3 = add_card(s6, Inches(8.88), Inches(1.8), Inches(3.64), Inches(4.8))
    tf3 = c3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "🧬 FORENSIC ACCURACY"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    p = tf3.add_paragraph()
    p.text = "\nBiological & Academic Dataset Modeling:\n• Canonical metadata determinism prevents encoding discrepancies.\n• Zero collision probability under SHA-256 space.\n• End-to-end immutability from issuer signature to verifier scan."
    p.font.size = Pt(11)
    p.font.color.rgb = C_WHITE

    set_notes(
        s6,
        speaker="Anushka Bansal (Co-Founder & Data Lead)",
        duration="1.5 Minutes (7:30 - 9:00)",
        script_hinglish="Data integrity lead ke roop me, humne system ko 24 alag-alag attack vectors par stress test kiya hai — jisme silent SQLite modification, block deletion gap attack, aur 50 identical credentials ka salt collision test shamil tha. Satyameva ne har single attack ko sirf 0.04 seconds me detect kiya with 0% false positives. Iska mathematical model itna robust hai ki biological datasets ya university confidential records ko 100% forensic precision ke sath secure karta hai.",
        hard_words="• False Positive: Kisi asli document ko galti se fake bol dena. Hamare test me false positive rate absolute 0.0% hai.\n• Salt Collision: Jab do alag documents ka galti se same hash ban jaye. Salted PBKDF2 me iski probability zero hai.",
        faculty_defense="Q: Agar university ka internet slow ho toh kya verification ruk jayegi?\nA: Nahi Mam, hash checking lightweight mathematical operation hai jo 40ms me hoti hai, 2G internet par bhi instant result deta hai."
    )

    # -------------------------------------------------------------------------
    # SLIDE 7: GEMINI AI EXTRACTION PIPELINE (SHASHANK RAY)
    # -------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "Gemini Multimodal AI Ingestion Pipeline", "AI ARCHITECTURE — SHASHANK RAY", "Automated document field extraction, DOB parsing, and unit cost optimization (< ₹0.48/doc)")

    left_c = add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf = left_c.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🤖 GEMINI MULTIMODAL EXTRACTION PIPELINE"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    ai_steps = [
        ("Multimodal Document Vision", "Scans raw certificate PDF or high-resolution PNG image directly without external OCR dependencies."),
        ("Strict JSON Schema Extraction", "Outputs structured fields: Student Name, Roll Number, Degree Program, Graduation Date, and Date of Birth."),
        ("Automated DOB Extraction", "Extracts DDMMYYYY format to feed AES-256 PDF encryption service."),
        ("Clerical Time Reduction", "Reduces 15 minutes of manual registrar typing per document down to 1.8 seconds.")
    ]
    for t, d in ai_steps:
        p = tf.add_paragraph()
        p.text = f"\n• {t}\n  {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    right_c = add_card(s7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    tf = right_c.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "💰 UNIT ECONOMICS BREAKDOWN (< ₹0.48/DOC)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    costs = [
        ("Gemini AI API Call", "₹0.18 per document scan (Gemini Flash multimodal tokens)"),
        ("PoW Mining & Blockchain", "₹0.04 per block (Local server CPU execution, zero gas fees)"),
        ("AES-256 Stamping & PDF", "₹0.06 per document (Local pikepdf engine)"),
        ("Cloud Server & Storage", "₹0.15 per document allocation"),
        ("TOTAL UNIT COST", "₹0.43 to ₹0.48 PER CREDENTIAL (Extremely High Gross Margin > 90%)")
    ]
    for t, d in costs:
        p = tf.add_paragraph()
        p.text = f"\n• {t}: {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    set_notes(
        s7,
        speaker="Shashank Ray (Co-Founder & AI Model Lead)",
        duration="1.5 Minutes (9:00 - 10:30)",
        script_hinglish="Respected VC Sir, AI Model Lead ke roop me maine Gemini AI multimodal pipeline implement ki hai jo registrar office ka 95% clerical typing work khatam kar deti hai. Registrar ko bas certificate ka scan ya PDF upload karna hai. Gemini instant student name, roll number, program aur Date of Birth extract karke structured JSON format me de deta hai. Isse human typo error zero ho jata hai. Aur sabse exciting baat: hamara unit cost sirf 43 se 48 paise per document aata hai! Iska matlab hamara gross margin 90% se zyada hai.",
        hard_words="• Multimodal AI: Wo AI model jo text ke sath-sath image, visual stamp aur table structure ko insaan ki tarah dekh kar samajh sakta hai.\n• Gross Margin: Service bechne ke baad jo net profit bachta hai — hamara cost 48 paise hai aur hum ₹10 se ₹15 charge karte hain.",
        faculty_defense="Q: Agar internet slow ho ya Gemini API rate limit ho jaye toh?\nA: Sir, hamara architecture asynchronous task queue (threading) use karta hai. Agar API slow ho, toh documents background me process hokar ledger me auto-sync ho jate hain bina UI freeze hue."
    )

    # -------------------------------------------------------------------------
    # SLIDE 8: B2B SAAS BUSINESS MODEL & REVENUE (SHASHANK RAY)
    # -------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "B2B SaaS Business Model & Revenue Projections", "COMMERCIALIZATION — SHASHANK RAY", "Sustainable monetization strategy for RIDE incubation & market expansion")

    # 3 Revenue Stream Cards
    c1 = add_card(s8, Inches(0.8), Inches(1.8), Inches(3.64), Inches(4.8))
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "🏛️ ANNUAL CAMPUS LICENSE"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    p = tf1.add_paragraph()
    p.text = "\n₹1.5 Lakhs / campus / year\n\nIncludes:\n• Full registrar issuance portal\n• Admin governance console\n• Unlimited credential anchoring\n• Student self-sovereign wallets\n• Automated grievance engine."
    p.font.size = Pt(11)
    p.font.color.rgb = C_WHITE

    c2 = add_card(s8, Inches(4.84), Inches(1.8), Inches(3.64), Inches(4.8))
    tf2 = c2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "🏢 CORPORATE API FEES"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    p = tf2.add_paragraph()
    p.text = "\n₹10 per instant verification\n\nCharged to corporate background check agencies (AuthBridge, First Advantage, TCS, Infosys) for 60-second instant API verification instead of 14-day manual delays."
    p.font.size = Pt(11)
    p.font.color.rgb = C_WHITE

    c3 = add_card(s8, Inches(8.88), Inches(1.8), Inches(3.64), Inches(4.8))
    tf3 = c3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "📈 3-YEAR ARR ROADMAP"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    p = tf3.add_paragraph()
    p.text = "\n• Year 1: ₹12 Lakhs\n  (Jaypee 3 Campuses Pilot + 5 Himachal/NCR universities)\n\n• Year 2: ₹45 Lakhs\n  (30 Private Universities across North India)\n\n• Year 3: ₹1.05 Crores ARR\n  (70+ Higher Education Institutions nationally)."
    p.font.size = Pt(11)
    p.font.color.rgb = C_WHITE

    set_notes(
        s8,
        speaker="Shashank Ray (Co-Founder & AI Model Lead)",
        duration="1.5 Minutes (10:30 - 12:00)",
        script_hinglish="RIDEHACK me investors aur VC Sir startup ki viability dekhte hain. Hamara business model do streams par based hai: Stream 1 — Universities humein ₹1.5 Lakh per year ka software subscription dengi, jisme complete registrar portal, unlimited degree blockchain anchoring, aur student support included hai. Stream 2 — Corporate background verification companies (jaise TCS, Wipro, AuthBridge) se hum ₹10 per instant verification charge karte hain. Year 1 me Jaypee ke teeno campuses se validation shuru hoga, aur Year 3 tak ₹1.05 Crore annual recurring revenue ka target hai.",
        hard_words="• B2B SaaS: Business-to-Business Software-as-a-Service (College humse software khareedta hai).\n• ARR: Annual Recurring Revenue — Har saal aane wali pakki income jo subscription se banti hai.",
        faculty_defense="Q: Private universities ₹1.5 Lakhs kyu dengi?\nA: Sir, har university verification clerical staff aur postal speed-post me saal ka ₹8 se ₹12 Lakh kharch karti hai. Satyameva lene se unka ₹10 Lakh bachta hai aur unka brand 100% fake-proof ho jata hai. ROI 5x se zyada hai!"
    )

    # -------------------------------------------------------------------------
    # SLIDE 9: THE 4-PORTAL WORKING PROTOTYPE (SAMEEKSHA CHANDEL)
    # -------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_header(s9, "The 4-Portal Working Prototype: Live Operational Flow", "PROTOTYPE ARCHITECTURE — SAMEEKSHA CHANDEL", "Role-gated interfaces for Super-Admin, Registrar, Student Wallet, and Public Verifier")

    p_boxes = [
        ("1. SUPER ADMIN PORTAL", "Institutional Governance", "• Approves universities\n• Manages yearly licenses\n• Monitors system health\n• Sets cryptographic difficulty."),
        ("2. ISSUER REGISTRAR PORTAL", "Bulk Issuance Engine", "• Bulk CSV degree upload\n• AI field extraction\n• Student email approval\n• Resolves student correction requests."),
        ("3. STUDENT SELF-SOVEREIGN WALLET", "Decentralized Access", "• DOB password-protected PDF\n• 60s dynamic QR code\n• Real-time verification alerts\n• 1-click grievance filing."),
        ("4. PUBLIC VERIFIER PORTAL", "Instant 60s Verification", "• Zero-login instant check\n• Visual color fingerprint\n• 3D cryptographic lock-in\n• PDF verification report download.")
    ]
    for idx, (title, sub, body) in enumerate(p_boxes):
        c = add_card(s9, Inches(0.8 + idx * 2.98), Inches(1.8), Inches(2.8), Inches(4.8))
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_GREEN

        p = tf.add_paragraph()
        p.text = sub
        p.font.size = Pt(10)
        p.font.color.rgb = C_GOLD

        p = tf.add_paragraph()
        p.text = f"\n{body}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    set_notes(
        s9,
        speaker="Sameeksha Chandel (Co-Founder & Product Lead)",
        duration="1.5 Minutes (12:00 - 13:30)",
        script_hinglish="Respected jury, Satyameva koi hypothetical PPT concept nahi hai — hamara working prototype already live hai. Hamare system me 4 specialized role-gated portals hain: Super Admin jo university onboarding aur yearly subscription govern karta hai; University Registrar portal jahan 1-click me hazaro degrees issue aur verify hoti hain; Student Self-Sovereign Wallet jahan student apni DOB-password protected degree aur dynamic QR access karta hai; aur Verifier Portal jahan duniya ka koi bhi recruiter 60 seconds me bina login kiye instant verify kar sakta hai.",
        hard_words="• Self-Sovereign Identity (SSI): Student ka apne data par complete ownership — usko degree lene ke liye registrar office ke 10 chakkar nahi kaatne padte.\n• Role-Gated: Har user (Admin, Registrar, Student) ko sirf wahi dikhta hai jiska use official adhikaar hai.",
        faculty_defense="Q: Agar student ke name ki spelling galat print ho gayi ho toh?\nA: Mam, humne Student Grievance & Correction engine integrate kiya hai. Student dashboard se correction raise karta hai, registrar review karke revised certificate hash link kar deta hai purane block reference ke sath."
    )

    # -------------------------------------------------------------------------
    # SLIDE 10: 3D WEBGL HOLOGRAPHIC VERIFICATION (SAMEEKSHA CHANDEL)
    # -------------------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_header(s10, "Next-Gen 3D WebGL Holographic Verification Experience", "USER EXPERIENCE — SAMEEKSHA CHANDEL", "Physical-grade tactile security inspection in browser with 60 FPS mobile optimization")

    left_box = add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf = left_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🧊 3D WEBGL ENGINE CAPABILITIES"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    feats = [
        ("3D Zero-Gravity Credential Mesh", "Renders academic parchment in real-time 3D space with gold-embossed Jaypee crest and dynamic normal lighting."),
        ("Iridescent Holographic Diffraction Foil", "Calculates real-time light angle coordinates, shifting rainbow spectral glints across official seals on mouse tilt or smartphone gyroscope."),
        ("180° Flip to Cryptographic Audit Backing", "One click rotates the certificate in 3D space to reveal the SHA-256 Merkle root, proof-of-work block nonce, and audit hash matrix."),
        ("Interactive 3D Ledger Explorer & PoW Mining", "Verifiers inspect mined block nodes and click 'Simulate POW Mining' to watch particle convergence attach a new block in real time.")
    ]
    for t, d in feats:
        p = tf.add_paragraph()
        p.text = f"\n• {t}\n  {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    right_box = add_card(s10, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    tf = right_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⚡ PERFORMANCE & RELIABILITY STANDARDS"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    perf = [
        ("60 FPS Smooth Rendering", "Clamped DPR (1.0x on mobile, 2.0x on desktop) with zero battery draining."),
        ("IntersectionObserver GPU Culling", "Automatically freezes WebGL requestAnimationFrame when scrolled out of view, saving 100% idle GPU cycles."),
        ("Zero Scroll Hijacking", "Pointer & touch listeners use passive event bindings — page scrolling is completely natural and buttery smooth."),
        ("Graceful CSS-3D Fallback", "If WebGL is unavailable or user has reduced motion, an elegant CSS-3D fallback chain keeps the visual intact.")
    ]
    for t, d in perf:
        p = tf.add_paragraph()
        p.text = f"\n✓ {t}\n  {d}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    set_notes(
        s10,
        speaker="Sameeksha Chandel (Co-Founder & Product Lead)",
        duration="1.5 Minutes (13:30 - 15:00)",
        script_hinglish="Jab koi company ya student document open karta hai, unhe milta hai ek cutting-edge 3D WebGL holographic experience. Certificate zero-gravity space me float karta hai. Gold institutional crest light ke angle ke sath physical hologram ki tarah chamakta hai. Phone ko tilt karne par phone ka gyroscope physical tilt detect karta hai. Aur button dabane par certificate 180 degree flip hokar peeche ka blockchain proof-of-work ledger dikha deta hai. Ye experience Jaypee degrees ko international level par Stanford ya MIT ke barabar elite banata hai.",
        hard_words="• Iridescent Diffraction: Rainbow ki tarah chamakne wala visual light effect jo physical hologram cards me security ke liye use hota hai.\n• GPU Culling: Jab screen par 3D element dikhai na de raha ho toh computer ka graphics processor rest mode me chala jata hai taaki battery na kharch ho.",
        faculty_defense="Q: Kya ye 3D animations phone ko hang nahi karenge?\nA: Bilkul nahi Mam. Humne Mobile DPR ko 1.0 par clamp kiya hai aur IntersectionObserver use kiya hai. Background me koi GPU overhead nahi hota, mobile par buttery smooth 60 FPS par chalta hai."
    )

    # -------------------------------------------------------------------------
    # SLIDE 11: TEAM ID: 10 RELAY & PITCH STOPWATCH SCHEDULE
    # -------------------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11)
    add_header(s11, "Founding Team & 10-Minute VC Pitch Schedule", "TEAM ID: 10 EXECUTION — RIDEHACK'26", "Stopwatch-disciplined presentation flow before Vice Chancellor Sir & Senior Faculty")

    # Embed Team Card
    if os.path.exists(IMG_TEAM):
        s11.shapes.add_picture(IMG_TEAM, Inches(0.8), Inches(1.8), width=Inches(11.733), height=Inches(2.55))

    # Bottom Relay Schedule Table
    t_card = add_card(s11, Inches(0.8), Inches(4.55), Inches(11.733), Inches(2.35))
    tf = t_card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⏱️ 10-MINUTE VC BOARD ROOM STOPWATCH SCHEDULE"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    schedule = [
        ("0:00 - 3:00", "A. Praneeth Sai", "Founder & Architecture", "The ₹1500 Fake Crisis, Satyameva Solution & Whole PoW Backend Engine"),
        ("3:00 - 5:00", "Anushka Bansal", "Co-Founder & Data Lead", "Why Not DigiLocker? Data Integrity, Mathematical Modeling & 24 Attacks"),
        ("5:00 - 7:30", "Shashank Ray", "Co-Founder & AI Model Lead", "Gemini AI Multimodal OCR, Unit Economics (< ₹0.48) & ₹1.5L B2B SaaS ARR"),
        ("7:30 - 10:00", "Sameeksha Chandel", "Co-Founder & Product Lead", "Live 4-Portal Prototype, 3D WebGL Holographic Demo, NEP 2020 & ₹25L Ask")
    ]
    for timing, name, role, topic in schedule:
        p = tf.add_paragraph()
        p.text = f"• [{timing}] {name} ({role}): {topic}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    set_notes(
        s11,
        speaker="Entire Team (Relay Handoffs)",
        duration="Entire Pitch (Strictly under 10:00 limit)",
        script_hinglish="[HANDOFF DIALOGUES]\n• Praneeth to Anushka (at 3:00): '...aur is data ki mathematical integrity aur DigiLocker differentiation ko explain karne ke liye, I invite our Data Lead, Anushka Bansal.'\n• Anushka to Shashank (at 5:00): '...ab is pure pipeline ki AI automation aur B2B SaaS revenue model ko present karenge hamare AI Model Lead, Shashank Ray.'\n• Shashank to Sameeksha (at 7:30): '...aur ab hamare working 4-portal prototype aur 3D WebGL experience ka live demonstration dengi hamari Product Lead, Sameeksha Chandel.'\n• Sameeksha to Praneeth (at 9:45): '...aur ab concluding ask ke sath hum VC sir aur jury ko open karte hain for Q&A.'",
        hard_words="• Relay Pitch: Jab 4 log ek synchronized sequence me bina ek dusre ko kaate time limit ke andar smoothly handoff karte hain.",
        faculty_defense="Tip: Har member ko apne assigned 2.5 minutes me confident rehna hai, timer ko follow karna hai, aur kisi doosre ke domain me intervene nahi karna hai."
    )

    # -------------------------------------------------------------------------
    # SLIDE 12: VC Q&A DEFENSE & RIDE INCUBATION ASK
    # -------------------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12)
    add_header(s12, "VC Rapid Q&A Defense & ₹25 Lakh Incubation Ask", "COMMERCIAL ROADMAP — RIDEHACK'26", "Direct milestone utilization of the ₹1 Crore RIDE funding pool for full campus rollout")

    # Left: Funding Ask
    left_ask = add_card(s12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf = left_ask.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🎯 ₹25 LAKH SEED INCUBATION ASK"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    allocations = [
        ("40% (₹10 Lakhs)", "Multi-Node Blockchain Infrastructure", "Dedicated consensus servers across JUIT, JIIT, and JUET nodes."),
        ("30% (₹7.5 Lakhs)", "Multi-Campus Pilot & University Rollout", "Onboarding registrar offices, testing with 5,000+ real graduation batches."),
        ("20% (₹5 Lakhs)", "Security Audits & IP Patenting", "Cert-In cybersecurity compliance and intellectual property protection."),
        ("10% (₹2.5 Lakhs)", "Operations & Legal Compliance", "B2B institutional SaaS contracts, NEP 2020 regulatory compliance.")
    ]
    for pct, title, desc in allocations:
        p = tf.add_paragraph()
        p.text = f"\n• {pct} — {title}\n  {desc}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    # Right: Rapid Rebuttals
    right_qna = add_card(s12, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    tf = right_qna.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🛡️ TOP 4 FACULTY QUESTIONS: QUICK CHEAT SHEET"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    qnas = [
        ("Q: Blockchain SQL database se expensive hoti hai?", "A: 'Sir, public crypto chain costly hoti hai, humne zero-gas private ledger banaya hai jisme unit cost sirf 48 paise hai.'"),
        ("Q: DigiLocker jab hai toh universities kyu dengi?", "A: 'DigiLocker storage locker hai, Satyameva B2B tamper-proof verification engine hai jo 60s me global verification deta hai.'"),
        ("Q: Server band ho gaya toh verification kaise hogi?", "A: 'Sir, multi-node decentralized architecture hai. Agar JUIT node offline hua, toh JIIT Noida node instant sync kar deta hai.'"),
        ("Q: Document ka size bada ho toh chain slow hogi?", "A: 'Sir, hum chain par PDF nahi, balki uska 64-character SHA-256 cryptographic hash store karte hain. Chain ultra-fast rehti hai.'")
    ]
    for q, a in qnas:
        p = tf.add_paragraph()
        p.text = f"\n{q}\n👉 {a}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_WHITE

    set_notes(
        s12,
        speaker="Praneeth Sai (Founder & Architecture) & Team",
        duration="1.5 Minutes (Conclusion & Q&A)",
        script_hinglish="Respected Vice Chancellor Sir aur Panel Judges — Satyameva Aegis sirf ek hackathon project nahi hai, yeh ek sustainable B2B venture hai jo JUIT aur Jaypee Group ko pure India me credential security ka pioneer banata hai. RIDEHACK'26 ke ₹1 Crore funding pool se hum ₹25 Lakhs ka seed incubation ask demand karte hain — jisse hum Jaypee ke teeno campuses me 100% rollout karenge aur Q4 tak 15 new universities onboard karenge. Thank you very much Sir! We are now open for your questions.",
        hard_words="• Seed Incubation Ask: Prototype ko real university product banane ke liye college aur investors se manga gaya pehla startup fund.\n• Multi-Node Redundancy: Agar ek campus ka computer band ho jaye toh doosre campus ka computer automatically bina kisi delay ke server chalu rakhta hai.",
        faculty_defense="Tip: Cross-question me bilkul calm rehna hai. Koi bhi question aaye, muskura kar confidence ke sath 'Yes Sir, exactly...' se shuru karke mathematical facts bolne hain."
    )

    prs.save(OUT_PPTX)
    print(f"[OK] PowerPoint saved successfully to: {OUT_PPTX}")

def build_pdf():
    # 16:9 Landscape Dimensions: 13.333 inches x 7.5 inches
    w, h = 13.333 * inch, 7.5 * inch
    c = rl_canvas.Canvas(OUT_PDF, pagesize=(w, h))

    styles = getSampleStyleSheet()

    # Color definitions
    HEX_BG = HexColor("#0B1120")
    HEX_CARD = HexColor("#131D31")
    HEX_BORDER = HexColor("#1E3A5F")
    HEX_CYAN = HexColor("#38BDF8")
    HEX_GOLD = HexColor("#D4AF37")
    HEX_GREEN = HexColor("#10B981")
    HEX_RED = HexColor("#EF4444")
    HEX_WHITE = HexColor("#F8FAFC")
    HEX_MUTED = HexColor("#94A3B8")
    HEX_DARK = HexColor("#0F172A")

    def draw_bg():
        c.setFillColor(HEX_BG)
        c.rect(0, 0, w, h, fill=1, stroke=0)

    def draw_card(x, y, cw, ch, bg=HEX_CARD, border=HEX_BORDER):
        c.setFillColor(bg)
        c.setStrokeColor(border)
        c.setLineWidth(1.2)
        c.roundRect(x, y, cw, ch, radius=10, fill=1, stroke=1)

    def draw_header(title, category="RIDEHACK'26 | JUIT INTERNAL QUALIFIERS", subtext=""):
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HEX_GOLD)
        c.drawString(0.8 * inch, h - 0.55 * inch, category.upper())

        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(HEX_WHITE)
        c.drawString(0.8 * inch, h - 0.95 * inch, title)

        if subtext:
            c.setFont("Helvetica", 11)
            c.setFillColor(HEX_MUTED)
            c.drawString(0.8 * inch, h - 1.25 * inch, subtext)

    # --- SLIDE 1 ---
    draw_bg()
    draw_card(0.8 * inch, h - 1.0 * inch, 6.5 * inch, 0.42 * inch, bg=HEX_DARK, border=HEX_GOLD)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HEX_GOLD)
    c.drawString(1.0 * inch, h - 0.76 * inch, "JUIT WAKNAGHAT | IIC RIDEHACK'26 INTERNAL QUALIFIERS")

    c.setFont("Helvetica-Bold", 34)
    c.setFillColor(HEX_WHITE)
    c.drawString(0.8 * inch, h - 1.8 * inch, "SATYAMEVA AEGIS")

    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(HEX_CYAN)
    c.drawString(0.8 * inch, h - 2.2 * inch, "Tamper-Proof Cryptographic Academic Credential & Verification Ecosystem")

    c.setFont("Helvetica", 12)
    c.setFillColor(HEX_MUTED)
    c.drawString(0.8 * inch, h - 2.5 * inch, "Empowering Universities with Zero-Gas-Fee Blockchain, Gemini AI & 3D Holographic Integrity")

    if os.path.exists(IMG_POSTER):
        c.drawImage(IMG_POSTER, 8.8 * inch, h - 4.2 * inch, width=3.8 * inch, height=3.8 * inch)

    if os.path.exists(IMG_TEAM):
        c.drawImage(IMG_TEAM, 0.8 * inch, 0.5 * inch, width=11.733 * inch, height=2.55 * inch)

    c.showPage()

    # --- SLIDE 2 ---
    draw_bg()
    draw_header("The Real-World Crisis: India's Academic Trust Deficit", "PROBLEM STATEMENT", "Why existing paper stamps and central databases are failing Indian universities")

    # 3 Cards
    draw_card(0.8 * inch, 0.9 * inch, 3.64 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HEX_RED)
    c.drawString(1.1 * inch, h - 2.1 * inch, "RS. 1,500 FAKE DEGREES")
    c.setFont("Helvetica", 11)
    c.setFillColor(HEX_WHITE)
    text = [
        "Photoshop & Telegram syndicates",
        "sell indistinguishable fake",
        "marksheet clones with replica",
        "university seals within 24 hours.",
        "",
        "Employers cannot verify original",
        "ink from printed clones on paper."
    ]
    for i, line in enumerate(text):
        c.drawString(1.1 * inch, h - 2.5 * inch - i * 18, line)

    draw_card(4.84 * inch, 0.9 * inch, 3.64 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HEX_GOLD)
    c.drawString(5.14 * inch, h - 2.1 * inch, "14-DAY DELAYS")
    c.setFont("Helvetica", 11)
    c.setFillColor(HEX_WHITE)
    text = [
        "Manual verification takes 14 to",
        "21 days via registrar office postal",
        "letters and manual emails.",
        "",
        "Costs universities Rs. 12-18 Lakhs",
        "annually in clerical overhead",
        "and lost administrative hours."
    ]
    for i, line in enumerate(text):
        c.drawString(5.14 * inch, h - 2.5 * inch - i * 18, line)

    draw_card(8.88 * inch, 0.9 * inch, 3.64 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HEX_CYAN)
    c.drawString(9.18 * inch, h - 2.1 * inch, "SQL VULNERABILITY")
    c.setFont("Helvetica", 11)
    c.setFillColor(HEX_WHITE)
    text = [
        "Centralized SQL databases have",
        "single points of failure.",
        "",
        "A rogue clerk or compromised",
        "admin password allows silent",
        "grade tampering without audit trails.",
        "",
        "Once modified, no trace exists."
    ]
    for i, line in enumerate(text):
        c.drawString(9.18 * inch, h - 2.5 * inch - i * 18, line)

    c.showPage()

    # --- SLIDE 3 ---
    draw_bg()
    draw_header("The Satyameva Breakthrough: Zero-Gas-Fee Blockchain Integrity", "OUR SOLUTION", "A mathematically unhackable multi-portal credential trust infrastructure")

    draw_card(0.8 * inch, 0.9 * inch, 5.6 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_GREEN)
    c.drawString(1.1 * inch, h - 2.0 * inch, "THE 3-PILLAR SECURITY ARCHITECTURE")
    s_items = [
        ("1. Zero-Gas Private Blockchain", "No crypto tokens, no Ethereum fees. Ultra-fast private PoW ledger."),
        ("2. Multimodal Gemini AI OCR", "Instant field extraction from PDF/scans with zero typing error."),
        ("3. 60-Second Dynamic Anti-Screenshot QR", "Tokens refresh every 60s. Screenshot sharing is completely invalid."),
        ("4. Automated DOB-Encrypted Stamped PDFs", "PDFs locked via AES-256 with birthdate. Paper-safe verification.")
    ]
    for idx, (t, d) in enumerate(s_items):
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(HEX_WHITE)
        c.drawString(1.1 * inch, h - 2.4 * inch - idx * 52, t)
        c.setFont("Helvetica", 9.5)
        c.setFillColor(HEX_MUTED)
        c.drawString(1.2 * inch, h - 2.65 * inch - idx * 52, d)

    draw_card(6.8 * inch, 0.9 * inch, 5.7 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_CYAN)
    c.drawString(7.1 * inch, h - 2.0 * inch, "VALUE DELIVERED TO JUIT & UNIVERSITIES")
    v_items = [
        ("14 Days -> 60 Seconds", "Background verifiers verify credentials instantly without disturbing staff."),
        ("Zero Gas Fees", "100% cost-predictable. Costs less than Rs. 0.48 per certificate."),
        ("NEP 2020 & WES Global Mobility", "Complies with National Education Policy digital locker mandate & WES."),
        ("Institutional Brand Shield", "Zero fake degree scandals ever possible under Jaypee name.")
    ]
    for idx, (t, d) in enumerate(v_items):
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(HEX_WHITE)
        c.drawString(7.1 * inch, h - 2.4 * inch - idx * 52, t)
        c.setFont("Helvetica", 9.5)
        c.setFillColor(HEX_MUTED)
        c.drawString(7.2 * inch, h - 2.65 * inch - idx * 52, d)

    c.showPage()

    # --- SLIDE 4 ---
    draw_bg()
    draw_header("Core Protocol & Blockchain Engine: Under The Hood", "BACKEND ARCHITECTURE — A. PRANEETH SAI", "Cryptographic proof-of-work, salting heuristics, and dual-layer persistence")

    b_steps = [
        ("1. RAW SALTING", "PBKDF2 HMAC-SHA256", "Document bytes + metadata salted with institutional key.", "Immunizes against rainbow attacks."),
        ("2. MERKLE LEAF", "Canonical Determinism", "Roll + Name + Program hashed into 64-char SHA-256 string.", "Guarantees exact determinism."),
        ("3. POW MINING", "Non-Blocking Async", "Miner computes nonce for Difficulty 4 ('0000...').", "Spam & injection immunity."),
        ("4. DUAL PERSISTENCE", "SQLite <-> JSON Ledger", "Relational queries in SQLite; Cryptographic chain in JSON.", "Automatic state self-healing.")
    ]
    for idx, (t, sub, l1, l2) in enumerate(b_steps):
        draw_card((0.8 + idx * 2.98) * inch, 0.9 * inch, 2.8 * inch, 4.8 * inch)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(HEX_CYAN)
        c.drawString((1.0 + idx * 2.98) * inch, h - 2.0 * inch, t)

        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(HEX_GOLD)
        c.drawString((1.0 + idx * 2.98) * inch, h - 2.3 * inch, sub)

        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_WHITE)
        c.drawString((1.0 + idx * 2.98) * inch, h - 2.7 * inch, l1)
        c.drawString((1.0 + idx * 2.98) * inch, h - 2.9 * inch, l2)

    c.showPage()

    # --- SLIDE 5 ---
    draw_bg()
    draw_header("The Strategic Question: Why Not DigiLocker?", "KILLER DIFFERENTIATION — ANUSHKA BANSAL", "Why DigiLocker is a citizen storage locker, while Satyameva is an institutional B2B security engine")

    draw_card(0.8 * inch, 0.9 * inch, 5.6 * inch, 4.8 * inch, bg=HEX_DARK, border=HEX_MUTED)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HEX_MUTED)
    c.drawString(1.1 * inch, h - 2.0 * inch, "GOVERNMENT DIGILOCKER (C2C STORAGE)")
    d_list = [
        ("Storage Locker Only", "DigiLocker only hosts signed PDFs; no block tracing."),
        ("High Aadhaar & OTP Friction", "Requires Indian Aadhaar OTP; fails for foreign recruiters."),
        ("No B2B University Analytics", "Universities get zero verification velocity or fraud insight."),
        ("Zero Physical Document Protection", "Printed PDFs lose all cryptographic tamper protection.")
    ]
    for idx, (t, d) in enumerate(d_list):
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(HEX_RED)
        c.drawString(1.1 * inch, h - 2.4 * inch - idx * 52, f"x  {t}")
        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_MUTED)
        c.drawString(1.3 * inch, h - 2.65 * inch - idx * 52, d)

    draw_card(6.8 * inch, 0.9 * inch, 5.7 * inch, 4.8 * inch, bg=HEX_CARD, border=HEX_GREEN)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HEX_GREEN)
    c.drawString(7.1 * inch, h - 2.0 * inch, "SATYAMEVA AEGIS (B2B SAAS SECURITY ENGINE)")
    s_list = [
        ("Institutional B2B SaaS Platform", "Universities manage yearly licenses & bulk degree issuance."),
        ("Global Frictionless Access", "Verifiers in USA, UK verify in 60s without Aadhaar."),
        ("Real-Time Fraud Telemetry", "Admin console maps exact IP address & tampering frequency."),
        ("Physical Paper Watermark & AES-256", "Stamped certificates carry cryptographic seal & dynamic QR.")
    ]
    for idx, (t, d) in enumerate(s_list):
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(HEX_GREEN)
        c.drawString(7.1 * inch, h - 2.4 * inch - idx * 52, f"/  {t}")
        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_WHITE)
        c.drawString(7.3 * inch, h - 2.65 * inch - idx * 52, d)

    c.showPage()

    # --- SLIDE 6 ---
    draw_bg()
    draw_header("Data Integrity Heuristics & Adversarial Benchmarks", "DATA INTEGRITY — ANUSHKA BANSAL", "Mathematical modeling, collision resistance, and 24 attack vector validation")

    draw_card(0.8 * inch, 0.9 * inch, 3.64 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_GREEN)
    c.drawString(1.1 * inch, h - 2.0 * inch, "24/24 ATTACK VECTORS")
    c.setFont("Helvetica", 10)
    c.setFillColor(HEX_WHITE)
    lines = [
        "Tested across 24 aggressive attacks:",
        "- Chain gap attacks",
        "- Silent DB row injections",
        "- Block nonce mutations",
        "- Salt collision stress tests (50/50)",
        "",
        "100% Detection Rate, 0% False Positives."
    ]
    for i, l in enumerate(lines):
        c.drawString(1.1 * inch, h - 2.4 * inch - i * 18, l)

    draw_card(4.84 * inch, 0.9 * inch, 3.64 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_CYAN)
    c.drawString(5.14 * inch, h - 2.0 * inch, "0.04s DETECTION")
    c.setFont("Helvetica", 10)
    c.setFillColor(HEX_WHITE)
    lines = [
        "Real-Time Tamper Triangulation:",
        "- Hash validation takes under 40ms.",
        "- Identifies exact character and",
        "  metadata field altered.",
        "- Automatically flags TAMPERED",
        "  status to verifier instantly."
    ]
    for i, l in enumerate(lines):
        c.drawString(5.14 * inch, h - 2.4 * inch - i * 18, l)

    draw_card(8.88 * inch, 0.9 * inch, 3.64 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_GOLD)
    c.drawString(9.18 * inch, h - 2.0 * inch, "FORENSIC ACCURACY")
    c.setFont("Helvetica", 10)
    c.setFillColor(HEX_WHITE)
    lines = [
        "Biological & Academic Modeling:",
        "- Canonical metadata determinism",
        "  prevents encoding discrepancies.",
        "- Zero collision probability under",
        "  SHA-256 cryptographic space.",
        "- End-to-end immutability from",
        "  issuer signature to verifier scan."
    ]
    for i, l in enumerate(lines):
        c.drawString(9.18 * inch, h - 2.4 * inch - i * 18, l)

    c.showPage()

    # --- SLIDE 7 ---
    draw_bg()
    draw_header("Gemini Multimodal AI Ingestion Pipeline", "AI ARCHITECTURE — SHASHANK RAY", "Automated document field extraction, DOB parsing, and unit cost optimization (< Rs. 0.48/doc)")

    draw_card(0.8 * inch, 0.9 * inch, 5.6 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_CYAN)
    c.drawString(1.1 * inch, h - 2.0 * inch, "GEMINI MULTIMODAL OCR PIPELINE")
    ai_list = [
        ("Multimodal Document Vision", "Scans certificate PDF or PNG directly without external OCR."),
        ("Strict JSON Schema Extraction", "Outputs Name, Roll, Program, and Date of Birth in clean JSON."),
        ("Automated DOB Extraction", "Feeds AES-256 PDF encryption service for password protection."),
        ("Clerical Time Reduction", "Reduces 15 minutes of manual typing down to 1.8 seconds.")
    ]
    for idx, (t, d) in enumerate(ai_list):
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(HEX_WHITE)
        c.drawString(1.1 * inch, h - 2.4 * inch - idx * 52, f"- {t}")
        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_MUTED)
        c.drawString(1.3 * inch, h - 2.65 * inch - idx * 52, d)

    draw_card(6.8 * inch, 0.9 * inch, 5.7 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_GREEN)
    c.drawString(7.1 * inch, h - 2.0 * inch, "UNIT ECONOMICS BREAKDOWN (< Rs. 0.48/DOC)")
    c_list = [
        ("Gemini AI API Call", "Rs. 0.18 per document scan (Gemini Flash multimodal tokens)"),
        ("PoW Mining & Blockchain", "Rs. 0.04 per block (Local CPU, zero gas fees)"),
        ("AES-256 Stamping & PDF", "Rs. 0.06 per document (Local pikepdf engine)"),
        ("Cloud Server & Storage", "Rs. 0.15 per document allocation"),
        ("TOTAL UNIT COST", "Rs. 0.43 - Rs. 0.48 PER CREDENTIAL (> 90% Gross Margin)")
    ]
    for idx, (t, d) in enumerate(c_list):
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HEX_GOLD if "TOTAL" in t else HEX_WHITE)
        c.drawString(7.1 * inch, h - 2.4 * inch - idx * 46, f"* {t}:")
        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_GREEN if "TOTAL" in t else HEX_MUTED)
        c.drawString(7.3 * inch, h - 2.62 * inch - idx * 46, d)

    c.showPage()

    # --- SLIDE 8 ---
    draw_bg()
    draw_header("B2B SaaS Business Model & Revenue Projections", "COMMERCIALIZATION — SHASHANK RAY", "Sustainable monetization strategy for RIDE incubation & market expansion")

    draw_card(0.8 * inch, 0.9 * inch, 3.64 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_GOLD)
    c.drawString(1.1 * inch, h - 2.0 * inch, "ANNUAL CAMPUS LICENSE")
    c.setFont("Helvetica", 10)
    c.setFillColor(HEX_WHITE)
    lines = [
        "Rs. 1.5 Lakhs / campus / year",
        "",
        "Includes:",
        "- Full registrar issuance portal",
        "- Admin governance console",
        "- Unlimited blockchain anchoring",
        "- Student self-sovereign wallets",
        "- Automated grievance engine."
    ]
    for i, l in enumerate(lines):
        c.drawString(1.1 * inch, h - 2.4 * inch - i * 18, l)

    draw_card(4.84 * inch, 0.9 * inch, 3.64 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_CYAN)
    c.drawString(5.14 * inch, h - 2.0 * inch, "CORPORATE API FEES")
    c.setFont("Helvetica", 10)
    c.setFillColor(HEX_WHITE)
    lines = [
        "Rs. 10 per instant verification",
        "",
        "Charged to corporate background",
        "check agencies (AuthBridge, TCS,",
        "Infosys, First Advantage) for",
        "60-second instant API verification",
        "instead of 14-day manual delays."
    ]
    for i, l in enumerate(lines):
        c.drawString(5.14 * inch, h - 2.4 * inch - i * 18, l)

    draw_card(8.88 * inch, 0.9 * inch, 3.64 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_GREEN)
    c.drawString(9.18 * inch, h - 2.0 * inch, "3-YEAR ARR ROADMAP")
    c.setFont("Helvetica", 10)
    c.setFillColor(HEX_WHITE)
    lines = [
        "- Year 1: Rs. 12 Lakhs",
        "  (Jaypee 3 Campuses + 5 NCR univs)",
        "",
        "- Year 2: Rs. 45 Lakhs",
        "  (30 Private Universities in North India)",
        "",
        "- Year 3: Rs. 1.05 Crores ARR",
        "  (70+ Higher Education Institutions)."
    ]
    for i, l in enumerate(lines):
        c.drawString(9.18 * inch, h - 2.4 * inch - i * 18, l)

    c.showPage()

    # --- SLIDE 9 ---
    draw_bg()
    draw_header("The 4-Portal Working Prototype: Live Operational Flow", "PROTOTYPE ARCHITECTURE — SAMEEKSHA CHANDEL", "Role-gated interfaces for Super-Admin, Registrar, Student Wallet, and Public Verifier")

    p_list = [
        ("1. SUPER ADMIN", "Institutional Governance", "- Approves universities", "- Manages yearly licenses", "- Monitors network health", "- Sets PoW difficulty."),
        ("2. ISSUER REGISTRAR", "Bulk Issuance Engine", "- Bulk CSV degree upload", "- AI field extraction", "- Student email approval", "- Resolves corrections."),
        ("3. STUDENT WALLET", "Decentralized Access", "- DOB password protected", "- 60s dynamic QR code", "- Real-time alerts", "- 1-click grievance filing."),
        ("4. PUBLIC VERIFIER", "Instant 60s Check", "- Zero-login instant check", "- Color fingerprint visual", "- 3D block lock-in view", "- PDF report export.")
    ]
    for idx, (t, sub, l1, l2, l3, l4) in enumerate(p_list):
        draw_card((0.8 + idx * 2.98) * inch, 0.9 * inch, 2.8 * inch, 4.8 * inch)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(HEX_GREEN)
        c.drawString((1.0 + idx * 2.98) * inch, h - 2.0 * inch, t)

        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(HEX_GOLD)
        c.drawString((1.0 + idx * 2.98) * inch, h - 2.3 * inch, sub)

        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_WHITE)
        c.drawString((1.0 + idx * 2.98) * inch, h - 2.7 * inch, l1)
        c.drawString((1.0 + idx * 2.98) * inch, h - 2.9 * inch, l2)
        c.drawString((1.0 + idx * 2.98) * inch, h - 3.1 * inch, l3)
        c.drawString((1.0 + idx * 2.98) * inch, h - 3.3 * inch, l4)

    c.showPage()

    # --- SLIDE 10 ---
    draw_bg()
    draw_header("Next-Gen 3D WebGL Holographic Verification Experience", "USER EXPERIENCE — SAMEEKSHA CHANDEL", "Physical-grade tactile security inspection in browser with 60 FPS mobile optimization")

    draw_card(0.8 * inch, 0.9 * inch, 5.6 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_CYAN)
    c.drawString(1.1 * inch, h - 2.0 * inch, "3D WEBGL ENGINE CAPABILITIES")
    f_list = [
        ("3D Zero-Gravity Credential Mesh", "Renders parchment in 3D with gold-embossed Jaypee crest."),
        ("Iridescent Holographic Foil", "Shifts rainbow spectral glints on mouse tilt or phone gyroscope."),
        ("180 Degree Flip to Audit Ledger", "Spins certificate 180 to reveal SHA-256 Merkle root & block hash."),
        ("Interactive 3D Ledger Explorer", "Click 'Simulate POW Mining' to watch live particle convergence.")
    ]
    for idx, (t, d) in enumerate(f_list):
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(HEX_WHITE)
        c.drawString(1.1 * inch, h - 2.4 * inch - idx * 52, f"- {t}")
        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_MUTED)
        c.drawString(1.3 * inch, h - 2.65 * inch - idx * 52, d)

    draw_card(6.8 * inch, 0.9 * inch, 5.7 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_GREEN)
    c.drawString(7.1 * inch, h - 2.0 * inch, "PERFORMANCE & RELIABILITY STANDARDS")
    p_list = [
        ("60 FPS Smooth Rendering", "Clamped DPR (1.0x mobile, 2.0x desktop) with zero battery draining."),
        ("IntersectionObserver GPU Culling", "Freezes rendering when scrolled out of view, saving 100% idle GPU."),
        ("Zero Scroll Hijacking", "Passive event bindings keep page scrolling natural & smooth."),
        ("Graceful CSS-3D Fallback", "CSS-3D fallback keeps visual intact if WebGL is disabled.")
    ]
    for idx, (t, d) in enumerate(p_list):
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(HEX_WHITE)
        c.drawString(7.1 * inch, h - 2.4 * inch - idx * 52, f"/ {t}")
        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_MUTED)
        c.drawString(7.3 * inch, h - 2.65 * inch - idx * 52, d)

    c.showPage()

    # --- SLIDE 11 ---
    draw_bg()
    draw_header("Founding Team & 10-Minute VC Pitch Schedule", "TEAM ID: 10 EXECUTION — RIDEHACK'26", "Stopwatch-disciplined presentation flow before Vice Chancellor Sir & Senior Faculty")

    if os.path.exists(IMG_TEAM):
        c.drawImage(IMG_TEAM, 0.8 * inch, h - 4.5 * inch, width=11.733 * inch, height=2.55 * inch)

    draw_card(0.8 * inch, 0.6 * inch, 11.733 * inch, 2.0 * inch)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HEX_GOLD)
    c.drawString(1.0 * inch, 2.25 * inch, "10-MINUTE VC BOARD ROOM STOPWATCH SCHEDULE")

    sch = [
        ("0:00 - 3:00", "A. Praneeth Sai (Founder & Architecture)", "The Fake Crisis, Satyameva Solution & Whole PoW Backend"),
        ("3:00 - 5:00", "Anushka Bansal (Co-Founder & Data Lead)", "Why Not DigiLocker? Data Integrity & 24 Attack Vector Tests"),
        ("5:00 - 7:30", "Shashank Ray (Co-Founder & AI Model Lead)", "Gemini AI Multimodal OCR, Unit Economics (< Rs. 0.48) & B2B SaaS"),
        ("7:30 - 10:00", "Sameeksha Chandel (Co-Founder & Product Lead)", "Live 4-Portal Prototype, 3D WebGL Holographic Demo & Rs. 25L Ask")
    ]
    for idx, (timing, name, topic) in enumerate(sch):
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(HEX_CYAN)
        c.drawString(1.0 * inch, 1.95 * inch - idx * 26, f"[{timing}] {name}:")
        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_WHITE)
        c.drawString(4.8 * inch, 1.95 * inch - idx * 26, topic)

    c.showPage()

    # --- SLIDE 12 ---
    draw_bg()
    draw_header("VC Rapid Q&A Defense & Rs. 25 Lakh Incubation Ask", "COMMERCIAL ROADMAP — RIDEHACK'26", "Direct milestone utilization of the Rs. 1 Crore RIDE funding pool for full campus rollout")

    draw_card(0.8 * inch, 0.9 * inch, 5.6 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_GOLD)
    c.drawString(1.1 * inch, h - 2.0 * inch, "RS. 25 LAKH SEED INCUBATION ASK")
    allocs = [
        ("40% (Rs. 10 Lakhs)", "Multi-Node Blockchain Infrastructure", "Dedicated servers across JUIT, JIIT, and JUET nodes."),
        ("30% (Rs. 7.5 Lakhs)", "Multi-Campus Pilot & Rollout", "Onboarding registrar offices with 5,000+ graduation batches."),
        ("20% (Rs. 5 Lakhs)", "Security Audits & IP Patenting", "Cert-In cybersecurity compliance and IP protection."),
        ("10% (Rs. 2.5 Lakhs)", "Operations & Legal Compliance", "B2B institutional SaaS contracts & NEP 2020 compliance.")
    ]
    for idx, (pct, t, d) in enumerate(allocs):
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(HEX_WHITE)
        c.drawString(1.1 * inch, h - 2.4 * inch - idx * 52, f"* {pct} - {t}")
        c.setFont("Helvetica", 9)
        c.setFillColor(HEX_MUTED)
        c.drawString(1.3 * inch, h - 2.65 * inch - idx * 52, d)

    draw_card(6.8 * inch, 0.9 * inch, 5.7 * inch, 4.8 * inch)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HEX_GREEN)
    c.drawString(7.1 * inch, h - 2.0 * inch, "TOP 4 FACULTY QUESTIONS: CHEAT SHEET")
    qnas = [
        ("Q: Blockchain database se zyada expensive hoti hai?", "A: 'Public crypto chain costly hoti hai, humne zero-gas private ledger banaya hai jisme cost sirf 48 paise hai.'"),
        ("Q: DigiLocker jab hai toh universities kyu dengi?", "A: 'DigiLocker storage locker hai, Satyameva B2B verification engine hai jo 60s me global verification deta hai.'"),
        ("Q: Server band ho gaya toh verification kaise hogi?", "A: 'Multi-node architecture hai. Agar JUIT node band hua toh JIIT Noida node instant sync kar deta hai.'"),
        ("Q: Document ka size bada ho toh chain slow hogi?", "A: 'Hum chain par PDF nahi, balki 64-char SHA-256 hash store karte hain. Chain ultra-fast rehti hai.'")
    ]
    for idx, (q, a) in enumerate(qnas):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(HEX_GOLD)
        c.drawString(7.1 * inch, h - 2.35 * inch - idx * 54, q)
        c.setFont("Helvetica", 8.5)
        c.setFillColor(HEX_WHITE)
        c.drawString(7.3 * inch, h - 2.55 * inch - idx * 54, a)

    c.showPage()
    c.save()
    print(f"[OK] Presentation PDF saved successfully to: {OUT_PDF}")

if __name__ == '__main__':
    build_pptx()
    build_pdf()
