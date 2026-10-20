<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=10,14,20,27&height=220&section=header&text=Satyameva%20Aegis&fontSize=48&fontAlignY=35&animation=twinkling&fontColor=ffffff" />
</p>

<p align="center">
  <b>Decentralized Academic & Identity Credentialing Ecosystem with Zero Gas Fees</b><br>
  <i>Forging immutable cryptographic truth across Higher Education & Global Employment</i>
</p>

<p align="center">
  <a href="https://github.com/praneethsai050-cmd/satyameva">
    <img src="https://img.shields.io/badge/RIDEHACK'26-Grand_Finalist_(Team_10)-FF6B00?style=for-the-badge&logo=target&logoColor=white" />
  </a>
  <a href="https://github.com/praneethsai050-cmd/satyameva">
    <img src="https://img.shields.io/badge/SIH_2026-Team_Leader_(SIH26125)-10B981?style=for-the-badge&logo=shield&logoColor=white" />
  </a>
  <a href="https://youtu.be/Uu-bOJTZrFY">
    <img src="https://img.shields.io/badge/YouTube-Watch_Pitch_Defense-FF0000?style=for-the-badge&logo=youtube&logoColor=white" />
  </a>
  <a href="https://praneethsai050-cmd.github.io">
    <img src="https://img.shields.io/badge/Live-Interactive_Portfolio-060810?style=for-the-badge&logo=googlechrome&logoColor=10B981" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Framework-Flask_3.0-000000?style=flat-square&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Consensus-Custom_SHA--256_PoW-10B981?style=flat-square" />
  <img src="https://img.shields.io/badge/Cryptography-ECDSA_secp256k1-8B5CF6?style=flat-square" />
  <img src="https://img.shields.io/badge/Biometrics-OpenCV_128D_Face--Lock-E11D48?style=flat-square&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/AI_OCR-Gemini_2.0_Flash-4285F4?style=flat-square&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Container-Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

---

