# Satyameva Aegis — API Reference & Interface Contracts (API.md)

> **Document Version:** 2.4.0 • **Protocol:** RESTful HTTPS + JSON-RPC 2.0  
> **Content-Types:** `application/json`, `multipart/form-data`, `text/csv`  
> **Security Schemes:** Cookie Session (`satyameva_session`), Asymmetric ECDSA Signatures

---

## 1. Authentication & Security Headers

All authenticated endpoints require an active session cookie established via `/login` or OAuth callback.

### Common Security Response Headers
```http
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Set-Cookie: session=...; HttpOnly; SameSite=Lax; Path=/
```

### Standard Error Response Envelope
```json
{
  "ok": false,
  "error": "Error description string",
  "code": 400
}
```

---

## 2. Public Verification Gateway Endpoints

### 2.1 Public Permitted Verification Query
- **Endpoint:** `GET /v/<doc_hash>`
- **Query Parameters:**
  - `t` (Optional): Dynamic 60-second HMAC QR token (`<expires_at>.<sig>`).
- **Description:** Verifies credential authenticity directly against the decentralized blockchain ledger.
- **Response HTML View:**
  - `RESULT_VALID`: Displays student name, roll number, issuing university, block index, verification count, and timestamp.
  - `RESULT_NOT_FOUND`: Displays warning banner: *"No such credential on the Satyameva ledger. This document is not authentic."* Student identity withheld.
  - `RESULT_QR_EXPIRED`: Displays warning banner: *"This QR code has expired. Ask the student for a freshly generated code."* Student identity withheld.
  - `RESULT_TAMPERED`: Displays critical red alert: *"Integrity check failed — the stored record does not match its blockchain hash."*
  - `RESULT_REVOKED`: Displays revocation alert with official issuer rationale.

### 2.2 Instant Hash Verification Search
- **Endpoint:** `POST /verify`
- **Request Body (Form-Encoded):**
  - `doc_hash`: 64-character hexadecimal SHA-256 string.
- **Success Response:** HTTP 302 Redirect to `/v/<doc_hash>`.
- **Validation Failure Response:** HTTP 200 re-rendering `/verify` with flash alert: *"Please enter a valid credential hash."*

---

## 3. Student Portal Endpoints (`/student`)

### 3.1 Dynamic QR Code Payload
- **Endpoint:** `GET /student/document/<id>/qr.json`
- **Authentication:** Student session required (must own document `<id>`).
- **Response Body (`application/json`):**
```json
{
  "ok": true,
  "token": "1793043800.7f89b6a12c45e89d",
  "expires_at": 1793043800,
  "ttl_remaining": 60,
  "verify_url": "http://127.0.0.1:5000/v/ec5aa41fc397c22c...?t=1793043800.7f89b6a12c45e89d",
  "qr_data_uri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### 3.2 Dynamic QR PNG Stream
- **Endpoint:** `GET /student/document/<id>/qr.png`
- **Response:** Raw binary image `image/png` containing high-contrast modules with embedded central campus crest.

### 3.3 Download Official Stamped PDF
- **Endpoint:** `GET /student/document/<id>/download`
- **Response Headers:**
  - `Content-Type: application/pdf`
  - `Content-Disposition: attachment; filename="certificate_<roll_number>.pdf"`
- **Security:** Encrypted with student Date of Birth (`DDMMYYYY`) via AES-256 if DOB is configured.

### 3.4 Live Blockchain Consensus Audit
- **Endpoint:** `GET /student/chain/validate`
- **Response Body (`application/json`):**
```json
{
  "ok": true,
  "message": "Chain intact — 7 blocks verified.",
  "length": 7,
  "head_hash": "ec5aa41fc397c22c2e12462bfab090622c8d4811ad8fd204a934545a84bfdbe1"
}
```

---

## 4. Issuer Portal Endpoints (`/issuer`)

### 4.1 Single Credential Issuance
- **Endpoint:** `POST /issuer/issue`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file`: Credential document (PDF, PNG, JPG).
  - `student_roll`: Student enrollment/roll number.
  - `student_name`: Student full legal name.
  - `student_email`: Student email address.
  - `doc_type`: `DEGREE`, `MARKSHEET`, `TC`, `MIGRATION`, `BONAFIDE`, `INTERNSHIP`.
  - `title`: Credential title string.
  - `validity_days`: Optional integer (validity period in days).
- **Processing Flow:**
  1. Derives 16-byte random salt and raw file SHA-256 digest.
  2. Calculates canonical metadata hash: $H_{doc}$.
  3. Signs hash with issuer's private `secp256k1` key.
  4. Mines new PoW block at difficulty $D=4$.
  5. Inserts into database, writes `instance/blockchain.json`, dispatches student SMTP notification.

