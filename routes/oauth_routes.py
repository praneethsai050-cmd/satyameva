"""
OAuth routes — Google and Microsoft sign-in alongside existing password login.

Uses Authlib's Flask OAuth client. The callback creates or retrieves the user
by OAuth provider + subject ID, then logs them in exactly like password auth.

Environment variables required (set in .env):
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
  MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT
"""
import time

from flask import (
    Blueprint, current_app, flash, redirect, render_template,
    request, session, url_for,
)
from flask_login import current_user, login_user

from extensions import db, utcnow
from models.user import ROLE_STUDENT, User
from security import hash_password

oauth_bp = Blueprint('oauth', __name__, url_prefix='/auth/oauth')

# Lazy initialisation: we only configure providers that have credentials.
_oauth = None


def _get_oauth():
    """Return (and lazily initialise) the Authlib OAuth client."""
    global _oauth
    if _oauth is None:
        try:
            from authlib.integrations.flask_client import OAuth  # type: ignore
            _oauth = OAuth(current_app._get_current_object())  # noqa: SLF001

            google_id = current_app.config.get('GOOGLE_CLIENT_ID', '')
            google_secret = current_app.config.get('GOOGLE_CLIENT_SECRET', '')
            if google_id and google_secret:
                _oauth.register(
                    name='google',
                    client_id=google_id,
                    client_secret=google_secret,
                    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                    client_kwargs={'scope': 'openid email profile'},
                )

            ms_id = current_app.config.get('MICROSOFT_CLIENT_ID', '')
            ms_secret = current_app.config.get('MICROSOFT_CLIENT_SECRET', '')
            ms_tenant = current_app.config.get('MICROSOFT_TENANT', 'common')
            if ms_id and ms_secret:
                _oauth.register(
                    name='microsoft',
                    client_id=ms_id,
                    client_secret=ms_secret,
                    server_metadata_url=f'https://login.microsoftonline.com/{ms_tenant}/v2.0/.well-known/openid-configuration',
                    client_kwargs={'scope': 'openid email profile'},
                )
        except Exception as exc:
            current_app.logger.warning('OAuth init failed: %s', exc)
            _oauth = None
    return _oauth


def _find_or_create_oauth_user(provider: str, sub: str, email: str, name: str) -> User | None:
    """Find existing user by OAuth sub or email, or create a new student account."""
    from models.institution import Institution
    juit_inst = Institution.query.filter_by(short_code='JUIT').first()

    # 1. Exact match on provider + sub (most reliable)
    user = User.query.filter_by(oauth_provider=provider, oauth_sub=sub).first()
    if user:
        if not user.institution_id and juit_inst:
            user.institution_id = juit_inst.id
            user.organization = juit_inst.name
            db.session.commit()
        return user

    # 2. Match on email (user may have registered with password first)
    user = User.query.filter_by(email=email.lower()).first()
    if user:
        # Link this OAuth provider to their existing account
        user.oauth_provider = provider
        user.oauth_sub = sub
        if not user.institution_id and juit_inst:
            user.institution_id = juit_inst.id
            user.organization = juit_inst.name
        db.session.commit()
        return user

    # 3. Create a new account (default role = student)
    username_base = email.split('@')[0].replace('.', '_').lower()
    username = username_base
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f'{username_base}{counter}'
        counter += 1

    # Generate a random unusable password for OAuth-only accounts
    salt, digest, iterations = hash_password(f'oauth-{sub}-{provider}')
    user = User(
        username=username,
        email=email.lower(),
        role=ROLE_STUDENT,
        oauth_provider=provider,
        oauth_sub=sub,
        password_salt=salt,
        password_hash=digest,
        password_iterations=iterations,
    )
    db.session.add(user)
    db.session.flush()

    from models.student import Student
    # Ensure Student row exists or link pre-provisioned credentials
    student = Student.query.filter_by(user_id=user.id).first()
    if not student:
        pre_student = Student.query.filter(Student.user.has(email=email.lower())).first()
        if pre_student:
            pre_student.user_id = user.id
            if name and (not pre_student.full_name or pre_student.full_name.startswith('Student ')):
                pre_student.full_name = name
        else:
            student = Student(
                user_id=user.id,
                full_name=name or email.split('@')[0],
                roll_number=email.split('@')[0].upper(),
                institution='Jaypee University of Information Technology',
            )
            db.session.add(student)

    db.session.commit()
    return user


def _oauth_redirect(provider_name: str):
    """Redirect the browser to the OAuth provider's authorisation URL."""
    oauth = _get_oauth()
    if oauth is None:
        flash('OAuth is not configured on this server.', 'warning')
        return redirect(url_for('auth.login'))
    client = getattr(oauth, provider_name, None)
    if client is None:
        flash(f'{provider_name.title()} sign-in is not configured.', 'warning')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for(f'oauth.{provider_name}_callback', _external=True)
    return client.authorize_redirect(redirect_uri)


def _oauth_callback(provider_name: str):
    """Handle the callback from the OAuth provider."""
    if current_user.is_authenticated:
        return redirect(url_for(current_user.home_endpoint()))
    oauth = _get_oauth()
    if oauth is None:
        flash('OAuth is not configured.', 'warning')
        return redirect(url_for('auth.login'))
    client = getattr(oauth, provider_name, None)
    if client is None:
        flash('OAuth provider not configured.', 'warning')
        return redirect(url_for('auth.login'))
    try:
        token = client.authorize_access_token()
        userinfo = token.get('userinfo') or client.userinfo()
        sub = userinfo.get('sub') or userinfo.get('oid') or ''
        email = (userinfo.get('email') or '').strip()
        name = userinfo.get('name') or email.split('@')[0]

        if not email:
            flash('Could not retrieve your email from the OAuth provider.', 'danger')
            return redirect(url_for('auth.login'))

        user = _find_or_create_oauth_user(provider_name, sub, email, name)
        if user is None or not user.is_active:
            flash('Your account is inactive. Contact the administrator.', 'danger')
            return redirect(url_for('auth.login'))

        user.last_login_at = utcnow()
        db.session.commit()
        login_user(user)
        session['last_active'] = time.time()
        flash(f'Welcome, {user.display_name}! Signed in with {provider_name.title()}.', 'success')
        return redirect(url_for(user.home_endpoint()))

    except Exception as exc:
        current_app.logger.error('OAuth callback error (%s): %s', provider_name, exc)
        flash('Sign-in failed. Please try again or use password login.', 'danger')
        return redirect(url_for('auth.login'))


# ---- Google ----
@oauth_bp.route('/google')
def google_login():
    return _oauth_redirect('google')


@oauth_bp.route('/google/callback')
def google_callback():
    return _oauth_callback('google')


# ---- Microsoft ----
@oauth_bp.route('/microsoft')
def microsoft_login():
    return _oauth_redirect('microsoft')


@oauth_bp.route('/microsoft/callback')
def microsoft_callback():
    return _oauth_callback('microsoft')
