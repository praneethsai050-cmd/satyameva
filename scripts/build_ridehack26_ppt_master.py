"""
scripts/build_ridehack26_ppt_master.py
Generates the complete 8-slide RIDEHACK'26 Grand Finale Pitch Deck
using the ppt-master toolkit and python-pptx engine.
Strictly covers all 7 mandatory points specified by the organizers.
"""

import os
import sys
import shutil
import subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, "projects", "ridehack26_satyameva_ppt169_20261028")
SVG_OUTPUT_DIR = os.path.join(PROJECT_DIR, "svg_output")
NOTES_DIR = os.path.join(PROJECT_DIR, "notes")
IMAGES_DIR = os.path.join(PROJECT_DIR, "images")
EXPORTS_DIR = os.path.join(PROJECT_DIR, "exports")

os.makedirs(SVG_OUTPUT_DIR, exist_ok=True)
os.makedirs(NOTES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
for old_f in os.listdir(SVG_OUTPUT_DIR):
    if old_f.endswith(".svg"):
        try:
            os.remove(os.path.join(SVG_OUTPUT_DIR, old_f))
        except Exception:
            pass

# Copy asset images
for asset_name in ["arr_growth_bar_chart.png", "ask_pie_chart.png", "cogs_donut_chart.png"]:
    src = os.path.join(BASE_DIR, "assets", asset_name)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(IMAGES_DIR, asset_name))

for logo_name in ["juit.png", "jiit.png", "juet.png"]:
    src = os.path.join(BASE_DIR, "static", "img", "campuses", logo_name)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(IMAGES_DIR, logo_name))

print("[1/3] Assets synced to ppt-master workspace.")

# Author 8 Professional SVG Slides (1280x720)
slides_svg = {}
notes_content = {}

# -------------------------------------------------------------
# SLIDE 1: Cover & Founding Team
# -------------------------------------------------------------
slides_svg["01_cover.svg"] = """<svg xmlns="http://www.w3.org/2000/svg" lang="en" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060810"/>
      <stop offset="50%" stop-color="#0a0f1d"/>
      <stop offset="100%" stop-color="#060810"/>
    </linearGradient>
    <linearGradient id="primaryGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10b981"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
  </defs>
  <rect width="1280" height="720" fill="url(#bg)"/>
  
  <!-- Subtle Grid Accent -->
  <line x1="60" y1="95" x2="1220" y2="95" stroke="#1e293b" stroke-width="1.5"/>
  <line x1="60" y1="655" x2="1220" y2="655" stroke="#1e293b" stroke-width="1.5"/>

  <!-- Top Pill -->
  <rect x="60" y="42" width="670" height="34" rx="17" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="75" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981" letter-spacing="1.5">JAYPEE UNIVERSITY OF INFORMATION TECHNOLOGY  ·  RIDEHACK'26 GRAND FINALE  ·  JIIT NOIDA</text>

  <!-- Title & Subtitle -->
  <text x="60" y="160" font-family="Segoe UI, Inter, sans-serif" font-size="54" font-weight="900" fill="#ffffff" letter-spacing="-1">SATYAMEVA <tspan fill="url(#primaryGrad)">AEGIS</tspan></text>
  <text x="60" y="196" font-family="Segoe UI, Inter, sans-serif" font-size="20" font-weight="700" fill="#38bdf8">Decentralized Academic Credential Integrity &amp; Instant Verification Engine</text>
  <text x="60" y="226" font-family="Segoe UI, Inter, sans-serif" font-size="14" fill="#94a3b8">Eradicating Indian academic credential counterfeiting by compressing verification from 21 days down to 60 seconds.</text>
  <text x="60" y="246" font-family="Segoe UI, Inter, sans-serif" font-size="14" fill="#94a3b8">Zero Gas Fees  ·  Google Gemini 2.0 Flash AI OCR  ·  AES-256 PDF Stamping  ·  3D WebGL Holographic Proofs</text>

  <!-- Key Metrics Row -->
  <g transform="translate(60, 275)">
    <rect x="0" y="0" width="275" height="90" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="18" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#64748b" letter-spacing="1">TURNAROUND TIME</text>
    <text x="18" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="24" font-weight="bold" fill="#10b981">14–21 Days ➔ &lt;60s</text>
    <text x="18" y="80" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">99.9% clerical inquiry reduction</text>

    <rect x="295" y="0" width="275" height="90" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="313" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#64748b" letter-spacing="1">UNIT COST (COGS)</text>
    <text x="313" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="24" font-weight="bold" fill="#38bdf8">&lt; ₹0.48 / Credential</text>
    <text x="313" y="80" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">Gross Margin &gt; 90% per doc</text>

    <rect x="590" y="0" width="275" height="90" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="608" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#64748b" letter-spacing="1">BLOCKCHAIN CONSENSUS</text>
    <text x="608" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="24" font-weight="bold" fill="#f59e0b">100% Zero Gas Fees</text>
    <text x="608" y="80" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">Private PoW immune to crypto volatility</text>

    <rect x="885" y="0" width="275" height="90" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="903" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#64748b" letter-spacing="1">TOTAL MARKET SCOPE</text>
    <text x="903" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="24" font-weight="bold" fill="#ec4899">1,100+ Universities</text>
    <text x="903" y="80" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">40 Million Higher Ed Students in India</text>
  </g>

  <!-- Team Section Title -->
  <text x="60" y="415" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#10b981" letter-spacing="1.5">CORE FOUNDING TEAM  ·  TEAM ID: 10 (JUIT WAKNAGHAT)</text>

  <!-- 4 Team Member Cards -->
  <g transform="translate(60, 430)">
    <rect x="0" y="0" width="275" height="195" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="18" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="17" font-weight="bold" fill="#ffffff">A. Praneeth Sai</text>
    <text x="18" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#10b981">FOUNDER &amp; ARCHITECTURE LEAD</text>
    <text x="18" y="74" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#cbd5e1">B.Tech CSE Core (2026–2030)</text>
    <text x="18" y="92" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#64748b">JUIT Waknaghat</text>
    <line x1="18" y1="106" x2="257" y2="106" stroke="#1e293b" stroke-width="1"/>
    <text x="18" y="128" font-family="Segoe UI, Inter, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8">CORE DOMAINS:</text>
    <text x="18" y="146" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Zero-Gas Private Blockchain</text>
    <text x="18" y="164" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• SHA-256 Merkle Ledger Sync</text>
    <text x="18" y="182" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Full-Stack System Security</text>

    <rect x="295" y="0" width="275" height="195" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="313" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="17" font-weight="bold" fill="#ffffff">Anushka Bansal</text>
    <text x="313" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#06b6d4">CO-FOUNDER &amp; DATA LEAD</text>
    <text x="313" y="74" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#cbd5e1">B.Tech CSE Core (2026–2030)</text>
    <text x="313" y="92" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#64748b">JUIT Waknaghat</text>
    <line x1="313" y1="106" x2="552" y2="106" stroke="#1e293b" stroke-width="1"/>
    <text x="313" y="128" font-family="Segoe UI, Inter, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8">CORE DOMAINS:</text>
    <text x="313" y="146" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Academic Record Data Schema</text>
    <text x="313" y="164" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Database Integrity &amp; Audit Logs</text>
    <text x="313" y="182" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Institutional Workflow Mapping</text>

    <rect x="590" y="0" width="275" height="195" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="608" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="17" font-weight="bold" fill="#ffffff">Shashank Ray</text>
    <text x="608" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#a855f7">CO-FOUNDER &amp; AI MODEL LEAD</text>
    <text x="608" y="74" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#cbd5e1">B.Tech CSE Core (2026–2030)</text>
    <text x="608" y="92" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#64748b">JUIT Waknaghat</text>
    <line x1="608" y1="106" x2="847" y2="106" stroke="#1e293b" stroke-width="1"/>
    <text x="608" y="128" font-family="Segoe UI, Inter, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8">CORE DOMAINS:</text>
    <text x="608" y="146" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Gemini 2.0 Flash Vision Pipeline</text>
    <text x="608" y="164" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Multimodal Certificate Parsing</text>
    <text x="608" y="182" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Tamper &amp; Pixel Anomaly Detection</text>

    <rect x="885" y="0" width="275" height="195" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="903" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="17" font-weight="bold" fill="#ffffff">Sameeksha Chandel</text>
    <text x="903" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#f59e0b">CO-FOUNDER &amp; PRODUCT LEAD</text>
    <text x="903" y="74" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#cbd5e1">B.Tech CSE Core (2026–2030)</text>
    <text x="903" y="92" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#64748b">JUIT Waknaghat</text>
    <line x1="903" y1="106" x2="1142" y2="106" stroke="#1e293b" stroke-width="1"/>
    <text x="903" y="128" font-family="Segoe UI, Inter, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8">CORE DOMAINS:</text>
    <text x="903" y="146" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Student &amp; Verifier UI/UX</text>
    <text x="903" y="164" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• BGV Enterprise Integrations</text>
    <text x="903" y="182" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">• Product Lifecycle &amp; Compliance</text>
  </g>

  <!-- Footer -->
  <text x="60" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#64748b">Tech Incubation: Dept. of CSE, JUIT Waknaghat  ·  Pilot Deployment: JUIT · JIIT · JUET Campuses</text>
  <text x="1220" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#10b981" text-anchor="end">SLIDE 01 / 08</text>
</svg>"""

