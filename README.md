# Satyameva — Student Portal

**Blockchain-backed academic credential verification.** A student signs in, sees
every credential their institution has issued them, and hands an employer a
60-second QR code instead of a scanned PDF. The employer gets a verdict in under
five seconds without phoning a registrar.

This repository is the **Student Portal** — one of three portals in the wider
Satyameva system (Student · Issuer · Verifier), all sharing one blockchain
backend. The issuer and verifier portals are not built here; issuer and verifier
*accounts* exist so you can prove that role-based access control locks them out
of the student portal.

---

## Run it

```bash
pip install -r requirements.txt
```

```bash
python seed.py --reset
```

```bash
python run.py
```

Then open <http://127.0.0.1:5000>. `seed.py` creates the SQLite database, mines
the blockchain, generates the certificate images and prints the demo logins.
`--reset` drops and recreates the tables — omit it to keep existing data.

### Demo logins

All four use the password `satyameva123` (demo data, printed on the login page).

| Username         | Role     | What it shows                                    |
| ---------------- | -------- | ------------------------------------------------ |
| `aarav.sharma`   | student  | 6 credentials spanning every status the UI draws |
| `priya.nair`     | student  | 1 revoked credential                             |
| `jiit.registrar` | issuer   | RBAC — blocked from the student portal           |
| `infosys.hr`     | verifier | RBAC — blocked from the student portal           |

Sessions end after **5 minutes of idle time**; the pill in the header counts
down. That is deliberate, not a bug — it is the security requirement.

---

## The five-minute demo

1. **Sign in** as `aarav.sharma`. The dashboard hero draws the live chain in
   WebGL; the stat counters roll up; the credential cards tilt in 3D on hover.
2. **Open the Degree.** The verification seal is pressed onto the certificate.
   Hit **Show ledger data** to flip the card and read the block behind it.
3. **Watch the QR code.** It carries a signed token that dies after 60 seconds,
   then refreshes itself. A screenshot someone forwards later will not verify —
   that is what stops replay.
4. **Copy the hash**, open `/verify` in a private window, paste it. Authentic,
   with the block that proves it. Every check is logged.
5. **Go back to History.** The check you just ran is at the top of the timeline,
   with its network address and the method used.
6. **Try the failure modes.** The Transfer Certificate is expired, the Bonafide
   is expiring soon, and `priya.nair`'s degree is revoked. Verify a hash that
   does not exist and the answer is unambiguous: not authentic.

---

## How it works

### Hashing and the ledger

Every credential is hashed from three things: a **per-document random salt**, the
file's own digest, and the credential metadata. Change any one and the hash stops
matching. The hash is then anchored into a proof-of-work blockchain
(`blockchain.py`, difficulty 4) persisted in the `Block` table, each block
carrying the previous block's hash.

Verification does not trust the stored hash. It **re-derives** the digest from the
stored payload and compares — so editing a row directly in the database produces
a `TAMPERED` verdict rather than a silent pass. The chain is then walked end to
end.

The six verdicts, cheapest check first: `NOT_FOUND` → `QR_EXPIRED` → `REVOKED` →
`TAMPERED` → `EXPIRED` → `VALID`.

### Dynamic QR codes

A QR payload is `hash` + `expiry.signature`, HMAC-signed with the app secret and
valid for 60 seconds. The verifier distinguishes *expired* from *wrong signature*
from *malformed*, so a stale-but-genuine code gets "ask for a fresh one" rather
than "forgery".

### Security

- **PBKDF2-HMAC-SHA256, 100,000 iterations**, per-user salt. Logins transparently
  re-hash if the iteration count has since been raised.
- **5-minute sliding idle timeout** — the window resets on each request.
- **RBAC** via a `role_required` decorator, plus an ownership check on every
  document route: a student who requests someone else's credential gets a 403,
  not a redirect.
- Public verification reveals the holder's name only for a genuine credential.
  An expired QR code withholds it.

### The 3D layer

CSS 3D throughout, with Three.js (r128, CDN) for the hero chain. Everything
degrades: no WebGL leaves the CSS chain in place, and no JavaScript at all still
gives working filters, a server-rendered QR code and real download links. The
tilt cards, the stamp press-in, the card flip and the QR parallax are all
transform-based and honour `prefers-reduced-motion`.

---

## Layout

```
app.py                 application factory, error handlers, idle timeout, filters
run.py                 dev entry point
config.py              one place for every tunable (timeouts, TTLs, difficulty)
seed.py                demo data — users, certificates, blocks, history
blockchain.py          proof of work, chaining, validate_chain()
security.py            PBKDF2, per-document salting, hash recomputation
decorators.py          role_required / student_required
extensions.py          db, login_manager, utcnow()

models/                user · student · document · block · verification_log
routes/                auth · public (/verify, /v/<hash>) · student
services/              credential · verification · qr · stamp · notification
templates/             base + login + error, public/, student/
static/css/            theme.css (tokens) · style.css (components + 3D)
static/js/             app.js (interaction) · hero3d.js (WebGL chain)
```

### Routes

| Route                               | What it does                            |
| ----------------------------------- | --------------------------------------- |
| `/login` `/logout`                  | Role-based redirect after sign-in       |
| `/student/dashboard`                | Stats, search, filter by type/status    |
| `/student/document/<id>`            | Preview + seal, flip to ledger, QR      |
| `/student/document/<id>/download`   | Stamped PDF (`/download/image` for PNG) |
| `/student/document/<id>/qr.png`     | QR image; `qr.json` refreshes it live   |
| `/student/document/<id>/history`    | Who verified this credential, when      |
| `/student/history`                  | Every check across all credentials      |
| `/student/notifications`            | Expiry warnings, revocations, checks    |
| `/student/chain/validate`           | JSON — re-run the chain check on demand |
| `/verify`                           | Public form — paste a hash              |
| `/v/<hash>`                         | Permanent verification link             |

---

## Verifying the build

Two harnesses, no framework required:

```bash
python _smoke.py
```

Walks every route as an authenticated student and asserts the status and body
size — including the 403 for another student's document.

```bash
PYTHONIOENCODING=utf-8 python _assert.py
```

Checks behaviour rather than plumbing: all six verdicts, the QR token accepted
fresh and rejected stale, holder details withheld on failure, the log growing by
exactly the number of checks run, RBAC blocking the issuer, and the idle timeout
kicking in. `PYTHONIOENCODING` is only needed because the output uses box-drawing
characters on a Windows console.

---

## Stack

Flask 3 · Flask-SQLAlchemy · Flask-Login · SQLite · `qrcode` · Pillow ·
Three.js r128 (CDN) · vanilla JS. The blockchain and the crypto are hand-written
in `blockchain.py` and `security.py` — no external chain, no reportlab.
