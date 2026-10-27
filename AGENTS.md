# Satyameva Aegis — AI Agents & MCP Architecture (AGENTS.md)

> **Document Version:** 2.4.0 • **Protocol Standard:** Model Context Protocol (MCP) JSON-RPC 2.0  
> **Multimodal Vision Model:** Google Gemini 2.0 Flash (`gemini-2.0-flash`)  
> **Autonomous Agent Runtime:** Stdio Transport / Python 3.14 Subprocess

---

## 1. Overview & Agentic Architecture

Satyameva Aegis is engineered from the ground up to support autonomous AI auditing agents, background verification robots, and LLM-driven compliance checkers. Rather than requiring brittle web scrapers or human UI interaction, Satyameva natively implements the **Model Context Protocol (MCP)** specification.

Through MCP, any external LLM agent (e.g. Claude Desktop, Google Antigravity, Cursor, or custom enterprise BGV agents) can directly query the decentralized blockchain, inspect block nonces, audit student credential portfolios, file fraud reports, and extract marksheet metadata.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL AGENT ECOSYSTEM                        │
├─────────────────────┬─────────────────────┬────────────────────────────┤
│   Claude Desktop    │  Google Antigravity │  Custom BGV Auditor Agent  │
└──────────┬──────────┴──────────┬──────────┴──────────────┬─────────────┘
           │                     │                         │
           ▼                     ▼                         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 MODEL CONTEXT PROTOCOL (JSON-RPC 2.0)                  │
│                     Transport: `stdio` Subprocess                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Handshake:    `initialize`, `notifications/initialized`              │
│ • Tool Call:    `tools/list`, `tools/call`                             │
│ • Resources:    `resources/list`, `resources/read`                     │
│ • Prompts:      `prompts/list`, `prompts/get`                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│              SATYAMEVA AEGIS CORE MCP SERVER (`mcp_server.py`)         │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Cryptographic Verification Engine (`verify_credential`)             │
│ 2. PoW Consensus Telemetry (`get_blockchain_info`, `get_block_by_index`)│
│ 3. Student Credential Portfolio Audit (`audit_student_records`)        │
│ 4. Forensic Fraud Registry Dispatch (`submit_fraud_report`)            │
│ 5. Google Gemini 2.0 Flash Multimodal OCR (`extract_academic_document`) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      BLOCKCHAIN & DATABASE INVARIANTS                  │
│   SQLite3 Database • JSON Blockchain Ledger • Asymmetric Signatures    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Model Context Protocol (MCP) Server Specification

The MCP server is implemented in `mcp_server.py`. It operates via standard input/output (`stdio`), ensuring complete platform independence across Windows, Linux, and macOS without port conflicts.

### 2.1 Available MCP Tools

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `verify_credential` | `doc_hash` (str, req), `qr_token` (str, opt) | Cryptographically verifies a credential hash or 60s dynamic QR token against the blockchain. Returns authenticity verdict, block index, student details, and digital signature status. |
| `get_blockchain_info`| *(None)* | Returns total blocks mined, difficulty ($D=4$), last block hash, consensus validation status (`validate_chain()`), and registered peer nodes. |
| `get_block_by_index` | `block_index` (int, req) | Returns full cryptographic block header, proof nonce, timestamp, previous hash pointer, and transaction doc hashes. |
| `audit_student_records`| `roll_number` (str, req) | Returns the student's complete academic portfolio, issuance history, and on-chain status for a university roll number. |
| `submit_fraud_report`| `doc_hash` (str, req), `reason` (str, req), `reporter_email` (str, opt) | Submits an immutable fraud alert to the national forensic audit queue. |
| `extract_academic_document`| `file_path` (str, req) | Triggers Google Gemini 2.0 Flash AI multimodal parsing on a local degree or marksheet PDF/image. |

### 2.2 Available MCP Resources

| Resource URI | MIME Type | Description |
| :--- | :--- | :--- |
| `satyameva://blockchain/ledger` | `application/json` | Full JSON blockchain ledger containing all mined blocks and transaction proofs. |
| `satyameva://institutions/registry` | `application/json` | Official registry of accredited campuses (JIIT, JUIT, JUET) and subscription status. |
| `satyameva://stats/telemetry` | `application/json` | Aggregated system metrics: total credentials anchored, verifications logged, and active nodes. |

### 2.3 Available MCP Prompt Templates

| Prompt Name | Arguments | Workflow Template |
| :--- | :--- | :--- |
| `audit_credential` | `doc_hash` (req) | Instructs the LLM to execute a deep cryptographic audit of `doc_hash`, verifying the proof walk to Genesis and evaluating tampering vectors. |
| `institution_compliance_check` | `short_code` (req) | Prompts the LLM to inspect campus accreditation, active subscription status, and digital signature keys for a given campus code (`JUIT`, `JIIT`, etc.). |

