"""Walk every page as a logged-in student plus the public verifier."""
import os, re, sys
from app import create_app
from models.document import Doc
from models.user import User

if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
app.config['MAIL_SUPPRESS_SEND'] = True
fails = []

def check(label, resp, expect=200):
    body = resp.get_data(as_text=True) if resp.mimetype.startswith('text') else ''
    ok = resp.status_code == expect
    note = ''
    if body:
        # Jinja renders missing names as empty, but these leak visibly.
        for bad in ('Undefined', 'jinja2.exceptions'):
            if bad in body:
                ok, note = False, f'contains {bad!r}'
    print(f'{"ok " if ok else "FAIL"}  {resp.status_code:3}  {len(resp.data):>7}b  {label}{"  <- " + note if note else ""}')
    if not ok:
        fails.append(label)
        if resp.status_code >= 400 and body:
            print('\n'.join(body.splitlines()[:14]))
    return body

with app.app_context():
    doc_ids = [d.id for d in Doc.query.all()]
    student_docs = Doc.query.join(Doc.student).all()
    first = student_docs[0] if student_docs else None
    first_id = first.id if first else 1
    first_hash = first.doc_hash if first else '0' * 64
    other = next((d for d in student_docs if d.student_id != first.student_id), None) if first else None
    other_id = other.id if other else None

c = app.test_client()

# ── public, unauthenticated ────────────────────────────────────────────────
check('GET  /            (redirect to login)', c.get('/'), 302)
check('GET  /login', c.get('/login'))
check('GET  /verify', c.get('/verify'))
check('POST /verify (empty -> error)', c.post('/verify', data={'doc_hash': ''}))
check('POST /verify (hash -> redirect)', c.post('/verify', data={'doc_hash': first_hash}), 302)
check('GET  /v/<hash>   VALID or EXPIRED', c.get(f'/v/{first_hash}'))
check('GET  /v/<bogus>  NOT_FOUND', c.get('/v/' + 'f' * 64))
check('GET  /v/<hash>?t=bad  QR_EXPIRED', c.get(f'/v/{first_hash}?t=1.deadbeef'))
check('GET  /student/dashboard (anon -> login)', c.get('/student/dashboard'), 302)
check('GET  /nope (404 page)', c.get('/nope'), 404)

# ── log in ────────────────────────────────────────────────────────────────
admin_pass = os.environ.get('ADMIN_PASSWORD', 'Satyameva@2026')
admin_user = os.environ.get('ADMIN_USERNAME', 'admin')

# Test admin login
r = c.post('/login', data={'identifier': admin_user, 'password': admin_pass})
check('POST /login (admin)', r, 302)
print('      -> ' + (r.headers.get('Location') or ''))

check('GET  /admin/ (dashboard)', c.get('/admin/'))
check('GET  /admin/users', c.get('/admin/users'))
check('GET  /admin/institutions', c.get('/admin/institutions'))
check('GET  /admin/documents', c.get('/admin/documents'))
check('GET  /admin/stats.json', c.get('/admin/stats.json'))
check('GET  /logout', c.get('/logout'), 302)

with app.app_context():
    student_user = User.query.filter_by(role='student').first()
if student_user:
    with c.session_transaction() as sess:
        sess['_user_id'] = str(student_user.id)
        sess['_fresh'] = True
    body = check('GET  /student/dashboard', c.get('/student/dashboard'))
    check('GET  /student/notifications', c.get('/student/notifications'))
    check('GET  /student/history', c.get('/student/history'))
    check('GET  /student/chain/validate', c.get('/student/chain/validate'))
else:
    body = ""

# Every document this student owns.
mine = [int(m) for m in set(re.findall(r'/student/document/(\d+)\b', body))]
print(f'\n      student owns doc ids: {sorted(mine)}')
for did in sorted(mine):
    check(f'GET  /student/document/{did}', c.get(f'/student/document/{did}'))
    check(f'GET  /student/document/{did}/history', c.get(f'/student/document/{did}/history'))
    check(f'GET  /student/document/{did}/qr.png', c.get(f'/student/document/{did}/qr.png'))
    check(f'GET  /student/document/{did}/qr.json', c.get(f'/student/document/{did}/qr.json'))
    check(f'GET  /student/document/{did}/download', c.get(f'/student/document/{did}/download'))
    check(f'GET  /student/document/{did}/preview', c.get(f'/student/document/{did}/preview'))
    check(f'GET  /student/document/{did}/download/image',
          c.get(f'/student/document/{did}/download/image'))

# ── RBAC: someone else's document must 403 ────────────────────────────────
foreign = [d for d in doc_ids if d not in mine]
if foreign and student_user:
    check(f'GET  /student/document/{foreign[0]} (not mine -> 403)',
          c.get(f'/student/document/{foreign[0]}'), 403)

check('GET  /logout', c.get('/logout'), 302)

print('\n' + ('ALL PASS' if not fails else f'{len(fails)} FAILURES: {fails}'))
sys.exit(1 if fails else 0)