notes_content["01_cover.md"] = """# Slide 1: Cover & Founding Team (Speaking Script)
**Speaker: A. Praneeth Sai (Founder & Architecture Lead)**
- Respected judges and distinguished evaluators at RIDEHACK'26 Grand Finale at JIIT Noida.
- We represent Team 10 from Jaypee University of Information Technology, Waknaghat.
- I am A. Praneeth Sai, joined by co-founders Anushka Bansal, Shashank Ray, and Sameeksha Chandel.
- Today, we present **Satyameva Aegis**: India's first decentralized academic credential integrity engine.
- We compress verification from 21 days down to 60 seconds with Zero Gas Fees, Google Gemini AI OCR, and 3D Holographic Proofs.
"""

# -------------------------------------------------------------
# SLIDE 2: Problem Statement
# -------------------------------------------------------------
slides_svg["02_problem_statement.svg"] = """<svg xmlns="http://www.w3.org/2000/svg" lang="en" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#060810"/>
  <line x1="60" y1="95" x2="1220" y2="95" stroke="#1e293b" stroke-width="1.5"/>
  <line x1="60" y1="655" x2="1220" y2="655" stroke="#1e293b" stroke-width="1.5"/>

  <!-- Top Pill -->
  <rect x="60" y="42" width="360" height="34" rx="17" fill="#0f172a" stroke="#ef4444" stroke-width="1.5"/>
  <text x="75" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#ef4444" letter-spacing="1.5">MANDATORY POINT 1  ·  PROBLEM STATEMENT</text>

  <!-- Title -->
  <text x="60" y="150" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#ffffff">The Crisis in Indian Higher Education: Counterfeits &amp; Delays</text>
  <text x="60" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="16" fill="#94a3b8">Critical Pain Point: Paper degrees and centralized PDFs have zero intrinsic origin proof.</text>

  <!-- 3 Problem Cards -->
  <g transform="translate(60, 210)">
    <!-- Card 1 -->
    <rect x="0" y="0" width="365" height="410" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <rect x="24" y="24" width="46" height="46" rx="23" fill="#ef4444" fill-opacity="0.15"/>
    <text x="47" y="54" font-family="Segoe UI, Inter, sans-serif" font-size="20" font-weight="bold" fill="#ef4444" text-anchor="middle">1</text>
    <text x="82" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="18" font-weight="bold" fill="#ffffff">₹1,500 Fake Degree</text>
    <text x="82" y="70" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#ef4444">Telegram &amp; Darknet Syndicates</text>

    <text x="24" y="115" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#38bdf8">Over 40,000 Fake Degrees</text>
    <text x="24" y="138" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">officially detected across India annually.</text>
    <text x="24" y="168" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#94a3b8">Syndicates sell high-precision replica marksheets with duplicate embossing, holographic foils, and university seals in 24 hours.</text>
    <text x="24" y="235" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#94a3b8">Corporate HR teams cannot distinguish fraudulent paper ink from authentic diplomas without slow institutional inquiries.</text>

    <rect x="24" y="325" width="317" height="60" rx="8" fill="#18181b" stroke="#27272a" stroke-width="1"/>
    <text x="38" y="350" font-family="Segoe UI, Inter, sans-serif" font-size="11" font-weight="bold" fill="#ef4444">IMPACT ON REPUTATION</text>
    <text x="38" y="370" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#ffffff">Erodes employer trust in legitimate Indian graduates.</text>

    <!-- Card 2 -->
    <rect x="395" y="0" width="365" height="410" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <rect x="419" y="24" width="46" height="46" rx="23" fill="#f59e0b" fill-opacity="0.15"/>
    <text x="442" y="54" font-family="Segoe UI, Inter, sans-serif" font-size="20" font-weight="bold" fill="#f59e0b" text-anchor="middle">2</text>
    <text x="477" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="18" font-weight="bold" fill="#ffffff">14–21 Day Verification</text>
    <text x="477" y="70" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#f59e0b">Administrative Bottlenecks</text>

    <text x="419" y="115" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#38bdf8">Severe Hiring &amp; Visa Friction</text>
    <text x="419" y="138" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">BGV agencies (TCS, Wipro, AuthBridge)</text>
    <text x="419" y="168" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#94a3b8">rely on manual email chains, physical courier transcripts, and overloaded registrar back-offices.</text>
    <text x="419" y="235" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#94a3b8">This manual burden costs an average university ₹12–18 Lakhs annually in clerical overhead while graduates lose global opportunities.</text>

    <rect x="419" y="325" width="317" height="60" rx="8" fill="#18181b" stroke="#27272a" stroke-width="1"/>
    <text x="433" y="350" font-family="Segoe UI, Inter, sans-serif" font-size="11" font-weight="bold" fill="#f59e0b">ADMINISTRATIVE DRAIN</text>
    <text x="433" y="370" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#ffffff">Over 4,000 manual verification emails/month/HEI.</text>

    <!-- Card 3 -->
    <rect x="790" y="0" width="370" height="410" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <rect x="814" y="24" width="46" height="46" rx="23" fill="#a855f7" fill-opacity="0.15"/>
    <text x="837" y="54" font-family="Segoe UI, Inter, sans-serif" font-size="20" font-weight="bold" fill="#a855f7" text-anchor="middle">3</text>
    <text x="872" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="18" font-weight="bold" fill="#ffffff">Centralized SQL Failures</text>
    <text x="872" y="70" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#a855f7">Single Point of Insider Tampering</text>

    <text x="814" y="115" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#38bdf8">Zero Mathematical Auditability</text>
    <text x="814" y="138" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">Relational databases lack immutable history.</text>
    <text x="814" y="168" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#94a3b8">A single compromised database administrator credential or insider access allows executing `UPDATE students SET cgpa=9.8` silently.</text>
    <text x="814" y="235" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#94a3b8">Traditional SQL databases provide no cryptographic proofs or Merkle history to detect retroactive database alterations.</text>

    <rect x="814" y="325" width="322" height="60" rx="8" fill="#18181b" stroke="#27272a" stroke-width="1"/>
    <text x="828" y="350" font-family="Segoe UI, Inter, sans-serif" font-size="11" font-weight="bold" fill="#a855f7">SECURITY VULNERABILITY</text>
    <text x="828" y="370" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#ffffff">Insider attacks go completely undetected forever.</text>
  </g>

  <!-- Footer -->
  <text x="60" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#64748b">Satyameva Aegis  ·  The Root Problem in Indian Academia</text>
  <text x="1220" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#ef4444" text-anchor="end">SLIDE 02 / 08</text>
</svg>"""