## 📑 Table of Contents
- [Executive Overview & The Problem](#-executive-overview--the-problem)
- [System Architecture & The Tri-Portal Ecosystem](#-system-architecture--the-tri-portal-ecosystem)
- [Cryptographic & Security Architecture](#-cryptographic--security-architecture)
- [Key Innovations & Technical Benchmarks](#-key-innovations--technical-benchmarks)
- [B2B SaaS Business Model & Economics](#-b2b-saas-business-model--economics)
- [Quickstart & Local Deployment](#-quickstart--local-deployment)
- [Docker Deployment](#-docker-deployment)
- [Demo Credentials & Scenarios](#-demo-credentials--scenarios)
- [Comprehensive Test Harness](#-comprehensive-test-harness)
- [Repository Layout](#-repository-layout)
- [Founding Team & Hackathon Accolades](#-founding-team--hackathon-accolades)
- [Connect & Transmission Hub](#-connect--transmission-hub)

---

## ⚡ Executive Overview & The Problem

Academic credential fraud, fake degrees, and forged certificates cost Indian universities and enterprise recruiters billions annually. The current verification process relies on:
1. **Manual Registrar Checks:** 3 to 6 weeks of bureaucratic turnaround.
2. **Third-Party Background Verification (BGV) Agencies:** Charging between **₹500 to ₹2,500 per candidate verification**.
3. **Public Blockchain Shortcomings:** Ethereum / Polygon implementations suffer from volatile gas fees ($2–$15 per mint), network congestion, and irreversible smart contract vulnerabilities.

### 🛡️ The Satyameva Aegis Solution
**Satyameva Aegis** solves this through a custom, zero-gas **Proof-of-Work (PoW) blockchain**, asymmetric **ECDSA signatures**, dynamic **anti-replay HMAC QR codes**, and multi-modal **AI identity heuristics**:
- ⏱️ **92% Verification Latency Reduction:** Verification drops from 30+ days to **under 5 seconds**.
- 💸 **₹0 Verification Cost for Students & Universities:** Completely eliminates gas fees through an optimized, institutionally managed private PoW consensus.
- 🔒 **Tamper-Evident Proof Engine:** Cryptographically binds raw document digests, per-record salts, student biometrics, and immutable block headers.

---

## 🏛️ System Architecture & The Tri-Portal Ecosystem

Satyameva Aegis provides a unified cryptographic backend supporting three specialized operational portals:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SATYAMEVA AEGIS PLATFORM                        │
└────────────────────────────────────────────────────────────────────────┘
          │                                 │                    │
          ▼                                 ▼                    ▼
┌──────────────────┐             ┌──────────────────┐   ┌────────────────┐
│  ISSUER PORTAL   │             │  STUDENT PORTAL  │   │VERIFIER PORTAL │
│ (University Reg) │             │ (Identity Wallet)│   │  (HR / Public) │
└──────────────────┘             └──────────────────┘   └────────────────┘
          │                                 │                    │
          │ • Bulk CSV Issuance             │ • 3D WebGL Ledger  │ • Instant Verification
          │ • ECDSA secp256k1 Signing       │ • 60s Dynamic QR   │ • Hash Audit Engine
          │ • Batch PoW Mining              │ • Stamped PDFs     │ • B2B API Key Access
          │                                 │                    │
          └────────────────────────┬────────┴────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      CORE CRYPTOGRAPHIC LAYER                          │
├────────────────────────────────────────────────────────────────────────┤
│ • Custom SHA-256 PoW Blockchain (Difficulty: 4)                        │
│ • PBKDF2-HMAC-SHA256 (100,000 Iterations) Key Derivation               │
│ • OpenCV 128D Face-Lock & PIL Differential Tamper Heatmapping          │
│ • Gemini 2.0 Flash Multimodal OCR Marksheet Extractor                  │
│ • Dual Storage: SQLite Persistence + Encrypted JSON Blockchain Ledger  │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. 🏛️ Issuer Portal (`/issuer`)
- **Single & Bulk CSV Issuance:** Registrars upload student graduation records via standard `.csv` with an all-or-nothing transactional parser (`POST /issuer/bulk-issue`).
- **ECDSA Key Minting:** Each credential is cryptographically signed using the institution's private key (`secp256k1`).
- **Automated Block Mining:** The PoW engine mines dedicated blocks for each issued credential and distributes instant email notifications with permanent cryptographic hashes.

### 2. 🎓 Student Portal (`/student`)
- **Interactive 3D WebGL Ledger:** Real-time visual blockchain viewer powered by Three.js (r128).
- **Anti-Replay Dynamic QR Codes:** Generates HMAC-signed dynamic QR codes valid for **60 seconds only**. Screenshots forwarded across WhatsApp or email fail upon expiration.
- **Permanent Tamper-Sealed PDF Generation:** Instantly downloads official certificates stamped with high-contrast dynamic cryptographic seals and ledger hashes.

### 3. 🔍 Verifier Portal & Public Gateway (`/verify`, `/v/<hash>`)
- **Zero-Friction Hash Verification:** Employers and universities verify credentials in <5 seconds without requiring an account.
- **Selective Disclosure:** Genuine credentials reveal verified holder details; revoked, forged, or expired credentials strictly redact student personal data.

---

## 🔐 Cryptographic & Security Architecture

### 1. Dual-Layer Hash Generation
Every credential hash $H_{doc}$ is calculated through canonical hashing of metadata, the raw file digest, and a cryptographically secure pseudo-random salt:

$$H_{doc} = \text{SHA-256}\Big(\text{SHA-256}(FileBytes) \parallel \text{Canonical}(Metadata) \parallel Salt_{16}\Big)$$

Even a single changed byte in the student's name, roll number, or marksheet alters the hash completely, invalidating the proof walk.

### 2. Custom Proof-of-Work (PoW) Consensus
- Hand-crafted Python engine in `blockchain.py` operating at difficulty $D=4$ (target: 4 leading hexadecimal zeros: `0000...`).
- Each block header seals:
  - `index`, `timestamp`, `doc_hash`, `issuer_id`, `prev_hash`, `nonce`, and `proof`.
- Chain validation (`validate_chain()`) re-calculates every nonce from genesis to the current block before passing audit checks.

### 3. 6-Stage Hierarchical Verification Pipeline
When an employer queries a credential, the verification engine evaluates proofs cheapest check first to prevent denial-of-service and state exhaustion:

```
[ Input Hash / QR ] ──► (1) NOT_FOUND ──► (2) QR_EXPIRED ──► (3) REVOKED ──► (4) TAMPERED ──► (5) EXPIRED ──► (6) VALID ✅
```

1. `NOT_FOUND`: Hash does not exist in the decentralized ledger.
2. `QR_EXPIRED`: The 60-second HMAC token has timed out (prompts verifier to request a live refresh).
3. `REVOKED`: University has flagged the credential as withdrawn / canceled.
4. `TAMPERED`: Stored document payload or salt does not match the re-derived SHA-256 digest.
5. `EXPIRED`: Document validity period has elapsed (e.g. provisional bonafides).
6. `VALID`: Cryptographic proof confirmed, signature valid, block walked to genesis.

---

## 🚀 Key Innovations & Technical Benchmarks

| Feature / Metric | Traditional Manual Verification | Public Ethereum / Polygon | Satyameva Aegis (Our Solution) |
| :--- | :--- | :--- | :--- |
| **Verification Latency** | 15 – 45 Days | 15 – 60 Seconds | **< 5 Seconds (Instant)** |
| **Transaction / Gas Fee** | ₹500 – ₹2,500 (BGV agency) | $2 – $15 (Volatile ETH/MATIC) | **₹0 (Zero Gas Fees)** |
| **Biometric Face-Lock** | ❌ None | ❌ None (Privacy Risk) | **✅ 128D OpenCV Face Embeddings** |
| **Tamper Detection** | ❌ Manual visual check | ❌ Only metadata check | **✅ PIL Pixel Heatmapping + Gemini OCR** |
| **Credential Portability** | Physical paper / Scanned PDF | Crypto Wallet (High Friction) | **✅ 60s Dynamic QR + Stamped PDF** |
| **Institutional Control** | Manual registrar records | Hard fork required | **✅ Instant Revocation & Audit Logs** |

---

## 💼 B2B SaaS Business Model & Economics

Satyameva Aegis is structured with a sustainable B2B institutional SaaS model validated for commercialization:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      REVENUE & MONETIZATION MODEL                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Institutional Campus Subscription:                                 │
│    • ₹1,50,000 / Year per University campus                            │
│    • Unlimited credential issuance, bulk CSV engine, admin dashboard   │
│                                                                        │
│ 2. Corporate Pay-Per-Verify API:                                       │
│    • ₹25 / Verification for BGV Agencies, IT Firms & Embassies         │
│    • Bulk enterprise packages: ₹10,000 for 500 API calls               │
│                                                                        │
│ 3. Cost to Students & Alumni:                                         │
│    • ₹0 FOREVER — Guaranteed equal access and zero student fee barrier │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Quickstart & Local Deployment

### Prerequisites
- Python 3.10+ (Recommended: Python 3.11 / 3.12 / 3.14)
- Git & Virtualenv

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/praneethsai050-cmd/satyameva.git
cd satyameva

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Mine Genesis Block
```bash
# Drops existing test tables and generates fresh demo dataset & blockchain
python seed.py --reset
```

### 4. Run Development Server
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🐳 Docker Deployment

Run the complete isolated production environment using Docker Compose:

```bash
# Build and run containers in detached mode
docker-compose up -d --build

# View container logs
docker-compose logs -f

# Stop environment
docker-compose down
```
Access the application on port **`5000`** (`http://localhost:5000`).

---

## 🔑 Demo Credentials & Scenarios

All accounts use the pre-seeded demo password: **`satyameva123`**

| Portal / Role | Username | Password | Operational Demonstration |
| :--- | :--- | :--- | :--- |
| 🎓 **Student** | `aarav.sharma` | `satyameva123` | 6 authentic credentials, 3D WebGL chain, 60s dynamic QR code, and ledger data inspection. |
| 🎓 **Student** | `priya.nair` | `satyameva123` | 1 officially **revoked** degree to test the `REVOKED` verification state. |
| 🏛️ **Issuer** | `jiit.registrar` | `satyameva123` | Registrar console: Single issuance, bulk CSV batch upload, and audit logs. |
| 🔍 **Verifier** | `infosys.hr` | `satyameva123` | Corporate verifier console: Candidate query history, bulk verification API checks. |

> **Security Note:** Sessions automatically terminate after **5 minutes of idle time** with a live visual countdown pill in the navigation header to enforce zero-trust workstation security.

---

## 🧪 Comprehensive Test Harness

The codebase ships with two independent test suites requiring zero external testing framework dependencies:

### 1. Smoke Route Audit
```bash
python _smoke.py
```
*Walks every endpoint as an authenticated student and asserts HTTP response codes, body sizes, and RBAC 403 Forbidden boundaries.*

### 2. Behavioral & Cryptographic Assertion Suite
```bash
# Windows:
python _assert.py
# Linux/macOS:
PYTHONIOENCODING=utf-8 python _assert.py
```
*Validates all 6 verification outcomes, checks 60-second HMAC QR expiry, verifies tamper detection against manually mutated database rows, and audits the consensus walk.*

### 3. End-to-End Bulk Issuance Integration Test
```bash
python test_bulk_issue_e2e.py
```
*Tests atomic CSV parsing, row pre-validation, all-or-nothing rollback guarantees, and bulk PoW block mining.*

---

## 📂 Repository Layout

```
satyameva/
├── app.py                      # Flask Application Factory & Middleware
├── blockchain.py               # Custom SHA-256 Proof-of-Work Consensus Engine
├── security.py                 # PBKDF2 Hashing, Salting & HMAC-SHA256 QR Tokens
├── config.py                   # Centralized Configuration & Cryptographic Tunables
├── seed.py                     # Demo Data Seeder (Users, Credentials, Blocks)
├── run.py                      # Local Development Entry Point
├── Dockerfile                  # Containerized Runtime Definition
├── docker-compose.yml          # Production Orchestration Spec
├── models/
│   ├── block.py                # Blockchain Ledger & Nonce Schema
│   ├── document.py             # Credential Document Model & Metadata
│   ├── user.py                 # RBAC User, Student, Issuer & Verifier Models
│   └── verification_log.py     # Immutable Forensic Verification Audit Trail
├── routes/
│   ├── auth_routes.py          # Session Lifecycle, Login & Logout Handlers
│   ├── issuer_routes.py        # Single & Bulk CSV Credential Issuance Engine
│   ├── student_routes.py       # Student Identity Wallet & 3D Ledger View
│   ├── verifier_routes.py      # B2B Corporate Verifier Workspace
│   └── public_routes.py        # Public Hash Verification & Permanent URLs
├── services/
│   ├── credential_service.py   # Core Issuance, Salt Generation & Block Mining
│   ├── crypto_service.py       # ECDSA secp256k1 Asymmetric Key Pair Minting
│   ├── gemini_service.py       # Multimodal Gemini 2.0 Flash Marksheet OCR
│   ├── stamp_service.py        # Dynamic Certificate Seal & Stamped PDF Renderer
│   ├── qr_service.py           # Replay-Resistant HMAC-SHA256 60s QR Generator
│   └── email_service.py        # Automated SMTP Dispatch for Hash Notifications
├── static/
│   ├── js/hero3d.js            # Three.js (r128) WebGL Blockchain Visualizer
│   └── css/style.css           # Responsive Glassmorphic Cyberpunk Theme
└── templates/                  # Jinja2 Tri-Portal Templates (Student, Issuer, Verifier)
```

---

## 👥 Founding Team & Hackathon Accolades

### 🏆 RIDEHACK'26 — Grand Finals Squad (JIIT Noida • Team ID: 10)
- **A. Praneeth Sai** — *Founder & Lead Architecture Engineer* (1st-Year B.Tech CSE - Cyber Security @ JUIT Solan)  
  *Sole architect of the custom Proof-of-Work engine, ECDSA signing protocols, backend APIs, and security mechanisms.*
- **Anushka Bansal** — *Co-Founder & Data Integrity Lead* (B.Tech Bioinformatics @ JUIT Solan)  
  *Heuristic models, forensic tamper detection pipelines, and structural validation specifications.*
- **Shashank Ray** — *Co-Founder & AI Systems Lead* (B.Tech CSE - AI & ML @ JUIT Solan)  
  *Gemini 2.0 Flash OCR extraction engine, multimodal integration, and B2B SaaS commercials.*
- **Sameeksha Chandel** — *Co-Founder & Product Operations Lead* (B.Tech CSE - AI & ML @ JUIT Solan)  
  *NEP 2020 regulatory compliance, institutional user experience, and venture pitch development.*

### 🎖️ Smart India Hackathon 2026 — Team CYPHER-X (`PS: SIH26125`)
- **A. Praneeth Sai** (Team Leader & Core Architect)
- **Jai Chauhan** (Systems & Network Deployment Lead)
- **Jyoti Rana** (Regulatory Compliance & Research Lead)
- **Gauri** (Frontend & UX Architecture Lead)
- **Sparsh** (Verification Protocols & Data Specs Lead)
- **Akshit Thakur** (QA & Presentation Workflow Lead)

---

## 📬 Connect & Transmission Hub

Have questions, collaboration inquiries, or investment discussions? Reach out directly:

<p align="center">
  <a href="https://www.linkedin.com/in/a-praneeth-sai-089023289/">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
  <a href="https://youtube.com/@flixyte">
    <img src="https://img.shields.io/badge/YouTube-@flixyte-FF0000?style=for-the-badge&logo=youtube&logoColor=white" />
  </a>
  <a href="mailto:261034004@juitsolan.in">
    <img src="https://img.shields.io/badge/Academic_Email-261034004@juitsolan.in-8B5CF6?style=for-the-badge&logo=gmail&logoColor=white" />
  </a>
  <a href="mailto:praneethsai050@gmail.com">
    <img src="https://img.shields.io/badge/Personal_Email-praneethsai050@gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white" />
  </a>
</p>

<p align="center">
  <a href="https://praneethsai050-cmd.github.io">
    <img src="https://img.shields.io/badge/🌐_Visit_My_Interactive_Web_Portfolio-10B981?style=for-the-badge&logoColor=white" />
  </a>
</p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=10,14,20,27&height=100&section=footer" />
</p>

<p align="center">
  <b>Satyameva Aegis</b> • <i>"Truth alone triumphs through immutable cryptography."</i>
</p>
