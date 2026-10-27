# Satyameva Aegis — Product Requirements Document (PRD)

> **Document Version:** 2.4.0 • **Status:** Production-Approved • **Author:** A. Praneeth Sai & Core Engineering Teams  
> **Ecosystem:** Decentralized Academic & Identity Credentialing Infrastructure with Zero Gas Fees

---

## 1. Executive Summary & Vision

Academic credential fraud, fake degrees, marksheet tampering, and counterfeit diplomas represent a multi-billion-rupee crisis across the Indian higher education and global recruitment ecosystems. Conventional background verification (BGV) takes 15 to 45 business days, costs between **₹500 and ₹2,500 per candidate**, and exposes universities to manual registrar fatigue and reputational compromise. Public blockchain solutions (Ethereum, Polygon, Solana) introduce prohibitive gas fees ($2–$15 per mint), smart contract immutability risks, and regulatory compliance friction under Indian data sovereignty laws.

**Satyameva Aegis** is an enterprise-grade, zero-gas-fee academic credentialing platform combining a custom Proof-of-Work (PoW) blockchain ledger, asymmetric **ECDSA secp256k1** digital signatures, dynamic **anti-replay HMAC-SHA256 QR codes** with campus crests, **Google Gemini 2.0 Flash** multimodal AI document parsing, and an integrated **Model Context Protocol (MCP)** interface for autonomous auditing agents.

### Core Value Proposition
1. **Zero Gas Fees ($0.00 / ₹0.00):** Completely eliminates blockchain transaction costs via an optimized, institution-governed private PoW consensus.
2. **Instant Verification (< 5 Seconds):** Reduces background verification turnaround time from 30+ days to under 5 seconds with zero-friction public verification.
3. **Multi-Modal AI Ingestion:** Extracts marksheet and degree metadata in < 2 seconds using Google Gemini 2.0 Flash AI, eliminating hours of manual registrar data entry.
4. **Anti-Replay Dynamic QR & AES-256 Sealed PDFs:** Enforces 60-second HMAC rolling tokens and AES-256 PDF encryption keyed to student Date of Birth (DDMMYYYY).
5. **Autonomous AI Interoperability:** Implements standard MCP (Model Context Protocol) JSON-RPC 2.0 stdio server for LLMs and autonomous compliance checkers.

---

## 2. Team Roster & Governance Configurations

Satyameva Aegis is deployed under two dual-governance team frameworks:

### 2.1 Smart India Hackathon (SIH 2026) — Team CYPHER-X (`PS: SIH26125`)
| Member Name | Role & Specialization | Key Operational Deliverables |
| :--- | :--- | :--- |
| **A. Praneeth Sai** | **Team Leader & Core Architect** | Full-stack architecture, custom PoW consensus, cryptographic engine, MCP server |
| **Jai Chauhan** | **Systems & Network Deployment Lead** | Dockerization, Linux/Windows node deployment, P2P multi-node gossip sync |
| **Jyoti Rana** | **Regulatory Compliance & Research Lead** | UGC / NEP 2020 alignment, Academic Bank of Credits (ABC) compliance, IP legalities |
| **Gauri** | **Frontend & UX Architecture Lead** | Glassmorphic cyber theme, Three.js (r128) 3D ledger visualizer, responsive UI |
| **Sparsh** | **Verification Protocols & Data Specs Lead** | Schema validation, CSV ingestion bounds, verification log schemas, forensic tracking |
| **Akshit Thakur** | **QA & Presentation Workflow Lead** | End-to-end test suites, adversarial stress testing, pitch deck collateral |

### 2.2 RIDEHACK 2026 (IIC JUIT / JIIT Noida) — Grand Finals Squad (Team 10)
| Member Name | Role & Designation | Core Institutional Focus |
| :--- | :--- | :--- |
| **A. Praneeth Sai** | **Founder & Lead Architecture Engineer** | Cryptographic core, custom PoW ledger, secp256k1 Schnorr/ECDSA, API architecture |
| **Anushka Bansal** | **Co-Founder & Data Integrity Lead** | Forensic tamper detection, differential heatmapping, biometric validation algorithms |
| **Shashank Ray** | **Co-Founder & AI Systems Lead** | Gemini 2.0 Flash multimodal prompt pipelines, B2B SaaS economics, ARR financial models |
| **Sameeksha Chandel**| **Co-Founder & Product Operations Lead** | Student portal UX, institutional pilot rollouts (JUIT/JIIT/JUET), pitch narrative |

