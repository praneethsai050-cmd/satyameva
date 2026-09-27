"""
Public verification.

Deliberately open — no login. A QR code on a printed transcript has to work
for an HR assistant who has never heard of this system, which is the entire
point of the "under 5 seconds" claim. Every hit is still logged.
"""
from flask import Blueprint, redirect, render_template, request, url_for

from security import truncate_hash, visual_hash_swatches
# Aliased: the view function below is also called `verify_hash` because its
# endpoint name is baked into url_for() calls and the QR payload.
from services.verification_service import verify_hash as run_verification

public_bp = Blueprint('public', __name__)


@public_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    """Paste-a-hash verification form."""
    if request.method == 'POST':
        doc_hash = (request.form.get('doc_hash') or '').strip()
        if doc_hash:
            return redirect(url_for('public.verify_hash', doc_hash=doc_hash))
        return render_template('public/verify.html',
                              error='Enter a credential hash to verify.')
    return render_template('public/verify.html', error=None)


@public_bp.route('/v/<doc_hash>')
def verify_hash(doc_hash):
    """
    Verification result page — the QR code's landing target.

    Supports permanent blockchain QR codes (`src=qr`) as well as legacy
    time-boxed tokens (`?t=`).
    """
    token = request.args.get('t')
    src = request.args.get('src')
    method = 'QR' if (token is not None or src == 'qr') else 'HASH'
    outcome = verify_hash_outcome(doc_hash, token, method=method)

    doc = outcome.get('doc')
    return render_template(
        'public/verify_result.html',
        outcome=outcome,
        doc=doc,
        block=outcome.get('block'),
        queried_hash=doc_hash,
        short_hash=truncate_hash(doc_hash),
        swatches=visual_hash_swatches(doc_hash),
        was_dynamic=token is not None,
    )


def verify_hash_outcome(doc_hash: str, token: str | None, method: str = 'HASH'):
    """Thin seam over the service, so the view stays free of branching."""
    if token is not None:
        return run_verification(doc_hash, method='QR', qr_token=token)
    return run_verification(doc_hash, method=method)


@public_bp.route('/offline')
def offline():
    """PWA offline fallback shell."""
    return render_template('offline.html')

