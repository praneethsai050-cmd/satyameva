"""
Satyameva Student, Issuer & Verifier Portals — Flask application factory.

Wires config, extensions, blueprints, models, the 5-minute idle session timeout, and
the template globals the UI depends on.
"""
import os
import time

from flask import (
    Flask, flash, g, redirect, render_template, request, session, url_for,
)
from flask_login import current_user, logout_user

from config import BASE_DIR, config_by_name
from extensions import db, login_manager, mail, utcnow

#: Endpoints reachable without a live session (login page, public verifier, register, static, blockchain consensus, offline, oauth, pwa).
PUBLIC_ENDPOINTS = {
    'auth.login', 'auth.register', 'auth.verify_email', 'public.verify', 'public.verify_hash', 'public.offline', 'static', 'index',
    'blockchain_api.get_chain', 'blockchain_api.list_nodes', 'blockchain_api.consensus_resolve',
    'blockchain_api.register_nodes',
    'oauth.google_login', 'oauth.google_callback',
    'oauth.microsoft_login', 'oauth.microsoft_callback',
    'service_worker', 'manifest',
}


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get('SATYAMEVA_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # SQLite needs its parent directory to exist before the first connect.
    os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from models import (  # noqa: F401
            Block, CredentialRequest, Doc, Document, FraudReport, Institution, Notification, Student, User,
            VerificationLog,
        )
        db.create_all()

        from blockchain import ensure_genesis_block
        ensure_genesis_block()

    _register_blueprints(app)
    _register_session_timeout(app)
    _register_template_helpers(app)
    _register_error_handlers(app)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for(current_user.home_endpoint()))
        return redirect(url_for('auth.login'))

    @app.route('/sw.js')
    def service_worker():
        from flask import send_from_directory
        resp = send_from_directory(os.path.join(BASE_DIR, 'static'), 'sw.js', mimetype='application/javascript')
        resp.headers['Service-Worker-Allowed'] = '/'
        resp.headers['Cache-Control'] = 'no-cache'
        return resp

    @app.route('/manifest.json')
    def manifest():
        from flask import send_from_directory
        return send_from_directory(os.path.join(BASE_DIR, 'static'), 'manifest.json', mimetype='application/manifest+json')

    return app


def _register_blueprints(app: Flask) -> None:
    from routes.admin_routes import admin_bp
    from routes.auth_routes import auth_bp
    from routes.issuer_routes import issuer_bp
    from routes.oauth_routes import oauth_bp
    from routes.public_routes import public_bp
    from routes.student_routes import student_bp
    from routes.verifier_routes import verifier_bp
    from routes.blockchain_routes import blockchain_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(issuer_bp)
    app.register_blueprint(verifier_bp)
    app.register_blueprint(blockchain_bp)
    app.register_blueprint(admin_bp)


def _register_session_timeout(app: Flask) -> None:
    """
    Sliding 5-minute idle timeout.

    `last_active` is refreshed on every authenticated request, so the clock
    measures inactivity rather than total session length.
    """
    timeout = app.config['SESSION_TIMEOUT_SECONDS']

    @app.before_request
    def enforce_idle_timeout():
        g.session_remaining = timeout

        if request.endpoint in PUBLIC_ENDPOINTS or not current_user.is_authenticated:
            return None

        now = time.time()
        last_active = session.get('last_active')

        if last_active is not None and now - last_active > timeout:
            logout_user()
            session.clear()
            flash('Your session expired after 5 minutes of inactivity.', 'warning')
            return redirect(url_for('auth.login'))

        session['last_active'] = now
        session.modified = True
        g.session_remaining = timeout if last_active is None else \
            max(0, int(timeout - (now - last_active)))
        return None