notes_content["02_problem_statement.md"] = """# Slide 2: Problem Statement (Speaking Script)
**Speaker: Anushka Bansal (Co-Founder & Data Lead)**
- The crisis in Indian Higher Education has three devastating dimensions:
1. Fake degrees are obtainable on Telegram for as little as ₹1,500 with duplicated holographic seals.
2. Background screening delays average 14–21 days, dragging down hiring pipelines and costing universities ₹12–18 Lakhs annually.
3. Centralized university databases have a single point of failure: an insider with SQL access can modify marks silently with zero tamper trail.
- We need an institutional cryptographic trust layer that acts at the origin.
"""

# -------------------------------------------------------------
# SLIDE 3: Proposed Solution
# -------------------------------------------------------------
slides_svg["03_proposed_solution.svg"] = """<svg xmlns="http://www.w3.org/2000/svg" lang="en" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="primaryGrad3" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10b981"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
  </defs>
  <rect width="1280" height="720" fill="#060810"/>
  <line x1="60" y1="95" x2="1220" y2="95" stroke="#1e293b" stroke-width="1.5"/>
  <line x1="60" y1="655" x2="1220" y2="655" stroke="#1e293b" stroke-width="1.5"/>

  <!-- Top Pill -->
  <rect x="60" y="42" width="410" height="34" rx="17" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="75" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981" letter-spacing="1.5">MANDATORY POINT 2  ·  PROPOSED SOLUTION &amp; LIVE UI</text>

  <!-- Title -->
  <text x="60" y="150" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#ffffff">4-Pillar Deep-Tech Architecture &amp; <tspan fill="url(#primaryGrad3)">Live Service Interface</tspan></text>
  <text x="60" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="15" fill="#94a3b8">Working deployment: SQLite + JSON ledger parity (0.04s) · Production UI active at JUIT Waknaghat.</text>

  <!-- Left Column: 4 Architecture Pillars (Stacked) -->
  <g transform="translate(60, 205)">
    <!-- Pillar 1 -->
    <rect x="0" y="0" width="570" height="100" rx="10" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
    <rect x="14" y="14" width="28" height="28" rx="6" fill="#064e3b"/>
    <text x="28" y="33" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#34d399" text-anchor="middle">1</text>
    <text x="52" y="33" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#10b981">ZERO-GAS PROOF-OF-WORK BLOCKCHAIN</text>
    <text x="52" y="55" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#cbd5e1">Consensus D=4  ·  SQLite + blockchain.json dual-persistence parity in 0.04s.</text>
    <text x="52" y="75" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">Zero gas fees, zero cryptocurrency exposure, automated peer rollback on tampering.</text>
    <rect x="445" y="12" width="112" height="22" rx="4" fill="#064e3b"/>
    <text x="501" y="27" font-family="Segoe UI, Inter, sans-serif" font-size="10" font-weight="bold" fill="#34d399" text-anchor="middle">ZERO GAS FEES</text>

    <!-- Pillar 2 -->
    <rect x="0" y="112" width="570" height="100" rx="10" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
    <rect x="14" y="126" width="28" height="28" rx="6" fill="#0c4a6e"/>
    <text x="28" y="145" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#38bdf8" text-anchor="middle">2</text>
    <text x="52" y="145" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#38bdf8">MULTIMODAL GEMINI 2.0 FLASH AI OCR</text>
    <text x="52" y="167" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#cbd5e1">Vision parsing in 1.8s directly from marksheet scans and phone photos.</text>
    <text x="52" y="187" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">Extracts Roll, Degree, CGPA &amp; DOB; auto-cascades to 2.5-flash for 99.99% uptime.</text>
    <rect x="445" y="124" width="112" height="22" rx="4" fill="#0c4a6e"/>
    <text x="501" y="139" font-family="Segoe UI, Inter, sans-serif" font-size="10" font-weight="bold" fill="#38bdf8" text-anchor="middle">1.8s AI PARSE</text>

    <!-- Pillar 3 -->
    <rect x="0" y="224" width="570" height="100" rx="10" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
    <rect x="14" y="238" width="28" height="28" rx="6" fill="#78350f"/>
    <text x="28" y="257" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#fbbf24" text-anchor="middle">3</text>
    <text x="52" y="257" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#f59e0b">DYNAMIC 60-SEC QR &amp; AES-256 ENCRYPTED PDF</text>
    <text x="52" y="279" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#cbd5e1">Anti-screenshot token protocol: HMAC-salted QR code cycles every 60s.</text>
    <text x="52" y="299" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">Official stamped PDF locked via 256-bit AES encryption using Student DOB.</text>
    <rect x="445" y="236" width="112" height="22" rx="4" fill="#78350f"/>
    <text x="501" y="251" font-family="Segoe UI, Inter, sans-serif" font-size="10" font-weight="bold" fill="#fbbf24" text-anchor="middle">SCREENSHOT PROOF</text>

    <!-- Pillar 4 -->
    <rect x="0" y="336" width="570" height="100" rx="10" fill="#0f172a" stroke="#ec4899" stroke-width="1.5"/>
    <rect x="14" y="350" width="28" height="28" rx="6" fill="#831843"/>
    <text x="28" y="369" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#f472b6" text-anchor="middle">4</text>
    <text x="52" y="369" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#ec4899">3D WEBGL HOLOGRAPHIC INSPECTOR</text>
    <text x="52" y="391" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#cbd5e1">In-browser Three.js holographic parchment with specular gold foil reflection.</text>
    <text x="52" y="411" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#94a3b8">180° 3D card flip exposes block index, previous hash, and Merkle root in real-time.</text>
    <rect x="445" y="348" width="112" height="22" rx="4" fill="#831843"/>
    <text x="501" y="363" font-family="Segoe UI, Inter, sans-serif" font-size="10" font-weight="bold" fill="#f472b6" text-anchor="middle">3D HASH FLIP</text>
  </g>

  <!-- Right Column: Live Production UI Reference Frames -->
  <g transform="translate(660, 205)">
    <!-- Frame 1: Student 3D Document Wallet -->
    <rect x="0" y="0" width="560" height="210" rx="10" fill="#0b1120" stroke="#38bdf8" stroke-width="1.5"/>
    <!-- Chrome Header -->
    <rect x="0" y="0" width="560" height="28" rx="10" fill="#1e293b"/>
    <circle cx="16" cy="14" r="4.5" fill="#ef4444"/>
    <circle cx="28" cy="14" r="4.5" fill="#f59e0b"/>
    <circle cx="40" cy="14" r="4.5" fill="#10b981"/>
    <text x="55" y="18" font-family="Segoe UI, Inter, sans-serif" font-size="10.5" font-weight="bold" fill="#94a3b8">satyameva.in/student/document/1  ·  3D Holographic Wallet &amp; Dynamic QR</text>
    <rect x="460" y="5" width="90" height="18" rx="9" fill="#0c4a6e"/>
    <text x="505" y="17" font-family="Segoe UI, Inter, sans-serif" font-size="9" font-weight="bold" fill="#38bdf8" text-anchor="middle">STUDENT PORTAL</text>

    <!-- Frame 2: Public Verifier Terminal -->
    <rect x="0" y="226" width="560" height="210" rx="10" fill="#0b1120" stroke="#10b981" stroke-width="1.5"/>
    <!-- Chrome Header -->
    <rect x="0" y="226" width="560" height="28" rx="10" fill="#1e293b"/>
    <circle cx="16" cy="240" r="4.5" fill="#ef4444"/>
    <circle cx="28" cy="240" r="4.5" fill="#f59e0b"/>
    <circle cx="40" cy="240" r="4.5" fill="#10b981"/>
    <text x="55" y="244" font-family="Segoe UI, Inter, sans-serif" font-size="10.5" font-weight="bold" fill="#94a3b8">satyameva.in/verify  ·  Instant Zero-Login Verification Terminal (&lt;5s)</text>
    <rect x="460" y="231" width="90" height="18" rx="9" fill="#064e3b"/>
    <text x="505" y="243" font-family="Segoe UI, Inter, sans-serif" font-size="9" font-weight="bold" fill="#34d399" text-anchor="middle">PUBLIC VERIFIER</text>
  </g>

  <!-- Footer -->
  <text x="60" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#64748b">Satyameva Aegis  ·  End-to-End Architecture &amp; Production Service Interfaces</text>
  <text x="1220" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#10b981" text-anchor="end">SLIDE 03 / 08</text>
</svg>"""

