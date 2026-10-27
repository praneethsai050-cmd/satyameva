# Satyameva Aegis — Technical Architecture Specification (ARCHITECTURE.md)

> **Document Version:** 2.4.0 • **Consensus Engine:** Custom SHA-256 Proof-of-Work (PoW)  
> **Cryptographic Core:** PBKDF2-HMAC-SHA256 / secp256k1 ECDSA / HMAC-SHA256 Dynamic Tokens  
> **Runtime Environment:** Python 3.14 + Flask 3.0 + SQLite (WAL Mode) + JSON Ledger

---

## 1. System Topology & Architectural Overview

Satyameva Aegis is engineered with a layered, decoupled service architecture designed for zero transaction fees, sub-second verification latency, and zero-trust tamper resistance.

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                                CLIENT ACCESS LAYER                                │
├─────────────────────────┬─────────────────────────┬───────────────────────────────┤
│    🎓 STUDENT WALLET    │   🏛️ ISSUER REGISTRAR   │   🔍 VERIFIER (HR/PUBLIC)     │
│   (3D WebGL / Dynamic)  │   (Bulk CSV / AI OCR)   │   (Instant Search / QR Scan)  │
└────────────┬────────────┴────────────┬────────────┴───────────────┬───────────────┘
             │                         │                            │
             ▼                         ▼                            ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION & ROUTING LAYER                             │
├───────────────────────────────────────────────────────────────────────────────────┤
│ Flask 3.0 App Factory • Blueprints (auth, student, issuer, verifier, public, mcp) │
│ Zero-Trust RBAC Decorators • 5-Minute Inactivity Session Engine • CSRF Protection │
└────────────┬─────────────────────────┬────────────────────────────┬───────────────┘
             │                         │                            │
             ▼                         ▼                            ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                             INTELLIGENCE & AI LAYER                               │
├───────────────────────────────────────────────────────────────────────────────────┤
│ Google Gemini 2.0 Flash Multimodal Vision • Automated Marksheet & Degree Parser   │
│ Schema Normalizer • High-Resolution Procedural Vector Crest Generator (4x Lanczos)│
└────────────┬─────────────────────────┬────────────────────────────┬───────────────┘
             │                         │                            │
             ▼                         ▼                            ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           CORE CRYPTOGRAPHIC ENGINE                               │
├───────────────────────────────────────────────────────────────────────────────────┤
│ PBKDF2-HMAC-SHA256 (100k rounds) • Pure-Python secp256k1 ECDSA Signatures        │
│ Canonical JSON Serializer • Anti-Replay HMAC-SHA256 60s Dynamic QR Tokens         │
└────────────┬─────────────────────────┬────────────────────────────┬───────────────┘
             │                         │                            │
             ▼                         ▼                            ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                      PROOF-OF-WORK CONSENSUS & LEDGER LAYER                       │
├───────────────────────────────────────────────────────────────────────────────────┤
│ Custom PoW Mining Engine (Difficulty: 4) • Merkle-Root Block Sealer               │
│ P2P Multi-Node Consensus Endpoints • Longest Valid Chain Conflict Resolution      │
└────────────┬──────────────────────────────────────────────────────┬───────────────┘
             │                                                      │
             ▼                                                      ▼