def _register_template_helpers(app: Flask) -> None:
    from models.document import DOC_TYPES
    from security import truncate_hash, visual_hash_swatches
    from services.qr_service import qr_data_uri

    @app.context_processor
    def inject_globals():
        alert_cnt = 0
        if getattr(current_user, 'is_authenticated', False) and getattr(current_user, 'is_student', False) and getattr(current_user, 'student', None):
            from services.notification_service import unread_count
            alert_cnt = unread_count(current_user.student, current_user.student.documents)

        campus = 'jiit'
        campus_name = 'JIIT Noida'
        campus_code = 'JIIT'
        if getattr(current_user, 'is_authenticated', False):
            inst = getattr(current_user, 'institution', None)
            code = (inst.short_code if inst else '').upper()
            org = (getattr(current_user, 'organization', '') or '').upper()
            if 'JUIT' in code or 'JUIT' in org or 'WAKNAGHAT' in org:
                campus = 'juit'
                campus_name = 'JUIT Waknaghat'
                campus_code = 'JUIT'
            elif 'JUET' in code or 'JUET' in org or 'GUNA' in org:
                campus = 'juet'
                campus_name = 'JUET Guna'
                campus_code = 'JUET'
            elif 'JIIT' in code or 'JIIT' in org or 'NOIDA' in org:
                campus = 'jiit'
                campus_name = 'JIIT Noida'
                campus_code = 'JIIT'

        return {
            'brand': app.config['INSTITUTION_NAME'],
            'tagline': app.config['BRAND_TAGLINE'],
            'session_timeout': app.config['SESSION_TIMEOUT_SECONDS'],
            'session_remaining': getattr(g, 'session_remaining',
                                         app.config['SESSION_TIMEOUT_SECONDS']),
            'doc_types': DOC_TYPES,
            'current_year': utcnow().year,
            'alert_count': alert_cnt,
            'utcnow': utcnow,
            'current_campus': campus,
            'campus_name': campus_name,
            'campus_code': campus_code,
            'jaypee_campuses': [
                ('JIIT', 'Jaypee Institute of Information Technology (JIIT Noida)'),
                ('JUIT', 'Jaypee University of Information Technology (JUIT Waknaghat)'),
                ('JUET', 'Jaypee University of Engineering & Technology (JUET Guna)'),
            ],
        }

    app.add_template_filter(truncate_hash, 'short_hash')
    app.add_template_filter(visual_hash_swatches, 'swatches')
    app.add_template_filter(qr_data_uri, 'qr_uri')

    @app.template_filter('datetime')
    def _fmt_datetime(value, fmt='%d %b %Y · %H:%M'):
        return value.strftime(fmt) if value else '—'

    @app.template_filter('date')
    def _fmt_date(value, fmt='%d %b %Y'):
        return value.strftime(fmt) if value else '—'

    @app.template_filter('ago')
    def _fmt_ago(value):
        """Compact relative time for the verification timeline."""
        if not value:
            return '—'
        seconds = (utcnow() - value).total_seconds()
        if seconds < 60:
            return 'just now'
        for limit, divisor, unit in (
            (3600, 60, 'min'), (86400, 3600, 'hr'), (2592000, 86400, 'day'),
        ):
            if seconds < limit:
                count = int(seconds // divisor)
                return f'{count} {unit}{"s" if count != 1 else ""} ago'
        return value.strftime('%d %b %Y')


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(_e):
        return render_template(
            'error.html', code=403, title='Not your credential',
            message='This document belongs to another user. '
                    'You can only access credentials issued to you.',
        ), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template(
            'error.html', code=404, title='Nothing here',
            message='That page or credential does not exist.',
        ), 404

    @app.errorhandler(413)
    def too_large(_e):
        return render_template(
            'error.html', code=413, title='File too large',
            message='Documents are limited to 16 MB.',
        ), 413

    @app.errorhandler(500)
    def server_error(_e):
        db.session.rollback()
        return render_template(
            'error.html', code=500, title='Something broke',
            message='An internal error occurred. Please try again.',
        ), 500