notes_content["03_proposed_solution.md"] = """# Slide 3: Proposed Solution (Speaking Script)
**Speaker: Shashank Ray (Co-Founder & AI Model Lead)**
- Satyameva Aegis integrates 4 deep-tech pillars directly with a production-ready interface:
1. **Zero-Gas PoW Blockchain**: Dual-persistence parity between relational SQLite and immutable ledger in 0.04s.
2. **Gemini 2.0 Flash Vision AI**: Extracts marksheet fields directly into JSON in 1.8s.
3. **Dynamic 60s Salted QR & Encrypted PDF**: Time-boxed tokens prevent screenshot forgery, locked via DOB.
4. **3D Holographic Proofs**: Recruiter inspects foil and flips 180° to audit block hash in real-time.
- On the right, you see our live deployed web application currently operational at JUIT Waknaghat.
"""

# -------------------------------------------------------------
# SLIDE 4: Unique Value Proposition (vs DigiLocker)
# -------------------------------------------------------------
slides_svg["04_unique_value_proposition.svg"] = """<svg xmlns="http://www.w3.org/2000/svg" lang="en" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#060810"/>
  <line x1="60" y1="95" x2="1220" y2="95" stroke="#1e293b" stroke-width="1.5"/>
  <line x1="60" y1="655" x2="1220" y2="655" stroke="#1e293b" stroke-width="1.5"/>

  <!-- Top Pill -->
  <rect x="60" y="42" width="410" height="34" rx="17" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="75" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8" letter-spacing="1.5">MANDATORY POINT 3  ·  UNIQUE VALUE PROPOSITION</text>

  <!-- Title -->
  <text x="60" y="150" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#ffffff">Strategic Differentiation: Why Not DigiLocker?</text>
  <text x="60" y="178" font-family="Segoe UI, Inter, sans-serif" font-size="15" fill="#10b981">VC Metaphor: "DigiLocker is a citizen storage cupboard. Satyameva is the biometric lock, digital seal, and origin proof."</text>

  <!-- Comparison Table Container -->
  <g transform="translate(60, 200)">
    <rect x="0" y="0" width="1160" height="370" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>

    <!-- Table Header Row -->
    <rect x="0" y="0" width="1160" height="48" rx="14" fill="#1e293b"/>
    <text x="24" y="30" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#94a3b8">EVALUATION CRITERIA</text>
    <text x="360" y="30" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#ef4444">GOVERNMENT DIGILOCKER (C2C)</text>
    <text x="760" y="30" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981">SATYAMEVA AEGIS (OUR B2B SOLUTION)</text>

    <!-- Row 1: Role -->
    <line x1="0" y1="48" x2="1160" y2="48" stroke="#334155" stroke-width="1"/>
    <text x="24" y="80" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" font-weight="bold" fill="#ffffff">Architecture &amp; Role</text>
    <text x="360" y="80" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">Citizen Storage Locker (C2C cloud repository)</text>
    <text x="760" y="80" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#34d399">Institutional Security &amp; Verification Engine (B2B SaaS)</text>

    <!-- Row 2: Speed -->
    <line x1="0" y1="102" x2="1160" y2="102" stroke="#334155" stroke-width="1"/>
    <text x="24" y="134" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" font-weight="bold" fill="#ffffff">Verification Speed</text>
    <text x="360" y="134" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#ef4444">Manual download &amp; inspection (14–21 days)</text>
    <text x="760" y="134" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">Instant in under 60 seconds (Automated Engine)</text>

    <!-- Row 3: Global Access -->
    <line x1="0" y1="156" x2="1160" y2="156" stroke="#334155" stroke-width="1"/>
    <text x="24" y="188" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" font-weight="bold" fill="#ffffff">Global Recruiter Access</text>
    <text x="360" y="188" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#ef4444">FAILS: Requires Indian Aadhaar &amp; active OTP</text>
    <text x="760" y="188" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#34d399">FRICTIONLESS: Global recruiters verify in 60s without login</text>

    <!-- Row 4: University Telemetry -->
    <line x1="0" y1="210" x2="1160" y2="210" stroke="#334155" stroke-width="1"/>
    <text x="24" y="242" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" font-weight="bold" fill="#ffffff">Institutional B2B Console</text>
    <text x="360" y="242" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#ef4444">Zero university telemetry or fraud analytics</text>
    <text x="760" y="242" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#34d399">Full governance console: fraud tracking &amp; license control</text>

    <!-- Row 5: Physical Print -->
    <line x1="0" y1="264" x2="1160" y2="264" stroke="#334155" stroke-width="1"/>
    <text x="24" y="296" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" font-weight="bold" fill="#ffffff">Physical Print Security</text>
    <text x="360" y="296" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#ef4444">Printed PDF loses all security features</text>
    <text x="760" y="296" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">Permanent institutional QR + AES-256 DOB password</text>

    <!-- Row 6: Relationship -->
    <line x1="0" y1="318" x2="1160" y2="318" stroke="#334155" stroke-width="1"/>
    <text x="24" y="350" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" font-weight="bold" fill="#ffffff">Strategic Alignment</text>
    <text x="360" y="350" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">Generic cloud document repository</text>
    <text x="760" y="350" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981">Complementary origin protocol: feeds data into DigiLocker &amp; ABC</text>
  </g>

  <!-- Forensic Security Benchmarks Pill -->
  <g transform="translate(60, 590)">
    <rect x="0" y="0" width="1160" height="46" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="1"/>
    <text x="24" y="28" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981">FORENSIC SECURITY BENCHMARKS (24/24 PASSED):</text>
    <text x="410" y="28" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#ffffff">Tamper Detection: 0.04s (40 ms)</text>
    <text x="660" y="28" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#ffffff">False Positive Rate: Absolute 0.0%</text>
    <text x="940" y="28" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#ffffff">PBKDF2 Salt Collisions: 0/50</text>
  </g>

  <!-- Footer -->
  <text x="60" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#64748b">Satyameva Aegis  ·  Co-existing and Empowering National Infrastructure</text>
  <text x="1220" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#38bdf8" text-anchor="end">SLIDE 04 / 08</text>
</svg>"""

