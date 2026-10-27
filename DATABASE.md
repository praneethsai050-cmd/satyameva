# Satyameva Aegis — Database Architecture & Schema Specification (DATABASE.md)

> **Document Version:** 2.4.0 • **RDBMS:** SQLite3 (WAL Mode Enabled) + Dual JSON Ledger Sync  
> **ORM Layer:** SQLAlchemy 2.0 / Flask-SQLAlchemy 3.1 • **Data Invariant:** Zero Untracked State

---

## 1. Overview & Storage Engine Architecture

Satyameva Aegis utilizes an ACID-compliant relational schema paired with a decentralized file-based cryptographic ledger. 

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SATYAMEVA STORAGE TOPOLOGY                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Relational Database (`instance/satyameva.db`):                      │
│    • SQLite 3.40+ operating in Write-Ahead Logging (WAL) mode          │
│    • Enforces foreign key constraints, unique indexes, and cascades    │
│    • Stores user identities, salted hashes, documents, and audit logs  │
│                                                                        │
│ 2. Decentralized JSON Ledger (`instance/blockchain.json`):             │
│    • File-backed serialization of all mined PoW blocks                 │
│    • Human-readable, portable cryptographic ledger for external audit  │
│    • Synchronized atomically with the `block` table                    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Entity-Relationship Diagram (ERD)

```
       ┌─────────────────┐
       │   INSTITUTION   │
       │─────────────────│
       │ id (PK)         │◄──────────────┐
       │ short_code (UQ) │               │
       │ name            │               │
       │ domain          │               │
       │ is_approved     │               │
       └────────┬────────┘               │
                │ 1                      │ 1
                │                        │
                │ *                      │ *
       ┌────────┴────────┐      ┌────────┴────────┐
       │      USER       │      │   CREDENTIAL    │
       │─────────────────│      │     REQUEST     │
       │ id (PK)         │      │─────────────────│
       │ username (UQ)   │      │ id (PK)         │
       │ email (UQ)      │      │ student_id (FK) │
       │ role            │      │ institution_id  │
       │ password_hash   │      │ doc_type        │
       │ password_salt   │      │ status          │
       │ public_key      │      └─────────────────┘
       └────────┬────────┘
                │ 1
                │
                │ 1
       ┌────────┴────────┐
       │     STUDENT     │
       │─────────────────│
       │ id (PK)         │
       │ user_id (FK, UQ)│
       │ roll_number (UQ)│◄──────────────┐
       │ full_name       │               │
       │ program         │               │
       │ dob             │               │
       └────────┬────────┘               │
                │ 1                      │
                │                        │
                │ *                      │
       ┌────────┴────────┐               │
       │       DOC       │               │
       │─────────────────│               │
       │ id (PK)         │               │
       │ student_id (FK) │               │
       │ issuer_id (FK)  │               │
       │ doc_hash (UQ)   │◄───────┐      │
       │ hash_salt       │        │      │
       │ doc_type        │        │      │
       │ title           │        │      │
       │ block_index     │        │      │
       │ signature       │        │      │
       │ revoked         │        │      │
       └────────┬────────┘        │      │
                │ 1               │      │
                │                 │      │
        ┌───────┴───────┐         │      │
        │               │         │      │
        ▼ *             ▼ *       │ *    │ *
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ VERIFICATION  │ │ NOTIFICATION  │ │ FRAUD_REPORT  │ │     BLOCK     │
│      LOG      │ │               │ │               │ │ (Ledger)      │
│───────────────│ │───────────────│ │───────────────│ │───────────────│
│ id (PK)       │ │ id (PK)       │ │ id (PK)       │ │ id (PK)       │
│ doc_id (FK)   │ │ student_id(FK)│ │ doc_id (FK)   │ │ index (UQ)    │
│ queried_hash  │ │ doc_id (FK)   │ │ doc_hash      │ │ hash (UQ)     │
│ result        │ │ title         │ │ reason        │ │ previous_hash │
│ method (QR/H) │ │ message       │ │ status        │ │ proof (nonce) │
│ timestamp     │ │ is_read       │ │ timestamp     │ │ doc_hash      │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘
```