┌───────────────────────────────────────────┐      ┌────────────────────────────────┐
│         RELATIONAL DATABASE (WAL)         │      │     DECENTRALIZED JSON LEDGER  │
│  SQLite3: `instance/satyameva.db`         │◄────►│  `instance/blockchain.json`    │
│  (Users, Documents, Blocks, Audit Logs)   │      │  (Immutable Public Block Walk) │
└───────────────────────────────────────────┘      └────────────────────────────────┘
```

---

## 2. Cryptographic Specifications & Mathematical Formulations

### 2.1 Canonical Payload Serialization
To guarantee that identical credential metadata produces byte-identical hashes across heterogeneous operating systems (Windows, Linux, macOS), the metadata dictionary is strictly normalized using RFC-8785 canonical rules:

$$\text{Canonical}(M) = \text{json.dumps}(M, \text{sort\_keys}=\text{True}, \text{separators}=(',', ':'), \text{default}=\text{str})$$

### 2.2 Dual-Layer Salted Document Hash
Every credential is sealed with a unique, cryptographically secure 16-byte random salt generated at issuance. The document hash binds the raw binary digest, metadata, and salt into a single irreversible SHA-256 string:

$$H_{doc} = \text{SHA-256}\Big(\text{Salt}_{16} \parallel \text{SHA-256}(FileBytes) \parallel \text{Canonical}(Metadata)\Big)$$

If the credential is text-only (e.g. bulk CSV issuance without uploaded images), $\text{SHA-256}(FileBytes)$ evaluates to the canonical string `'no-file'`.

### 2.3 Custom Proof-of-Work (PoW) Consensus Formula
Mining a new block requires discovering a positive integer nonce $P$ (proof) satisfying the cryptographic difficulty constraint:

$$\text{SHA-256}\Big(P_{prev} \parallel P \parallel Index\Big) < \text{Target}$$

At standard difficulty $D=4$, the target requires **4 leading hexadecimal zeros** (`0000...`):

$$\text{Target} = 16^{64 - 4} = 16^{60}$$

#### Block Header Digest Calculation
$$\text{Block\_Hash} = \text{SHA-256}\Big(Index \parallel Timestamp_{ISO} \parallel Data_{canonical} \parallel Proof \parallel Previous\_Hash\Big)$$

Every block commits immutably to its parent block via `Previous_Hash`. Block #0 (Genesis) fixes `Previous_Hash` to:
$$\text{Previous\_Hash}_{\text{genesis}} = 0^{64} = \text{"0000000000000000000000000000000000000000000000000000000000000000"}$$

### 2.4 Asymmetric secp256k1 Digital Signatures (ECDSA & Schnorr)
Satyameva implements asymmetric cryptography natively using Python's standard library without requiring external compiled C extensions (e.g., OpenSSL or libsecp256k1 binaries), ensuring 100% portable zero-dependency execution.

#### Curve Parameters
- **Elliptic Curve:** $y^2 = x^3 + 7 \pmod p$
- **Field Prime $p$:** $2^{256} - 2^{32} - 977 = \text{0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F}$
- **Group Order $n$:** $\text{0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141}$
- **Generator Point $G$:**
  $$G_x = \text{0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798}$$
  $$G_y = \text{0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8}$$

#### Keypair Generation
$$\text{Private Key: } d \in_R [1, n-2]$$
$$\text{Public Key: } Q = d \times G = (Q_x, Q_y)$$
$$\text{Public Key Hex: } \text{"04"} \parallel Q_x \parallel Q_y \quad (\text{130 characters})$$

#### Signature Generation
$$\text{Signature: } (r, s) \in [1, n-1]^2 \quad (\text{128 characters})$$

### 2.5 Replay-Resistant Dynamic QR Code Token Formulation
To prevent credential holders or third parties from taking a screenshot of a QR code and distributing it via messaging apps, dynamic QR codes incorporate a rolling HMAC token:

$$T_{\text{expiry}} = \lfloor \text{Time}() \rfloor + 60$$
$$\text{Sig} = \text{HMAC-SHA256}\Big(K_{\text{secret}}, H_{doc} \parallel T_{\text{expiry}}\Big)[:32]$$
$$\text{Token} = T_{\text{expiry}} \parallel "." \parallel \text{Sig}$$

Upon scan, the verification engine checks:
1. Valid HMAC signature using server master secret $K_{\text{secret}}$.
2. $\text{Time}() \le T_{\text{expiry}}$. If current time exceeds $T_{\text{expiry}}$, the check returns `RESULT_QR_EXPIRED`.

---

## 3. Dual-Persistence & Self-Healing Ledger State

Satyameva implements an active dual-persistence ledger model:

```
┌─────────────────────────────────┐
│     BLOCKCHAIN MINING EVENT     │
└────────────────┬────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌───────────────┐ ┌───────────────┐
│ SQLite DB     │ │ JSON Ledger   │
│ `block` table │ │ `instance/    │
│               │ │  blockchain   │
│               │ │  .json`       │
└───────┬───────┘ └───────┬───────┘
        │                 │
        └────────┬────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│      `validate_chain()`         │