notes_content["04_unique_value_proposition.md"] = """# Slide 4: Unique Value Proposition (Speaking Script)
**Speaker: Sameeksha Chandel (Co-Founder & Product Lead)**
- A common investor question: 'Doesn't DigiLocker already exist?'
- We clarify: DigiLocker is a citizen document locker. Satyameva is the cryptographic seal and origin verification protocol that guarantees what goes inside that locker is authentic.
- DigiLocker requires Indian Aadhaar OTP—foreign employers and embassies cannot use it. Satyameva allows zero-login instant verification worldwide.
- DigiLocker offers zero telemetry to universities; Satyameva provides a complete B2B fraud analytics and governance dashboard.
"""

# -------------------------------------------------------------
# SLIDE 5: Market Opportunity (TAM / SAM / SOM)
# -------------------------------------------------------------
slides_svg["05_market_opportunity.svg"] = """<svg xmlns="http://www.w3.org/2000/svg" lang="en" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#060810"/>
  <line x1="60" y1="95" x2="1220" y2="95" stroke="#1e293b" stroke-width="1.5"/>
  <line x1="60" y1="655" x2="1220" y2="655" stroke="#1e293b" stroke-width="1.5"/>

  <!-- Top Pill -->
  <rect x="60" y="42" width="400" height="34" rx="17" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="75" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981" letter-spacing="1.5">MANDATORY POINT 4  ·  MARKET OPPORTUNITY</text>

  <!-- Title -->
  <text x="60" y="150" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#ffffff">Market Sizing: Capturing India's ₹2,400 Cr Verification Market</text>
  <text x="60" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="16" fill="#94a3b8">Higher Education Institutions (HEIs) issuing 1.5 Crore credentials annually with 14.5% BGV CAGR.</text>

  <!-- TAM / SAM / SOM 3 Columns -->
  <g transform="translate(60, 210)">
    <!-- TAM -->
    <rect x="0" y="0" width="365" height="300" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <rect x="24" y="24" width="85" height="30" rx="6" fill="#0369a1"/>
    <text x="66" y="44" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">TAM</text>
    <text x="24" y="90" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#38bdf8">₹2,400+ CR</text>
    <text x="24" y="112" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#94a3b8">TOTAL ADDRESSABLE MARKET</text>
    <line x1="24" y1="128" x2="341" y2="128" stroke="#1e293b" stroke-width="1"/>
    <text x="24" y="155" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• 1,100+ Recognized Indian Universities</text>
    <text x="24" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• 45,000+ Higher Education Colleges</text>
    <text x="24" y="205" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• 40 Million+ Enrolled Students in India</text>
    <text x="24" y="230" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• 1.5 Crore degrees &amp; diplomas issued/yr</text>
    <text x="24" y="255" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Corporate BGV growing at 14.5% CAGR</text>

    <!-- SAM -->
    <rect x="395" y="0" width="365" height="300" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <rect x="419" y="24" width="85" height="30" rx="6" fill="#047857"/>
    <text x="461" y="44" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">SAM</text>
    <text x="419" y="90" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#10b981">₹360 CR</text>
    <text x="419" y="112" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#94a3b8">SERVICEABLE ADDRESSABLE MARKET</text>
    <line x1="419" y1="128" x2="736" y2="128" stroke="#1e293b" stroke-width="1"/>
    <text x="419" y="155" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• 350+ Tier-1 &amp; Tier-2 Universities</text>
    <text x="419" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Private, Deemed &amp; State Tech HEIs</text>
    <text x="419" y="205" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• NEP 2020 DigiLocker/ABC Mandates</text>
    <text x="419" y="230" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• NAAC Criterion 2 digitization audits</text>
    <text x="419" y="255" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Active placement cells &amp; global alumni</text>

    <!-- SOM -->
    <rect x="790" y="0" width="370" height="300" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <rect x="814" y="24" width="85" height="30" rx="6" fill="#b45309"/>
    <text x="856" y="44" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">SOM</text>
    <text x="814" y="90" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#f59e0b">₹12 – 45 L</text>
    <text x="814" y="112" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#94a3b8">SERVICEABLE OBTAINABLE (Y1–Y2)</text>
    <line x1="814" y1="128" x2="1136" y2="128" stroke="#1e293b" stroke-width="1"/>
    <text x="814" y="155" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• 3 Jaypee Pilot Campuses (JUIT/JIIT/JUET)</text>
    <text x="814" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• 15,000+ active student records</text>
    <text x="814" y="205" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Year 2: Expand to 30 North India HEIs</text>
    <text x="814" y="230" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Direct pipeline via placement cell networks</text>
    <text x="814" y="255" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Breakeven achieved within 14 months</text>
  </g>

  <!-- Key Growth Tailwinds Row -->
  <g transform="translate(60, 530)">
    <rect x="0" y="0" width="365" height="105" rx="10" fill="#0f172a" stroke="#10b981" stroke-width="1"/>
    <text x="18" y="28" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981">1. REGULATORY MANDATES</text>
    <text x="18" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#cbd5e1">NEP 2020 &amp; UGC guidelines push verifiable, digital-first academic repositories.</text>

    <rect x="395" y="0" width="365" height="105" rx="10" fill="#0f172a" stroke="#38bdf8" stroke-width="1"/>
    <text x="413" y="28" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">2. CORPORATE BGV SURGE</text>
    <text x="413" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#cbd5e1">Over 50,000 bulk campus hires each placement season demand instant API verification.</text>

    <rect x="790" y="0" width="370" height="105" rx="10" fill="#0f172a" stroke="#f59e0b" stroke-width="1"/>
    <text x="808" y="28" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#f59e0b">3. GLOBAL SCHOLAR MOBILITY</text>
    <text x="808" y="52" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#cbd5e1">Foreign universities &amp; visa consulates reject paper photocopies without digital cryptographic seals.</text>
  </g>

  <!-- Footer -->
  <text x="60" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#64748b">Satyameva Aegis  ·  Indian EdTech &amp; BGV Market Size</text>
  <text x="1220" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#10b981" text-anchor="end">SLIDE 05 / 08</text>
</svg>"""

notes_content["05_market_opportunity.md"] = """# Slide 5: Market Opportunity (Speaking Script)
**Speaker: Anushka Bansal (Co-Founder & Data Lead)**
- India's higher education verification market stands at over ₹2,400 Crores with 1,100+ universities and 40 million students.
- Our Serviceable Addressable Market (SAM) is ₹360 Crores, targeting 350+ private and state technical universities with high campus placement volume.
- Our immediate Serviceable Obtainable Market (SOM) is ₹12 to ₹45 Lakhs in Years 1–2, starting with our 3 Jaypee campuses (JUIT, JIIT, JUET) with 15,000+ student records, expanding to 30 regional HEIs.
"""