---

## 3. User Personas & Use Cases

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SATYAMEVA TRI-PORTAL ACTORS                     │
└────────────────────────────────────────────────────────────────────────┘
          │                                 │                    │
          ▼                                 ▼                    ▼
┌──────────────────┐             ┌──────────────────┐   ┌────────────────┐
│ 🏛️ UNIVERSITY     │             │ 🎓 STUDENT       │   │ 🔍 CORPORATE   │
│    ISSUER        │             │    WALLET HOLDER │   │    VERIFIER    │
└──────────────────┘             └──────────────────┘   └────────────────┘
 - Issue Degrees / Marks           - View 3D WebGL Ledger - Verify Hashes (<5s)
 - Bulk CSV Batch Minting          - 60s Dynamic QR Codes - Batch Verify CSV
 - Approve Registrations           - Download AES-256 PDF - Export Audit Reports
 - Gemini AI PDF Extraction        - Real-Time SMTP Alerts- Flag Tampered Docs
```

### 3.1 University Registrar (Issuer)
- **Problem:** Registrars spend hundreds of hours manually entering graduate data and responding to postal/email BGV requests.
- **Jobs To Be Done:**
  - Upload degree certificates as single files or bulk CSV batches.
  - Automatically parse names, roll numbers, programs, and graduation dates via Gemini 2.0 Flash AI.
  - Digitally sign credentials with the institution’s private secp256k1 key and anchor them into newly mined PoW blocks.
  - Revoke compromised or fraudulent credentials with immutable timestamped audit logs.

### 3.2 Student & Alumni (Credential Holder)
- **Problem:** Students must physically visit campus or pay high courier fees to obtain stamped bonafide/migration certificates, and risk privacy leaks when sending credentials over unsecured channels.
- **Jobs To Be Done:**
  - Self-sovereign identity wallet accessible via password or Google/Microsoft OAuth.
  - Display credentials in an interactive 3D WebGL holographic blockchain ledger.
  - Generate dynamic, single-use 60-second HMAC QR codes that defeat screenshot-forwarding fraud.
  - Download official certificates stamped with high-contrast crests and secured with AES-256 passwords (DOB: `DDMMYYYY`).
  - Receive instant security alerts (email + portal notification) whenever an employer verifies their record.

### 3.3 Corporate Employer & Background Verification Agency (Verifier)
- **Problem:** Verification agencies face long wait times, opaque manual verification fees (₹500–₹2,500), and forged paper seals.
- **Jobs To Be Done:**
  - Instant zero-login hash verification at `/verify` or permanent permalink `/v/<doc_hash>`.
  - Point-and-shoot camera verification of live student dynamic QR codes.
  - Authenticated enterprise workspace (`/verifier/dashboard`) for batch hash lookups and bulk CSV auditing.
  - Export cryptographic proof certificates and compliance audit logs in PDF/CSV.
  - Report fraudulent documents directly into the national forensic registry.

### 3.4 Master Administrator (Satyameva Platform Authority)
- **Jobs To Be Done:**
  - Multi-campus governance (JIIT Noida, JUIT Waknaghat, JUET Guna, and partner universities).
  - Institution onboarding, domain validation, and annual SaaS subscription management.
  - Dynamic PoW difficulty tuning ($D=1$ to $D=4$) and node health monitoring.
  - Review fraud reports and audit cryptographic integrity across all network nodes.

---

## 4. Detailed Functional Requirements

### 4.1 Authentication & Zero-Trust Session Management
- **FR-AUTH-01 (RBAC Segregation):** Strict role-based routing (`student`, `issuer`, `verifier`, `admin`). Any cross-portal access attempt triggers a hard HTTP 403 Forbidden without redirect leakage.
- **FR-AUTH-02 (PBKDF2 Password Hashing):** 100,000 iterations of PBKDF2-HMAC-SHA256 with 32-byte cryptographically secure random per-user salt. Zero silent passes or fallback to weak algorithms.
- **FR-AUTH-03 (5-Minute Inactivity Timeout):** User sessions automatically expire after 300 seconds of inactivity. Client UI displays an active visual countdown pill in the navbar.
- **FR-AUTH-04 (OAuth 2.0 / OIDC):** Native Google and Microsoft Single Sign-On (SSO) mapped directly to pre-verified student records.

### 4.2 Credential Ingestion & AI Parsing
- **FR-AI-01 (Gemini 2.0 Flash Extraction):** Ingestion of scanned degrees and marksheets (PDF, PNG, JPEG) via `google-genai` SDK. Automatically extracts:
  - `student_name`, `roll_number`, `student_email`, `doc_type`, `title`, `institution`, and `dob`.
- **FR-AI-02 (Schema Normalization):** Normalizes document types against 6 canonical classes: `DEGREE`, `MARKSHEET`, `TC`, `MIGRATION`, `BONAFIDE`, `INTERNSHIP`.
- **FR-AI-03 (Fallback Resilience):** If AI key is missing or model times out, the UI gracefully enables manual form entry without crashing.

### 4.3 Bulk Issuance & Transactional Atomicity
- **FR-BULK-01 (CSV Parser & Header Normalization):** Synchronous parser supporting UTF-8 BOM stripping, whitespace trimming, and case-insensitive headers: `roll_number`, `doc_type`, `title`, with optional `student_name`, `validity_days`, `extra_fields`.
- **FR-BULK-02 (All-or-Nothing Batch Validator):** Pre-validates every row in the batch. If ANY row fails validation (unknown doc type, negative validity, malformed roll number):
  - 0 documents are created.
  - 0 blocks are mined.
  - Immediate HTTP 400 with row-by-row error feedback.
- **FR-BULK-03 (Automated Student Provisioning):** If a student roll number does not exist during a valid bulk issuance, a student account is auto-provisioned with standard credentials.

### 4.4 Custom Proof-of-Work Blockchain Consensus
- **FR-BC-01 (PoW Consensus Engine):** Custom Python engine in `blockchain.py` operating at difficulty $D=4$ (target: 4 leading hex zeros `0000...`).
- **FR-BC-02 (Dual Persistence):** Every mined block is dual-persisted simultaneously to:
  1. Relational SQLite table `block`.
  2. JSON ledger file `instance/blockchain.json`.
- **FR-BC-03 (Chain Validation):** `validate_chain()` recomputes all SHA-256 block hashes and proof-of-work nonces from Genesis (#0) to current head. Detects any database tampering, broken pointers, or gap attacks.
- **FR-BC-04 (P2P Longest Chain Rule):** Multi-node endpoints (`/blockchain/chain`, `/blockchain/nodes/register`, `/blockchain/resolve`) implement Nakamoto consensus conflict resolution.

### 4.5 Dynamic QR & Institutional Crest Branding
- **FR-QR-01 (Replay-Resistant Dynamic QR):** QR payload carries a short-lived HMAC-SHA256 signature token valid for exactly 60 seconds (`expires_at.signature`). Expired or forwarded QR screenshots fail verification.
- **FR-QR-02 (Error Correction Level H):** Encoded with `ERROR_CORRECT_H` (~30% error correction tolerance) to ensure rapid smartphone camera scanning.
- **FR-QR-03 (Retina Campus Crest Emblems):** Embedded circular institutional badges (JIIT, JUIT, JUET, AEGIS) generated via PIL at 4x supersampling with Lanczos downscaling and white isolation margins.

### 4.6 Verification Engine & Forensic Audit Logs
- **FR-VER-01 (Hierarchical 6-Stage Check):**
  1. `NOT_FOUND` → Hash absent from ledger.
  2. `QR_EXPIRED` → 60-second token elapsed.
  3. `REVOKED` → Issuer marked credential as withdrawn.
  4. `TAMPERED` → Recomputed document digest or signature mismatch.
  5. `EXPIRED` → Document passed its `valid_until` date.
  6. `VALID` → Cryptographic proof verified to genesis block.
- **FR-VER-02 (Selective Disclosure):** Valid checks reveal verified student details. Non-valid checks strictly redact student data to prevent enumeration attacks.
- **FR-VER-03 (Audit Telemetry):** Every check logs IPv4, IPv6, timestamp, user agent, verification method (`QR` vs `HASH`), and verifier label to `VerificationLog`.
- **FR-VER-04 (Live SMTP Alerting):** Dispatches multipart HTML/text email notification to student via Gmail SMTP immediately upon successful verification.

### 4.7 Model Context Protocol (MCP) Server
- **FR-MCP-01 (JSON-RPC 2.0 stdio Server):** Complete MCP implementation in `mcp_server.py` exposing:
  - Tools: `verify_credential`, `get_blockchain_info`, `get_block_by_index`, `audit_student_records`, `submit_fraud_report`, `extract_academic_document`.
  - Resources: `satyameva://blockchain/ledger`, `satyameva://institutions/registry`, `satyameva://stats/telemetry`.
  - Prompts: `audit_credential`, `institution_compliance_check`.