---

## 3. Complete Schema Definitions & Field Specifications

### 3.1 Table: `institution`
Represents an authorized higher education institution (e.g. JIIT Noida, JUIT Waknaghat, JUET Guna).

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique institution ID |
| `name` | `VARCHAR(180)` | `NOT NULL` | Full university name |
| `short_code` | `VARCHAR(20)` | `UNIQUE, NOT NULL, INDEX` | Campus code (`JIIT`, `JUIT`, `JUET`) |
| `domain` | `VARCHAR(120)` | `NOT NULL` | Official academic domain (e.g. `juit.ac.in`) |
| `address` | `VARCHAR(255)` | `NULLABLE` | Physical campus location |
| `is_approved` | `BOOLEAN` | `DEFAULT FALSE, NOT NULL` | Administrator approval flag |
| `approved_at` | `DATETIME` | `NULLABLE` | Timestamp of administrator approval |
| `approved_by_id` | `INTEGER` | `FK(user.id), NULLABLE` | Admin who approved campus |
| `subscription_expires_at` | `DATETIME` | `NULLABLE` | Annual SaaS license expiration |
| `created_at` | `DATETIME` | `DEFAULT utcnow, NOT NULL` | Creation timestamp |

### 3.2 Table: `user`
Master table for all system actors across the 4 core roles (`student`, `issuer`, `verifier`, `admin`).

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique user account ID |
| `username` | `VARCHAR(80)` | `UNIQUE, NOT NULL, INDEX` | Login handle or student roll number |
| `email` | `VARCHAR(120)` | `UNIQUE, NOT NULL, INDEX` | Normalized lowercase email address |
| `password_hash` | `VARCHAR(128)` | `NOT NULL` | Hex-encoded PBKDF2-HMAC-SHA256 digest |
| `password_salt` | `VARCHAR(64)` | `NOT NULL` | Hex-encoded 32-byte cryptographically random salt |
| `password_iterations`| `INTEGER` | `DEFAULT 100000, NOT NULL`| Iteration count for PBKDF2 key derivation |
| `role` | `VARCHAR(20)` | `DEFAULT 'student', INDEX` | Role flag: `student`, `issuer`, `verifier`, `admin` |
| `organization` | `VARCHAR(150)` | `NULLABLE` | Associated institution or BGV employer |
| `institution_id` | `INTEGER` | `FK(institution.id), INDEX`| Bound institution for registrars/students |
| `created_at` | `DATETIME` | `DEFAULT utcnow, NOT NULL` | Account registration timestamp |
| `last_login_at` | `DATETIME` | `NULLABLE` | Most recent successful authentication |
| `oauth_provider` | `VARCHAR(30)` | `NULLABLE` | `google` or `microsoft` if OAuth enabled |
| `oauth_sub` | `VARCHAR(256)` | `NULLABLE` | Unique subject identifier from OAuth provider |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE, NOT NULL` | Account active state |
| `public_key` | `TEXT` | `NULLABLE` | 130-char uncompressed secp256k1 public key |
| `private_key` | `TEXT` | `NULLABLE` | 64-char hex-encoded secp256k1 private key |

### 3.3 Table: `student`
Extended academic profile linked 1:1 with a student `user`.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique student record ID |
| `user_id` | `INTEGER` | `FK(user.id), UNIQUE, NOT NULL`| 1:1 link to master user record |
| `full_name` | `VARCHAR(120)` | `NOT NULL` | Legal full student name |
| `roll_number` | `VARCHAR(40)` | `UNIQUE, NOT NULL, INDEX` | University roll / enrollment number |
| `department` | `VARCHAR(120)` | `NULLABLE` | Academic department (e.g. CSE) |
| `program` | `VARCHAR(120)` | `NULLABLE` | Degree program (e.g. B.Tech CSE) |
| `batch` | `VARCHAR(40)` | `NULLABLE` | Academic graduation cohort (e.g. 2026-2030) |
| `institution` | `VARCHAR(150)` | `NULLABLE` | College or university name |
| `dob` | `VARCHAR(20)` | `NULLABLE` | Date of Birth (format: `YYYY-MM-DD` or `DDMMYYYY`) |
| `email_verified` | `BOOLEAN` | `DEFAULT FALSE, NOT NULL` | Email verification flag |
| `issuer_approved`| `BOOLEAN` | `DEFAULT FALSE, NOT NULL` | University registrar approval flag |
| `created_at` | `DATETIME` | `DEFAULT utcnow, NOT NULL` | Profile creation timestamp |

### 3.4 Table: `doc` (Academic Credentials)
The core immutable credential record.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique credential ID |
| `student_id` | `INTEGER` | `FK(student.id), INDEX, NOT NULL`| Credential recipient student |
| `issuer_id` | `INTEGER` | `FK(user.id), NULLABLE` | University registrar who issued document |
| `doc_type` | `VARCHAR(30)` | `NOT NULL, DEFAULT 'DEGREE'`| Type: `DEGREE`, `MARKSHEET`, `TC`, etc. |
| `title` | `VARCHAR(160)` | `NOT NULL` | Full credential title |
| `issuer_name` | `VARCHAR(150)` | `NULLABLE` | Denormalized issuing institution name |
| `doc_hash` | `VARCHAR(64)` | `UNIQUE, INDEX, NOT NULL` | 64-char SHA-256 cryptographic document hash |
| `hash_salt` | `VARCHAR(64)` | `NOT NULL` | 32-char hex random per-record salt |
| `file_digest` | `VARCHAR(64)` | `NULLABLE` | Raw SHA-256 digest of original uploaded file |
| `payload` | `TEXT` | `NULLABLE` | Canonical metadata JSON |
| `file_data` | `BLOB` | `NULLABLE` | Binary file storage (PNG, PDF) |
| `file_name` | `VARCHAR(255)` | `NULLABLE` | Original uploaded filename |
| `file_mime` | `VARCHAR(100)` | `NULLABLE` | MIME type (e.g. `image/png`, `application/pdf`)|
| `issued_on` | `DATETIME` | `DEFAULT utcnow, NOT NULL` | Date and time credential was anchored |
| `valid_until` | `DATETIME` | `NULLABLE` | Expiration date (`NULL` for permanent degrees)|
| `is_stamped` | `BOOLEAN` | `DEFAULT FALSE, NOT NULL` | Digital seal stamp status |
| `block_index` | `INTEGER` | `NULLABLE, INDEX` | Mined blockchain block index containing hash |
| `tx_hash` | `VARCHAR(80)` | `NULLABLE` | Transaction reference hash |
| `signature` | `VARCHAR(130)` | `NULLABLE` | 128-char secp256k1 digital signature |
| `issuer_public_key`| `TEXT` | `NULLABLE` | Public key used to verify credential signature |
| `verification_count`| `INTEGER`| `DEFAULT 0, NOT NULL` | Total times verified globally |
| `last_verified_at`| `DATETIME` | `NULLABLE` | Most recent verification timestamp |
| `revoked` | `BOOLEAN` | `DEFAULT FALSE, NOT NULL` | Revocation status flag |
| `revoked_reason` | `VARCHAR(255)`| `NULLABLE` | Legal justification for credential revocation |

### 3.5 Table: `block` (Blockchain Ledger)
The on-chain block ledger.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Internal database row ID |
| `index` | `INTEGER` | `UNIQUE, NOT NULL, INDEX` | Monotonically increasing block height (0, 1, 2...)|
| `timestamp` | `DATETIME` | `NOT NULL` | Block creation timestamp |
| `data` | `TEXT` | `NOT NULL` | JSON string containing anchored transactions |
| `proof` | `BIGINT` | `NOT NULL` | Nonce discovered during Proof-of-Work mining |
| `hash` | `VARCHAR(64)` | `NOT NULL` | SHA-256 hash of this block |
| `previous_hash` | `VARCHAR(64)` | `NOT NULL` | SHA-256 hash of preceding block |
| `doc_hash` | `VARCHAR(64)` | `NULLABLE, INDEX` | Document hash anchored in this block |
| `signature` | `VARCHAR(130)` | `NULLABLE` | Miner digital signature of block hash |
| `miner_public_key` | `TEXT` | `NULLABLE` | Public key of the node that mined the block |

### 3.6 Table: `verification_log`
Forensic audit trail capturing all verification events.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique audit log ID |
| `doc_id` | `INTEGER` | `FK(doc.id), NULLABLE, INDEX`| Verified credential (if found) |
| `verifier_id` | `INTEGER` | `FK(user.id), NULLABLE` | Authenticated verifier account ID |
| `verifier_label`| `VARCHAR(120)`| `NULLABLE` | Human-readable company/verifier name |
| `queried_hash` | `VARCHAR(64)` | `NOT NULL, INDEX` | Hash string submitted to the verification engine |
| `result` | `VARCHAR(30)` | `NOT NULL` | `VALID`, `EXPIRED`, `REVOKED`, `TAMPERED`, `NOT_FOUND` |
| `method` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'HASH'`| Method: `HASH`, `QR`, or `API` |
| `ipv4` | `VARCHAR(45)` | `NULLABLE` | Client IPv4 address |
| `ipv6` | `VARCHAR(45)` | `NULLABLE` | Client IPv6 address |
| `user_agent` | `VARCHAR(255)`| `NULLABLE` | Client browser or API user-agent string |
| `timestamp` | `DATETIME` | `DEFAULT utcnow, NOT NULL` | Audit timestamp |