# -------------------------------------------------------------
# SLIDE 6: Business Model & Unit Economics
# -------------------------------------------------------------
slides_svg["06_business_model.svg"] = """<svg xmlns="http://www.w3.org/2000/svg" lang="en" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#060810"/>
  <line x1="60" y1="95" x2="1220" y2="95" stroke="#1e293b" stroke-width="1.5"/>
  <line x1="60" y1="655" x2="1220" y2="655" stroke="#1e293b" stroke-width="1.5"/>

  <!-- Top Pill -->
  <rect x="60" y="42" width="370" height="34" rx="17" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="75" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981" letter-spacing="1.5">MANDATORY POINT 5  ·  BUSINESS MODEL</text>

  <!-- Title -->
  <text x="60" y="150" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#ffffff">B2B SaaS Licensing, Verification API &amp; &gt;90% Gross Margin</text>
  <text x="60" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="16" fill="#10b981">Ultra-lean unit economics: Total COGS is under ₹0.48 per credential issued.</text>

  <!-- 2 Revenue Streams Columns -->
  <g transform="translate(60, 210)">
    <!-- Stream 1 -->
    <rect x="0" y="0" width="565" height="300" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <rect x="24" y="24" width="160" height="28" rx="6" fill="#047857"/>
    <text x="104" y="43" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">ANNUAL UNIVERSITY SAAS</text>
    <text x="24" y="86" font-family="Segoe UI, Inter, sans-serif" font-size="30" font-weight="900" fill="#10b981">₹1.5 Lakhs <tspan font-size="16" font-weight="normal" fill="#94a3b8">/ campus / year</tspan></text>
    <line x1="24" y1="104" x2="541" y2="104" stroke="#1e293b" stroke-width="1"/>
    <text x="24" y="132" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" fill="#cbd5e1">• Bulk CSV Degree Issuance Portal with Gemini AI OCR</text>
    <text x="24" y="158" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" fill="#cbd5e1">• Self-Sovereign Student Wallets &amp; 60s Dynamic QR Codes</text>
    <text x="24" y="184" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" fill="#cbd5e1">• Superadmin Governance: Fraud analytics, license telemetry</text>
    <text x="24" y="210" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" fill="#cbd5e1">• Unlimited credential issuance &amp; registrar block mining</text>
    <rect x="24" y="238" width="517" height="42" rx="8" fill="#18181b"/>
    <text x="38" y="264" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981">INSTITUTIONAL ROI: <tspan fill="#ffffff" font-weight="normal">Saves ₹8–12 Lakhs in clerical costs (5x ROI).</tspan></text>

    <!-- Stream 2 -->
    <rect x="595" y="0" width="565" height="300" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <rect x="619" y="24" width="180" height="28" rx="6" fill="#0284c7"/>
    <text x="709" y="43" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">CORPORATE VERIFIER API</text>
    <text x="619" y="86" font-family="Segoe UI, Inter, sans-serif" font-size="30" font-weight="900" fill="#38bdf8">₹10 to ₹25 <tspan font-size="16" font-weight="normal" fill="#94a3b8">/ verification check</tspan></text>
    <line x1="619" y1="104" x2="1136" y2="104" stroke="#1e293b" stroke-width="1"/>
    <text x="619" y="132" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" fill="#cbd5e1">• B2B API access for screening agencies (AuthBridge, TCS, Wipro)</text>
    <text x="619" y="158" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" fill="#cbd5e1">• Instant cryptographic response in &lt;5s (eliminating 21-day delays)</text>
    <text x="619" y="184" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" fill="#cbd5e1">• High volume during campus hiring (50,000+ checks / enterprise)</text>
    <text x="619" y="210" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" fill="#cbd5e1">• Official tamper-proof verification audit PDF certificate export</text>
    <rect x="619" y="238" width="517" height="42" rx="8" fill="#18181b"/>
    <text x="633" y="264" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">ENTERPRISE BENEFIT: <tspan fill="#ffffff" font-weight="normal">Zero clerical burden for the host university.</tspan></text>
  </g>

  <!-- Unit Cost Breakdown Banner -->
  <g transform="translate(60, 530)">
    <rect x="0" y="0" width="1160" height="105" rx="14" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
    <text x="24" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#10b981">UNIT ECONOMICS BREAKDOWN (&lt; ₹0.48 / CREDENTIAL ISSUED  ·  &gt;90% GROSS MARGIN)</text>
    
    <g transform="translate(24, 48)">
      <rect x="0" y="0" width="205" height="42" rx="6" fill="#18181b"/>
      <text x="14" y="26" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#94a3b8">Gemini AI OCR: <tspan font-weight="bold" fill="#38bdf8">₹0.18 (38%)</tspan></text>

      <rect x="225" y="0" width="205" height="42" rx="6" fill="#18181b"/>
      <text x="239" y="26" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#94a3b8">Cloud Storage: <tspan font-weight="bold" fill="#10b981">₹0.15 (31%)</tspan></text>

      <rect x="450" y="0" width="205" height="42" rx="6" fill="#18181b"/>
      <text x="464" y="26" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#94a3b8">AES-256 PDF Stamp: <tspan font-weight="bold" fill="#f59e0b">₹0.06 (13%)</tspan></text>

      <rect x="675" y="0" width="205" height="42" rx="6" fill="#18181b"/>
      <text x="689" y="26" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#94a3b8">PoW CPU Node: <tspan font-weight="bold" fill="#a855f7">₹0.04 (8%)</tspan></text>

      <rect x="900" y="0" width="210" height="42" rx="6" fill="#18181b"/>
      <text x="914" y="26" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#94a3b8">Buffer / Reserve: <tspan font-weight="bold" fill="#cbd5e1">₹0.05 (10%)</tspan></text>
    </g>
  </g>

  <!-- Footer -->
  <text x="60" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#64748b">Satyameva Aegis  ·  Dual-Engine SaaS &amp; API Monetization</text>
  <text x="1220" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#10b981" text-anchor="end">SLIDE 06 / 08</text>
</svg>"""

notes_content["06_business_model.md"] = """# Slide 6: Business Model & Unit Economics (Speaking Script)
**Speaker: Sameeksha Chandel (Co-Founder & Product Lead)**
- Our business model has two high-margin revenue streams:
1. **Annual University SaaS**: ₹1.5 Lakhs per campus per year for unlimited issuance, Gemini AI OCR extraction, and the registrar governance portal. A 5x ROI for universities saving ₹8–12 Lakhs in clerical costs.
2. **Corporate Verification API**: ₹10 to ₹25 per check for BGV firms (AuthBridge, TCS, Wipro), returning verified cryptographic proof in under 5 seconds.
- Our total Cost of Goods Sold is less than ₹0.48 per credential, yielding a Gross Margin above 90% with zero cryptocurrency exposure.
"""

