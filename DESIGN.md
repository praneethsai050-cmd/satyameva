# Satyameva Aegis — System & UI/UX Design Specification (DESIGN.md)

> **Document Version:** 2.4.0 • **Design System:** Cyber-Glassmorphic Aegis UI  
> **Frontend Stack:** HTML5 / CSS3 / Vanilla JavaScript / Three.js (r128) WebGL / Progressive Web App (PWA)

---

## 1. Design System & Visual Philosophy

Satyameva Aegis employs a modern **Cyber-Glassmorphic** aesthetic engineered to convey institutional authority, high-tech cryptographic permanence, and frictionless simplicity. The visual language blends military-grade defense themes with modern fintech clarity.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AEGIS DESIGN SYSTEM TOKENS                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Background Canvas:  Deep Void (#060810) to Cyber Slate (#0f172a)    │
│ • Glass Panels:       rgba(18, 24, 48, 0.72) + 16px Backdrop Blur     │
│ • Border Tracing:     rgba(99, 102, 241, 0.22) with Hover Neon Glow   │
│ • Accent Primary:     Quantum Cyan (#06b6d4) & Indigo Beacon (#6366f1)│
│ • Verification State: Emerald Green (#10b981) [Valid]                 │
│ • Warning State:      Amber Gold (#f59e0b) [Expiring / Refresh]       │
│ • Tamper / Threat:    Crimson Flame (#ef4444) [Tampered / Revoked]    │
└────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Color Tokens & Theming
| Token Name | Hex Code | Purpose & Usage |
| :--- | :--- | :--- |
| `--bg-void` | `#060810` | Primary application canvas background |
| `--bg-surface` | `#0b102b` | Card container and table surfaces |
| `--glass-panel` | `rgba(18, 24, 48, 0.75)` | Glassmorphic containers with `backdrop-filter: blur(14px)` |
| `--border-glow` | `rgba(99, 102, 241, 0.25)` | Subtle borders, transitioning to vibrant cyan on hover |
| `--accent-cyan` | `#06b6d4` | Primary brand accent, glowing buttons, blockchain nonces |
| `--accent-indigo` | `#6366f1` | Secondary gradient anchor, navigation active indicators |
| `--status-valid` | `#10b981` | Cryptographic match, verified block badge, authentic seal |
| `--status-warn` | `#f59e0b` | Expiring soon credentials, QR token refresh prompts |
| `--status-error` | `#ef4444` | Hash mismatch, tampered record, revoked certificate |
| `--text-primary` | `#f8fafc` | High-contrast headings and primary labels |
| `--text-muted` | `#94a3b8` | Metadata descriptors, helper notes, timestamps |

### 1.2 Typography Hierarchy
- **Primary Font Family:** System font stack `Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif` for native operating system rendering without network font latencies.
- **Monospace Family:** `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace` for SHA-256 hashes, ECDSA public keys, and cryptographic nonces.
- **Scale:**
  - `Display / Hero Title`: 32px – 44px (Font Weight: 800)
  - `Section Header`: 22px – 28px (Font Weight: 700)
  - `Card Header / Metric Title`: 16px – 18px (Font Weight: 600)
  - `Body Copy`: 14px – 15px (Font Weight: 400, Line Height: 1.6)
  - `Micro-Badges & Hashes`: 11px – 12.5px (Letter Spacing: +0.5px)

---

## 2. Interactive Micro-Interactions & Components

### 2.1 3D WebGL Holographic Blockchain Ledger (`hero3d.js`)
- Built using **Three.js (r128)** rendering directly on an HTML5 `<canvas id="hero-3d-canvas">`.
- Renders interconnected 3D crystalline blocks floating in a cyber coordinate matrix with particle nodes.
- Responsive to mouse movement and cursor tilt, rotating and illuminating blocks dynamically.
- Performance tuned with automated frame throttling when the tab is idle or canvas is out of viewport.

### 2.2 3D Tiltable Credential Flip Cards
- Built using pure CSS 3D transforms (`perspective: 1200px`, `transform-style: preserve-3d`).
- **Front Face:** Displays official degree title, student photo/avatar, campus crest, issuing registrar seal, and cryptographic summary.
- **Back Face:** Flips $180^\circ$ on hover or tap to reveal full 64-character SHA-256 hash, raw metadata payload, and blockchain block index.

### 2.3 60-Second Dynamic QR Code Countdown Ring
- Renders an SVG circular countdown ring around the dynamic QR code on the Student Portal.
- Depletes smoothly over 60 seconds using CSS stroke-dashoffset transitions.
- As the timer drops below 10 seconds, the ring transitions from Emerald Green (`#10b981`) to Amber Alert (`#f59e0b`), prompting the user to refresh before expiration.
- Instant AJAX endpoint (`GET /student/document/<id>/qr.json`) fetches the next rolling HMAC token seamlessly without refreshing the entire page.

### 2.4 Live 5-Minute Inactivity Session Pill
- Positioned in the persistent navigation bar: a live timer pill displaying `⏳ Session: MM:SS`.
- Automatically tracks mouse movements, keystrokes, and scroll events.
- If no user interaction occurs for 300 seconds, the session terminates immediately, redirecting to `/login` with flash notice to prevent workstation hijack.

### 2.5 Pressed Physical Seal Effect
- High-fidelity visual wax/gold seal rendered via SVG & CSS box-shadow inset highlights.
- Visually mimics an embossed university registrar stamp pressed directly into the digital paper texture of certificates and stamped PDF downloads.

---

## 3. Institutional Campus Crest System (`crest_service.py`)

To eliminate reliance on low-resolution raster images, Satyameva features an institutional procedural vector crest renderer operating at **4x supersampling** with Lanczos downscaling.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CAMPUS CREST COLOR ARCHITECTURE                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. JIIT Noida:   Deep Royal Navy (#0e265c) + Imperial Gold (#d4a017)  │
│ 2. JUIT Solan:   Alpine Pine (#0c4430) + Mountain Gold (#d4af37)       │
│ 3. JUET Guna:    Engineering Crimson (#6e121c) + Forge Amber (#eb9b1e) │
│ 4. Universal:    Cyber Slate (#0f172a) + Quantum Cyan (#06b6d4)       │
└────────────────────────────────────────────────────────────────────────┘
```

### Crest Embedding Inside QR Codes
- QR codes are rendered using `qrcode` with **Error Correction Level H (30%)**.
- The circular crest is sized to **22% of the QR matrix dimension**, occupying less than **5% of the total barcode area**.
- A dedicated 2.5px white isolation ring wraps the crest, preventing QR module occlusion and ensuring 100% scan pass rates across iPhone and Android native camera scanners.

---

## 4. Tri-Portal User Experience Architecture

```
                    ┌─────────────────────────┐
                    │    /login or OAuth      │
                    └────────────┬────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  STUDENT PORTAL  │   │  ISSUER PORTAL   │   │ VERIFIER PORTAL  │
│ (/student/...)   │   │  (/issuer/...)   │   │ (/verifier/...)  │
├──────────────────┤   ├──────────────────┤   ├──────────────────┤
│ • Holographic 3D │   │ • Bulk CSV Issue │   │ • Fast Hash Scan │
│ • 60s Dynamic QR │   │ • Gemini AI OCR  │   │ • Batch CSV Test │
│ • Download PDF   │   │ • Approval Queue │   │ • Audit Logs CSV │
│ • Live Alerts    │   │ • Block Ledger   │   │ • Fraud Reports  │
└──────────────────┘   └──────────────────┘   └──────────────────┘
```

### 4.1 Student Portal (`/student`)
1. **Dashboard (`/student/dashboard`):**
   - Displays all issued credentials in responsive grid cards.
   - Shows live verification count odometer and quick download buttons.
   - Embeds the Three.js 3D WebGL blockchain explorer in the hero banner.
2. **Credential Detail (`/student/document/<id>`):**
   - Interactive flip card with full cryptographic details.
   - Dynamic rolling QR code with live refresh timer.
   - Download Stamped PDF (with AES-256 password prompt: student DOB `DDMMYYYY`).
   - Download High-Res Certificate PNG.
3. **Audit History (`/student/history`):**
   - Timeline of all historical verification events for the student's records.
   - Exposes verifier name, method (QR / Hash), timestamp, and masked IP address.
4. **Notifications (`/student/notifications`):**
   - Unread badge counter in header.
   - Real-time alerts generated each time an employer or BGV agency audits a credential.

### 4.2 Issuer Portal (`/issuer`)
1. **Single Credential Issuance (`/issuer/issue`):**
   - File upload zone supporting PDF, PNG, JPG.
   - **Google Gemini 2.0 Flash AI Auto-Fill:** Instantly populates Student Name, Roll Number, Degree Title, and DOB.
   - One-click blockchain anchoring with automatic PoW block mining.
2. **Bulk CSV Issuance Engine (`/issuer/bulk-issue`):**
   - Drag-and-drop CSV upload input.
   - Direct download link for `template.csv` sample format.
   - Real-time transactional feedback with row-by-row error reporting.
3. **Student Account Approval (`/issuer/approvals`):**
   - Review pending student registrations matching university domain.
   - One-click activation authorizing student portal access.

### 4.3 Verifier Portal & Public Gateway (`/verify`, `/verifier`)
1. **Public Verification (`/verify`, `/v/<doc_hash>`):**
   - Universal search box accepting 64-character SHA-256 hashes or direct camera scan.
   - Zero login required for global employers, embassies, and HR agencies.
   - Instant cryptographic verdict badge (`Authentic`, `QR Expired`, `Revoked`, `Tampered`, `Expired`).
2. **Corporate Enterprise Workspace (`/verifier/dashboard`):**
   - Batch verification input: paste up to 100 hashes simultaneously or upload a CSV.
   - Audit trail history with exportable CSV and official verification certificates.
   - Built-in fraud reporting tool to flag counterfeit credentials.

### 4.4 Superadmin Portal (`/admin`)
1. **Campus Governance (`/admin/institutions`):**
   - Onboard new university campuses with official domains and physical addresses.
   - Toggle annual subscription status (locks issuance if expired).
2. **Blockchain Operations (`/admin/`):**
   - Dynamic difficulty slider ($D=1$ to $D=4$) for tuning PoW mining latency.
   - Real-time node health telemetry, block height counter, and peer connection monitor.
   - Central fraud report triage queue.

---

## 5. Mobile Responsiveness & PWA Capabilities

- **Fluid Breakpoints:**
  - Desktop: $> 1024\text{px}$ (Multi-column dashboard, 3D WebGL enabled)
  - Tablet: $768\text{px} - 1023\text{px}$ (Adaptive 2-column grid)
  - Mobile: $< 767\text{px}$ (Single-column layout, bottom sticky navigation, touch swipe support)
- **Progressive Web App (PWA):**
  - Web App Manifest (`manifest.json`) supporting standalone app launch on iOS and Android homescreens.
  - Service Worker (`sw.js`) providing offline shell caching for credential views.
  - High-resolution SVG icons and splash screen configs.
