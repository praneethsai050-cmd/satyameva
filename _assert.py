"""Behavioural checks: QR token lifecycle, session timeout, RBAC, verdicts."""
import re, sys, time
from app import create_app
from extensions import db
from models.document import Doc
from models.verification_log import VerificationLog
from security import make_qr_token

app = create_app()
fails = []

def want(label, cond, extra=''):
    print(f'{"ok  " if cond else "FAIL"}  {label}{"  <- " + extra if extra and not cond else ""}')
    if not cond: fails.append(label)

with app.app_context():
    valid = next(d for d in Doc.query.all() if d.status in ('VALID', 'EXPIRING') and not d.revoked)
    expired = next((d for d in Doc.query.all() if d.status == 'EXPIRED'), None)
    revoked = next((d for d in Doc.query.all() if d.revoked), None)
    vh, eh, rh = valid.doc_hash, (expired.doc_hash if expired else None), (revoked.doc_hash if revoked else None)
    secret = app.config['SECRET_KEY']
    fresh, _exp = make_qr_token(vh, secret, ttl=60)
    stale, _ = make_qr_token(vh, secret, ttl=-5)          # already dead
    wrong, _ = make_qr_token('0' * 64, secret, ttl=60)    # signed for another doc
    before = VerificationLog.query.count()

c = app.test_client()

print('\n── public verdicts ─────────────────────────────────────────────')
b = c.get(f'/v/{vh}').get_data(as_text=True)
want('permanent link  -> Authentic', 'Authentic credential' in b)
want('permanent link  -> "Permanent link" badge', 'Permanent link' in b)
want('permanent link  -> holder revealed', 'Holder' in b)
want('permanent link  -> block shown', 'Blockchain proof' in b and 'Proof of work' in b)

b = c.get(f'/v/{vh}?t={fresh}').get_data(as_text=True)
want('fresh QR token  -> Authentic', 'Authentic credential' in b)
want('fresh QR token  -> "Live QR scan" badge', 'Live QR scan' in b)

b = c.get(f'/v/{vh}?t={stale}').get_data(as_text=True)
want('expired QR token -> QR expired verdict', 'This QR code has expired' in b)
want('expired QR token -> holder withheld', 'Holder' not in b, 'identity leaked')

b = c.get(f'/v/{vh}?t={wrong}').get_data(as_text=True)
want('mismatched token -> rejected', 'QR' in b and 'Authentic credential' not in b)

b = c.get('/v/' + 'f' * 64).get_data(as_text=True)
want('unknown hash    -> Not on the ledger', 'Not on the ledger' in b)
want('unknown hash    -> no credential panel', 'Holder' not in b)

if eh:
    b = c.get(f'/v/{eh}').get_data(as_text=True)
    want('expired doc     -> "Genuine, but expired"', 'Genuine, but expired' in b)
if rh:
    b = c.get(f'/v/{rh}').get_data(as_text=True)
    want('revoked doc     -> "Revoked by the issuer"', 'Revoked by the issuer' in b)
    # A revoked credential is a genuine record the issuer withdrew, so the page
    # must not also imply the ledger failed its integrity check.
    want('revoked doc     -> chain still reported intact',
         'chain intact' in b and 'chain not walked' not in b)

print('\n── every attempt is logged ─────────────────────────────────────')
with app.app_context():
    after = VerificationLog.query.count()
want(f'log grew by the number of checks ({after - before} new rows)', after > before)

print('\n── login / RBAC ────────────────────────────────────────────────')
want('bad password rejected',
     b'Signed in' not in c.post('/login', data={'identifier': 'aarav.sharma',
                                                'password': 'wrong'}).data)
r = c.post('/login', data={'identifier': 'aarav.sharma', 'password': 'satyameva123'})
want('good password -> /student/dashboard', r.headers.get('Location') == '/student/dashboard')

d = c.get('/student/dashboard').get_data(as_text=True)
want('dashboard greets the student', 'Aarav' in d)
want('dashboard shows only own docs', '/student/document/7' not in d)
want('dashboard has the 3D hero canvas', 'data-hero3d' in d)
want('dashboard cards are tiltable', d.count('data-tilt') >= 5)
want('odometer counters seeded', 'data-count' in d)

n = c.get('/student/notifications').get_data(as_text=True)
want('notifications render alerts', 'alert alert-' in n)

h = c.get('/student/history').get_data(as_text=True)
want('history renders the timeline', 'tl-item' in h and 'tl-dot' in h)
want('history shows IP addresses', 'IPv4' in h or '🌐' in h)

det = c.get(f'/student/document/{valid.id}').get_data(as_text=True)
want('detail has the flip card', 'doc-flip' in det and 'flip-back' in det)
want('detail has the pressed stamp', 'class="stamp' in det)
want('detail has the floating QR', 'qr-float' in det and 'data-qr-image' in det)
want('detail exposes the QR refresh endpoint', 'qr.json' in det)
want('detail shows the full 64-char hash', valid.doc_hash in det)

print('\n── issuer/verifier cannot reach the student portal ──────────────')
c2 = app.test_client()
c2.post('/login', data={'identifier': 'jiit.registrar', 'password': 'satyameva123'})
want('issuer blocked from student dashboard',
     c2.get('/student/dashboard').status_code in (302, 403))

print('\n── 5-minute idle timeout ───────────────────────────────────────')
c3 = app.test_client()
c3.post('/login', data={'identifier': 'aarav.sharma', 'password': 'satyameva123'})
want('session alive immediately', c3.get('/student/dashboard').status_code == 200)
with c3.session_transaction() as s:
    s['last_active'] = time.time() - (app.config['SESSION_TIMEOUT_SECONDS'] + 1)
r = c3.get('/student/dashboard')
want('idle past the timeout -> kicked to login',
     r.status_code == 302 and '/login' in (r.headers.get('Location') or ''),
     f'{r.status_code} {r.headers.get("Location")}')

print('\n' + ('ALL PASS' if not fails else f'{len(fails)} FAILURES: {fails}'))
sys.exit(1 if fails else 0)