---

## 3. Google Gemini 2.0 Flash Multimodal AI Pipeline

Satyameva integrates Google Gemini 2.0 Flash (`gemini-2.0-flash`) via the modern `google-genai` SDK in `services/gemini_service.py`.

```
[ Uploaded PDF / Image ] 
           │
           ▼
[ `types.Part.from_bytes` ]
           │
           ▼
[ Gemini 2.0 Flash Vision API ]
   • Model: `gemini-2.0-flash`
   • Strict JSON Schema Instruction
   • Temperature: 0.1 (Deterministic)
           │
           ▼
[ Structured JSON Output ]
   • student_name: "Praneeth Sai"
   • roll_number:  "22103050"
   • doc_type:     "DEGREE"
   • title:        "Bachelor of Technology in CSE"
   • dob:          "01092008"
           │
           ▼
[ Auto-Populate Issuer Form ] ──► [ PoW Mining & Blockchain Anchoring ]
```

### 3.1 Model Cascade Architecture
To guarantee 99.99% availability during peak registration periods, the service implements an automated model cascade:
1. `gemini-2.0-flash`: Primary high-speed, multimodal vision reasoning model.
2. `gemini-2.5-flash`: Next-generation high-throughput fallback.
3. `gemini-1.5-flash`: High-context stable fallback.
4. `gemini-flash-latest`: Dynamic production alias.

### 3.2 System Prompt Design
```
You are an academic document parser for an Indian university verification system.
Extract the following fields from the provided document image or PDF:
- student_name: full legal name of the student
- roll_number: student roll / enrollment / registration number
- student_email: email address of the student if found on the document
- doc_type: one of DEGREE, MARKSHEET, TC, MIGRATION, BONAFIDE, or INTERNSHIP
- title: exact credential title (e.g. "Bachelor of Technology in Computer Science")
- institution: name of the issuing university or institute
- dob: date of birth of the student in DDMMYYYY format (e.g. 01011999). If not found, use ""

Respond ONLY with a valid JSON object in this exact format:
{"student_name": "...", "roll_number": "...", "student_email": "...", "doc_type": "...", "title": "...", "institution": "...", "dob": "..."}
```

---

## 4. MCP Agent Configuration & Integration Guide

### 4.1 Running the MCP Diagnostic Self-Test
Verify that all MCP tools, resources, and blockchain connections function seamlessly:
```bash
python mcp_server.py --test
```
*Expected Output:*
```text
====================================================
  Satyameva Aegis MCP Server Self-Diagnostic Suite  
====================================================
[1/5] Testing tool: get_blockchain_info...
      [OK] Total Blocks: 7 | Valid: True
[2/5] Testing tool: get_block_by_index #0 (Genesis)...
      [OK] Genesis Hash: b7399ea3af7cb120... | Proof: 1
[3/5] Testing tool: audit_student_records for 22103050...
      [OK] Student: Praneeth Sai | Docs: 6
[4/5] Testing tool: verify_credential...
      [OK] Result: VALID | Title: Official Institutional Migration Certificate
[5/5] Testing resource: satyameva://stats/telemetry...
      [OK] Anchored Docs: 6 | Verified Blocks: 7
====================================================
  ALL MCP TOOLS & RESOURCES PASSED SELF-DIAGNOSTIC! 
====================================================
```

### 4.2 Connecting to Claude Desktop
Add Satyameva Aegis to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "satyameva-aegis": {
      "command": "python",
      "args": [
        "c:/Users/hp/OneDrive/Desktop/Satyameva/mcp_server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### 4.3 Autonomous Verification Agent Example (Python)
```python
import json
import subprocess

# Spawn Satyameva MCP server as a subprocess
proc = subprocess.Popen(
    ["python", "mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 1. Initialize MCP Session
init_req = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {"protocolVersion": "2024-11-05", "capabilities": {}}
}
proc.stdin.write(json.dumps(init_req) + "\n")
proc.stdin.flush()
init_res = json.loads(proc.stdout.readline())

# 2. Call verify_credential Tool
call_req = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "verify_credential",
        "arguments": {"doc_hash": "dd7d0a1788dca4c9..."}
    }
}
proc.stdin.write(json.dumps(call_req) + "\n")
proc.stdin.flush()
call_res = json.loads(proc.stdout.readline())

print("Audit Verdict:", call_res["result"]["content"][0]["text"])
```