│  • Cross-diffs both stores      │
│  • Self-heals JSON from DB      │
│  • Self-heals DB from JSON      │
└─────────────────────────────────┘
```

### Self-Healing Logic
- **Scenario A (Missing or Corrupted JSON File):** When `validate_chain()` runs, if `blockchain.json` is deleted or contains corrupted bytes, the engine reads all verified blocks from the SQLite `block` table and rewrites the JSON file atomically.
- **Scenario B (Database Reset with Existing Ledger):** If the SQLite database is re-initialized while `blockchain.json` contains a valid historical chain, the engine detects the difference and reconstructs the SQLite records from the authoritative ledger file.

---

## 4. Multi-Node P2P Consensus Architecture

The Satyameva network enables decentralized multi-campus operation through an HTTP gossip consensus protocol:

```
┌────────────────────┐     Register Nodes     ┌────────────────────┐
│   JIIT NOIDA NODE  │───────────────────────►│  JUIT WAKNAGHAT    │
│ (Port 5000)        │◄───────────────────────│  NODE (Port 5001)  │
└─────────┬──────────┘                        └─────────┬──────────┘
          │                                             │
          │             GET /blockchain/chain           │
          └──────────────────────┬──────────────────────┘
                                 ▼
                     ┌───────────────────────┐
                     │   LONGEST VALID CHAIN │
                     │   CONFLICT RESOLUTION │
                     │   (`resolve_conflicts`)
                     └───────────────────────┘
```

### Nakamoto Consensus Algorithm
When a node calls `resolve_conflicts()`:
1. Queries all registered peer nodes via `GET /blockchain/chain`.
2. Inspects remote chain lengths: only chains strictly longer than the local chain are evaluated.
3. Re-computes every block hash and proof-of-work nonce across the remote candidate chain.
4. If a longer valid chain is discovered, the local node swaps its database and JSON ledger to the remote authoritative chain.

---

## 5. Security Threat Modeling & STRIDE Analysis

| Threat Class (STRIDE) | Attack Vector / Injection | Defense Invariant Implemented in Satyameva |
| :--- | :--- | :--- |
| **Spoofing** | Forged registrar issuing degrees | Asymmetric secp256k1 keypair assigned to verified institutions; signature verified on each audit. |
| **Tampering** | Mutating student grade in database row | Recomputed hash $H_{recompute} = \text{SHA-256}(Salt \parallel Digest \parallel Payload) \ne H_{doc}$; triggers `RESULT_TAMPERED`. |
| **Repudiation** | Institution denies issuing a degree | Non-repudiable on-chain block commitment containing issuer ID, timestamp, and signature. |
| **Information Disclosure** | Scraping student PII via brute-force hash scanning | Selective disclosure: invalid or expired lookups redact student identity completely. |
| **Denial of Service** | Flooding heavy mining operations | All-or-nothing batch pre-validation; PoW difficulty bound; session rate limits. |
| **Elevation of Privilege** | Student modifying issuer approval endpoints | Strict `@role_required('issuer', 'admin')` decorator triggering hard HTTP 403. |

---

## 6. Containerization & Deployment Spec

### Docker Compose Architecture
- **Web Node:** Python 3.14 on `python:3.14-slim` base image.
- **Port:** Exposed on host port `5000` (`http://localhost:5000`).
- **Volumes:** Persistent volume mount for `instance/` holding `satyameva.db` and `blockchain.json`.
- **Environment:** Strict production environment flags (`FLASK_DEBUG=0`, `SESSION_COOKIE_SECURE=True`).