### 4.2 AI Multimodal Document Ingestion (Gemini 2.0 Flash)
- **Endpoint:** `POST /issuer/extract-ai`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `document_file`: Uploaded PDF or image scan.
- **Response Body (`application/json`):**
```json
{
  "ok": true,
  "data": {
    "student_name": "Praneeth Sai",
    "roll_number": "22103050",
    "student_email": "praneethsai050@gmail.com",
    "doc_type": "DEGREE",
    "title": "Bachelor of Technology in Computer Science & Engineering",
    "institution": "Jaypee University of Information Technology",
    "dob": "01092008"
  }
}
```

### 4.3 Bulk CSV Credential Issuance
- **Endpoint:** `POST /issuer/bulk-issue`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `csv_file`: Uploaded `.csv` file.
- **CSV Required Columns:** `roll_number`, `doc_type`, `title`.
- **CSV Optional Columns:** `student_name`, `validity_days`, `extra_fields`.
- **Transactional Guarantee:**
  - **All-or-Nothing:** If row $N$ fails validation, 0 documents are created, 0 blocks are mined. Returns HTTP 400 with row errors.
  - **Success:** Redirects to `/issuer/dashboard` with flash message: *"Successfully issued N credentials in bulk."*

### 4.4 Sample CSV Template Download
- **Endpoint:** `GET /issuer/sample-csv` and `GET /issuer/template.csv`
- **Response Headers:**
  - `Content-Type: text/csv; charset=utf-8`
  - `Content-Disposition: attachment; filename="template.csv"`

---

## 5. Corporate Verifier Endpoints (`/verifier`)

### 5.1 Batch Verification Engine
- **Endpoint:** `POST /verifier/batch`
- **Request Body (JSON or Form):**
  - `hashes`: Comma- or newline-separated list of 64-character SHA-256 hashes.
- **Response Body (`application/json`):**
```json
{
  "total_queried": 2,
  "valid_count": 2,
  "results": [
    {
      "hash": "dd7d0a1788dca4c9...",
      "status": "VALID",
      "student_name": "Praneeth Sai",
      "roll_number": "22103050",
      "title": "Bachelor of Technology in Computer Science & Engineering",
      "block_index": 1
    },
    {
      "hash": "8ddff68da2b10ede...",
      "status": "VALID",
      "student_name": "Praneeth Sai",
      "roll_number": "22103050",
      "title": "Consolidated Grade Marksheet",
      "block_index": 2
    }
  ]
}
```

### 5.2 Submit Fraud Telemetry Report
- **Endpoint:** `POST /verifier/report-fraud`
- **Request Body (JSON or Form):**
  - `doc_hash`: Target 64-character hash.
  - `reason`: Explanation of forgery/tampering.
  - `reporter_email`: Contact email address.
- **Response Body:**
```json
{
  "ok": true,
  "report_id": 14,
  "status": "PENDING",
  "message": "Fraud report submitted to forensic registry."
}
```

---

## 6. P2P Multi-Node Consensus API (`/blockchain`)

### 6.1 Retrieve Full Local Blockchain
- **Endpoint:** `GET /blockchain/chain`
- **Response Body (`application/json`):**
```json
{
  "status": "ok",
  "length": 7,
  "chain": [
    {
      "index": 0,
      "timestamp": "2026-10-26T19:34:52.000Z",
      "data": "{\"chain\":\"satyameva\",\"genesis\":true}",
      "proof": 1,
      "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000",
      "hash": "b7399ea3af7cb120..."
    },
    {
      "index": 1,
      "timestamp": "2026-10-26T19:34:52.200Z",
      "data": "{\"doc_hash\":\"dd7d0a1788dca4c9...\"}",
      "proof": 48291,
      "previous_hash": "b7399ea3af7cb120...",
      "hash": "0000a184e93d..."
    }
  ]
}
```

### 6.2 Register Peer Blockchain Nodes
- **Endpoint:** `POST /blockchain/nodes/register`
- **Request Body (`application/json`):**
```json
{
  "nodes": ["http://192.168.1.101:5000", "http://jiit-node.satyameva.in:5000"]
}
```
- **Response Body:**
```json
{
  "message": "Registered 2 new nodes.",
  "registered": ["http://192.168.1.101:5000", "http://jiit-node.satyameva.in:5000"],
  "total_nodes": ["http://192.168.1.101:5000", "http://jiit-node.satyameva.in:5000"]
}
```

### 6.3 Run Consensus Conflict Resolution
- **Endpoint:** `GET /blockchain/resolve` or `POST /blockchain/resolve`
- **Response Body:**
```json
{
  "replaced": false,
  "message": "Our chain is authoritative.",
  "length": 7
}
```