### 3.7 Table: `notification`
In-app student verification alerts.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique notification ID |
| `student_id` | `INTEGER` | `FK(student.id), INDEX, NOT NULL`| Recipient student |
| `doc_id` | `INTEGER` | `FK(doc.id), NULLABLE` | Associated credential |
| `title` | `VARCHAR(120)` | `NOT NULL` | Notification subject heading |
| `message` | `TEXT` | `NOT NULL` | Detailed verification alert message |
| `category` | `VARCHAR(30)` | `DEFAULT 'info'` | Alert level: `info`, `success`, `warning`, `danger`|
| `verifier_label`| `VARCHAR(120)`| `NULLABLE` | Name of auditing organization |
| `is_read` | `BOOLEAN` | `DEFAULT FALSE, NOT NULL` | Read/unread flag |
| `created_at` | `DATETIME` | `DEFAULT utcnow, NOT NULL` | Timestamp alert was generated |

### 3.8 Table: `fraud_report`
Registry of reported fraudulent credentials and forensic tamper alerts.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique report ID |
| `doc_id` | `INTEGER` | `FK(doc.id), NULLABLE` | Linked document if found |
| `doc_hash` | `VARCHAR(64)` | `NOT NULL, INDEX` | Suspected counterfeit hash |
| `reported_by_id`| `INTEGER` | `FK(user.id), NULLABLE` | Reporting user (if authenticated) |
| `reporter_email`| `VARCHAR(120)`| `NULLABLE` | Contact email of whistleblower or employer |
| `reason` | `TEXT` | `NOT NULL` | Forensic description of tampering/forgery |
| `ip_address` | `VARCHAR(45)` | `NULLABLE` | Submitter IP address |
| `user_agent` | `VARCHAR(255)`| `NULLABLE` | Submitter browser signature |
| `status` | `VARCHAR(20)` | `DEFAULT 'PENDING'` | Triage state: `PENDING`, `INVESTIGATING`, `RESOLVED`|
| `created_at` | `DATETIME` | `DEFAULT utcnow, NOT NULL` | Report submission timestamp |

---

## 4. Database Initialization & Seeding Commands

```bash
# 1. Clean Production Initialization (JIIT, JUIT, JUET campuses + Master Admin)
python init_db.py

# 2. Comprehensive 4-Role Seeding with JUIT Credentials for Praneeth Sai (Roll: 22103050)
python seed.py --reset
```