# -------------------------------------------------------------
# SLIDE 7: Financials & Seed Ask
# -------------------------------------------------------------
slides_svg["07_financials_and_seed_ask.svg"] = """<svg xmlns="http://www.w3.org/2000/svg" lang="en" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#060810"/>
  <line x1="60" y1="95" x2="1220" y2="95" stroke="#1e293b" stroke-width="1.5"/>
  <line x1="60" y1="655" x2="1220" y2="655" stroke="#1e293b" stroke-width="1.5"/>

  <!-- Top Pill -->
  <rect x="60" y="42" width="410" height="34" rx="17" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="75" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#f59e0b" letter-spacing="1.5">MANDATORY POINT 6  ·  FINANCIALS &amp; SEED ASK</text>

  <!-- Title -->
  <text x="60" y="150" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#ffffff">Financial Projections &amp; ₹25 Lakh Seed Fund Allocation</text>
  <text x="60" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="16" fill="#10b981">Operational breakeven achieved by Month 14 · Projected ₹1.05 Cr ARR by Year 3.</text>

  <!-- 3 Chart Cards with Images -->
  <g transform="translate(60, 205)">
    <!-- Chart 1: Seed Ask -->
    <rect x="0" y="0" width="365" height="430" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="20" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="15" font-weight="bold" fill="#ffffff">₹25 LAKH SEED ALLOCATION</text>
    <text x="20" y="50" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#38bdf8">Use of Funds at RIDEHACK'26</text>
    <image href="../images/ask_pie_chart.png" x="20" y="65" width="325" height="235"/>
    <line x1="20" y1="312" x2="345" y2="312" stroke="#1e293b" stroke-width="1"/>
    <text x="20" y="336" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#38bdf8">• 40% (₹10.0L): Multi-Node Hardware Infra</text>
    <text x="20" y="358" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#10b981">• 30% (₹7.5L): Multi-Campus Pilot Deployment</text>
    <text x="20" y="380" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#f59e0b">• 20% (₹5.0L): Cert-In Security Audits &amp; IP</text>
    <text x="20" y="402" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#a855f7">• 10% (₹2.5L): Legal, Compliance &amp; B2B Ops</text>

    <!-- Chart 2: Unit Cost COGS -->
    <rect x="395" y="0" width="365" height="430" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="415" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="15" font-weight="bold" fill="#ffffff">UNIT COST COGS (&lt; ₹0.48)</text>
    <text x="415" y="50" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#10b981">&gt;90% Gross Margin Advantage</text>
    <image href="../images/cogs_donut_chart.png" x="415" y="65" width="325" height="235"/>
    <line x1="415" y1="312" x2="740" y2="312" stroke="#1e293b" stroke-width="1"/>
    <text x="415" y="336" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#38bdf8">• Gemini AI Vision OCR: ₹0.18 (38%)</text>
    <text x="415" y="358" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#10b981">• Cloud Storage Allocation: ₹0.15 (31%)</text>
    <text x="415" y="380" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#f59e0b">• AES-256 PDF Stamping: ₹0.06 (13%)</text>
    <text x="415" y="402" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#a855f7">• PoW CPU Node: ₹0.04 (8%)  ·  Buffer: ₹0.05</text>

    <!-- Chart 3: 3-Year ARR Projection -->
    <rect x="790" y="0" width="370" height="430" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
    <text x="810" y="32" font-family="Segoe UI, Inter, sans-serif" font-size="15" font-weight="bold" fill="#ffffff">3-YEAR ARR PROJECTION</text>
    <text x="810" y="50" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#f59e0b">Cash-Flow Positive by Month 14</text>
    <image href="../images/arr_growth_bar_chart.png" x="810" y="65" width="330" height="235"/>
    <line x1="810" y1="312" x2="1140" y2="312" stroke="#1e293b" stroke-width="1"/>
    <text x="810" y="336" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#38bdf8">• Year 1 (Pilot): ₹12 Lakhs ARR (8 HEIs)</text>
    <text x="810" y="358" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#10b981">• Year 2 (Regional): ₹45 Lakhs ARR (30 HEIs)</text>
    <text x="810" y="380" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#f59e0b">• Year 3 (National): ₹1.05 Crores ARR (70+ HEIs)</text>
    <text x="810" y="402" font-family="Segoe UI, Inter, sans-serif" font-size="11.5" fill="#cbd5e1">• High Net Revenue Retention (NRR) &gt; 125%</text>
  </g>

  <!-- Footer -->
  <text x="60" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#64748b">Satyameva Aegis  ·  Capital Efficiency &amp; 3-Year ARR Growth</text>
  <text x="1220" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#f59e0b" text-anchor="end">SLIDE 07 / 08</text>
</svg>"""

notes_content["07_financials_and_seed_ask.md"] = """# Slide 7: Financials & Seed Ask (Speaking Script)
**Speaker: A. Praneeth Sai (Founder & Architecture Lead)**
- We are seeking a ₹25 Lakh seed investment at RIDEHACK'26.
- 40% will fund private multi-node blockchain hardware servers.
- 30% supports our multi-campus pilot deployments across JUIT, JIIT, and JUET.
- 20% covers official Cert-In government security audits and our Indian patent filing for dynamic salted QR codes.
- 10% is allocated for legal, compliance, and B2B sales operations.
- With unit cost below ₹0.48 per credential, we reach cash-flow positivity by Month 14 and scale to ₹1.05 Crores ARR by Year 3.
"""

# -------------------------------------------------------------
# SLIDE 8: Future Scope & Roadmap
# -------------------------------------------------------------
slides_svg["08_future_scope_and_roadmap.svg"] = """<svg xmlns="http://www.w3.org/2000/svg" lang="en" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#060810"/>
  <line x1="60" y1="95" x2="1220" y2="95" stroke="#1e293b" stroke-width="1.5"/>
  <line x1="60" y1="655" x2="1220" y2="655" stroke="#1e293b" stroke-width="1.5"/>

  <!-- Top Pill -->
  <rect x="60" y="42" width="370" height="34" rx="17" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="75" y="64" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981" letter-spacing="1.5">MANDATORY POINT 7  ·  FUTURE SCOPE</text>

  <!-- Title -->
  <text x="60" y="150" font-family="Segoe UI, Inter, sans-serif" font-size="34" font-weight="900" fill="#ffffff">Future Scope &amp; Incubation Scaling Roadmap</text>
  <text x="60" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="16" fill="#10b981">From 3 Jaypee Pilot Campuses to 70+ National Universities &amp; Global Trust Gateways.</text>

  <!-- 3 Phased Roadmap Cards -->
  <g transform="translate(60, 210)">
    <!-- Phase 1 -->
    <rect x="0" y="0" width="365" height="380" rx="14" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
    <rect x="24" y="24" width="110" height="28" rx="6" fill="#064e3b"/>
    <text x="79" y="43" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#34d399" text-anchor="middle">MONTHS 1 – 6</text>
    <text x="24" y="84" font-family="Segoe UI, Inter, sans-serif" font-size="20" font-weight="bold" fill="#ffffff">Phase 1: Pilot &amp; Hardening</text>
    <text x="24" y="106" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#10b981">Consortium Rollout Across Jaypee</text>
    <line x1="24" y1="120" x2="341" y2="120" stroke="#1e293b" stroke-width="1"/>
    <text x="24" y="148" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Live Pilot Deployment across JUIT, JIIT &amp; JUET</text>
    <text x="24" y="180" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Onboard 5,000+ real graduation credentials</text>
    <text x="24" y="212" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Indian Provisional Patent filing for Dynamic 60s Salted QR Verification Protocol</text>
    <text x="24" y="260" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Complete official Cert-In government cybersecurity certification audit</text>
    <rect x="24" y="315" width="317" height="42" rx="8" fill="#18181b"/>
    <text x="36" y="341" font-family="Segoe UI, Inter, sans-serif" font-size="12.5" font-weight="bold" fill="#10b981">MILESTONE: <tspan fill="#ffffff" font-weight="normal">Zero-tamper consortium trial.</tspan></text>

    <!-- Phase 2 -->
    <rect x="395" y="0" width="365" height="380" rx="14" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
    <rect x="419" y="24" width="115" height="28" rx="6" fill="#0c4a6e"/>
    <text x="476" y="43" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#38bdf8" text-anchor="middle">MONTHS 7 – 18</text>
    <text x="419" y="84" font-family="Segoe UI, Inter, sans-serif" font-size="20" font-weight="bold" fill="#ffffff">Phase 2: National Scaling</text>
    <text x="419" y="106" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">DigiLocker, ABC &amp; 30 HEIs</text>
    <line x1="419" y1="120" x2="736" y2="120" stroke="#1e293b" stroke-width="1"/>
    <text x="419" y="148" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• DigiLocker &amp; Academic Bank of Credits (ABC) official API Gateway integration</text>
    <text x="419" y="196" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Scale to 30 North India State &amp; Private Tech Universities</text>
    <text x="419" y="244" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Enterprise B2B API partnerships with top BGV agencies (AuthBridge, TCS)</text>
    <rect x="419" y="315" width="317" height="42" rx="8" fill="#18181b"/>
    <text x="431" y="341" font-family="Segoe UI, Inter, sans-serif" font-size="12.5" font-weight="bold" fill="#38bdf8">MILESTONE: <tspan fill="#ffffff" font-weight="normal">Operational cash-flow positivity.</tspan></text>

    <!-- Phase 3 -->
    <rect x="790" y="0" width="370" height="380" rx="14" fill="#0f172a" stroke="#ec4899" stroke-width="1.5"/>
    <rect x="814" y="24" width="125" height="28" rx="6" fill="#831843"/>
    <text x="876" y="43" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#f472b6" text-anchor="middle">MONTHS 19 – 36</text>
    <text x="814" y="84" font-family="Segoe UI, Inter, sans-serif" font-size="20" font-weight="bold" fill="#ffffff">Phase 3: Global Trust Bridge</text>
    <text x="814" y="106" font-family="Segoe UI, Inter, sans-serif" font-size="13" font-weight="bold" fill="#ec4899">WES, Embassies &amp; 70+ HEIs</text>
    <line x1="814" y1="120" x2="1136" y2="120" stroke="#1e293b" stroke-width="1"/>
    <text x="814" y="148" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Cross-Border Verification Gateway for WES, foreign universities &amp; embassies</text>
    <text x="814" y="196" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• NEP 2020 internationalization trust bridge for Indian scholars abroad</text>
    <text x="814" y="244" font-family="Segoe UI, Inter, sans-serif" font-size="13" fill="#cbd5e1">• Scale to 70+ higher education institutions reaching ₹1.05 Crores ARR</text>
    <rect x="814" y="315" width="322" height="42" rx="8" fill="#18181b"/>
    <text x="826" y="341" font-family="Segoe UI, Inter, sans-serif" font-size="12.5" font-weight="bold" fill="#ec4899">MILESTONE: <tspan fill="#ffffff" font-weight="normal">National standard for origin verification.</tspan></text>
  </g>

  <!-- Final Call to Action Banner -->
  <g transform="translate(60, 605)">
    <rect x="0" y="0" width="1160" height="38" rx="8" fill="#10b981" fill-opacity="0.1" stroke="#10b981" stroke-width="1"/>
    <text x="580" y="24" font-family="Segoe UI, Inter, sans-serif" font-size="13.5" font-weight="bold" fill="#10b981" text-anchor="middle">THE ASK AT RIDEHACK'26: ₹25 Lakhs Incubation &amp; Multi-Node Hardware Deployment  ·  Live working prototype deployed at JUIT Waknaghat.</text>
  </g>

  <!-- Footer -->
  <text x="60" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#64748b">Satyameva Aegis  ·  Empowering Indian Universities with Immutable Truth</text>
  <text x="1220" y="685" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="bold" fill="#10b981" text-anchor="end">SLIDE 08 / 08</text>
</svg>"""