- **FR-MCP-02 (Diagnostic Self-Test):** Built-in `--test` flag for automated CLI test of all MCP capabilities.

---

## 5. Non-Functional Requirements & Performance SLAs

| Metric / Dimension | Target SLA | Empirical Benchmark | Hard Failure Boundary |
| :--- | :--- | :--- | :--- |
| **Public Verification Latency** | < 5.0 seconds | **0.85 – 1.40 seconds** | > 10.0 seconds |
| **PoW Block Mining (Diff 4)** | < 3.0 seconds | **0.42 – 1.10 seconds** | > 15.0 seconds |
| **Bulk CSV Batch Throughput** | > 10 docs / sec | **12.5 docs / sec** | < 2.0 docs / sec |
| **Gemini AI Ingestion Latency** | < 3.0 seconds | **1.80 – 2.20 seconds** | > 8.0 seconds |
| **Dynamic QR Expiry Precision**| Exactly 60 seconds | **60.00s $\pm 0.05$s** | $\Delta > 2.0$ seconds |
| **Idle Session Timeout** | Exactly 300 seconds | **300.00s** | Active past 305s |
| **PBKDF2 Password Rounds** | 100,000 iterations | **100,000 rounds** | < 100,000 rounds |
| **Gas Fee per Transaction** | ₹0.00 / $0.00 | **₹0.00 (Zero Gas)** | Any non-zero cost |

---

## 6. Regulatory & Compliance Standards

- **NEP 2020 (National Education Policy):** Adheres to credit mobility, multi-disciplinary exits, and permanent digital transcript archiving.
- **UGC (University Grants Commission) Norms:** Validates degrees against accredited university domains and official registrar signatories.
- **IT Act 2000 & Digital Personal Data Protection Act (DPDP 2023):** Implements selective disclosure, role-based data isolation, student notification consent, and local data residency.
- **NIST FIPS 180-4 (Secure Hash Standard):** SHA-256 for all block headers, credential digests, and tamper heatmaps.
- **RFC 2104 (HMAC):** HMAC-SHA256 for time-boxed dynamic QR tokens and session authentication.

---

## 7. Release Roadmap

- **Phase 1 (M1–M4) [COMPLETED]:** Core PoW consensus, tri-portal architecture, bulk CSV engine, dynamic QR codes, Gemini AI integration, adversarial hardening test harness.
- **Phase 2 (Current Release) [COMPLETED]:** MCP JSON-RPC 2.0 server for autonomous evaluation agents, multi-node P2P consensus, AES-256 PDF encryption, and production documentation suite.
- **Phase 3 (Post-Hackathon):** Polygon L2 state-root periodic rollup anchoring (zero gas to universities, periodic state commitment on public L2 for global cross-border recognition).