notes_content["08_future_scope_and_roadmap.md"] = """# Slide 8: Future Scope & Roadmap (Speaking Script)
**Speaker: A. Praneeth Sai (Founder & Architecture Lead)**
- Our roadmap executes across 3 high-impact phases:
- **Phase 1 (Months 1–6)**: Jaypee consortium pilot hardening across JUIT, JIIT, and JUET, patent filing for dynamic salted QR, and Cert-In cybersecurity audit.
- **Phase 2 (Months 7–18)**: Official DigiLocker and ABC API integration, scaling to 30 North India universities and achieving operational breakeven.
- **Phase 3 (Months 19–36)**: International trust gateway for WES and foreign visa embassies, reaching 70+ institutions and ₹1.05 Crores ARR.
- With our live working prototype ready at JUIT Waknaghat, we invite you to partner with us in restoring trust to Indian higher education. Thank you!
"""

# Write all SVG slides and notes
for filename, svg_str in slides_svg.items():
    with open(os.path.join(SVG_OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg_str)

for filename, note_str in notes_content.items():
    with open(os.path.join(NOTES_DIR, filename), "w", encoding="utf-8") as f:
        f.write(note_str)

print(f"[2/3] All 8 SVG slides and speaker notes written to {PROJECT_DIR}")

# Compile with ppt-master svg_to_pptx.py
compiler = os.path.join(BASE_DIR, "ppt-master", "skills", "ppt-master", "scripts", "svg_to_pptx.py")
out_pptx_internal = os.path.join(EXPORTS_DIR, "RIDEHACK26_SATYAMEVA_AEGIS_PITCH_DECK.pptx")
out_pptx_root = os.path.join(BASE_DIR, "RIDEHACK26_SATYAMEVA_AEGIS_PITCH_DECK.pptx")

cmd = [
    sys.executable,
    compiler,
    PROJECT_DIR,
    "-o", out_pptx_internal,
    "--enable-dangerous-nonconforming-svg-export"
]

print("[3/3] Compiling presentation using ppt-master engine...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"[OK] ppt-master successfully built: {out_pptx_internal}")
    shutil.copy2(out_pptx_internal, out_pptx_root)
    print(f"[OK] Copied to workspace root: {out_pptx_root}")
else:
    print(f"[!] Compilation error:\n{res.stderr}\n{res.stdout}")


# Post-process PPTX: Inject real UI screenshot images onto Slide 3
try:
    print("[4/4] Embedding high-res UI screenshots onto Slide 3...")
    prs = Presentation(out_pptx_root)
    slide3 = prs.slides[2]  # Slide 3
    
    screen_doc = os.path.join(BASE_DIR, "static", "screenshots", "04_student_document.png")
    screen_verify = os.path.join(BASE_DIR, "static", "screenshots", "02_verify_public.png")
    
    if os.path.exists(screen_doc):
        # Top Frame inside browser chrome
        # Left = 660 px * (13.333333/1280) = 6.875 in
        # Top = (205 + 28) px * (7.5/720) = 2.427 in
        # Width = 560 px * (13.333333/1280) = 5.833 in
        # Height = (210 - 28) px * (7.5/720) = 1.895 in
        slide3.shapes.add_picture(
            screen_doc,
            Inches(6.88), Inches(2.44),
            width=Inches(5.82), height=Inches(1.88)
        )
        print("  [OK] Embedded 04_student_document.png onto Slide 3")
        
    if os.path.exists(screen_verify):
        # Bottom Frame inside browser chrome
        # Top = (205 + 226 + 28) px * (7.5/720) = 4.781 in
        slide3.shapes.add_picture(
            screen_verify,
            Inches(6.88), Inches(4.79),
            width=Inches(5.82), height=Inches(1.88)
        )
        print("  [OK] Embedded 02_verify_public.png onto Slide 3")
        
    prs.save(out_pptx_root)
    shutil.copy2(out_pptx_root, out_pptx_internal)
    print("  [OK] Presentation updated with native UI pictures.")
except Exception as e:
    print(f"  [!] Note: Post-processing picture insertion: {e}")

# Export PDF via PowerPoint COM if available
try:
    import win32com.client
    pdf_out = os.path.join(BASE_DIR, "RIDEHACK26_SATYAMEVA_AEGIS_PITCH_DECK.pdf")
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    ppt = powerpoint.Presentations.Open(os.path.abspath(out_pptx_root), WithWindow=False)
    ppt.SaveAs(os.path.abspath(pdf_out), 32)  # 32 = ppSaveAsPDF
    ppt.Close()
    powerpoint.Quit()
    print(f"[OK] Exported updated PDF: {pdf_out}")
except Exception as e:
    print(f"  [!] PDF export note: {e}")
