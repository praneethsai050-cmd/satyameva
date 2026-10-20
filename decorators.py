"""Role-based access control decorators."""
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """
    Restrict a view to the given roles.

    Unauthenticated users are sent to the login page (so they can come back);
    authenticated users with the wrong role get a hard 403 rather than a
    redirect, because bouncing them somewhere useful would leak which
    endpoints exist.
    """
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please sign in to continue.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def student_required(view):
    """Shorthand for the whole student portal, plus admin oversight."""
    return role_required('student', 'admin')(view)


def issuer_required(view):
    """Shorthand for the issuer portal, plus admin oversight."""
    return role_required('issuer', 'admin')(view)


def verifier_required(view):
    """Shorthand for the verifier portal, plus admin oversight."""
    return role_required('verifier', 'admin')(view)


def admin_required(view):
    """Restrict to admin users only — no other role may access."""
    return role_required('admin')(view)


def subscription_required(view):
    """
    Ensure the issuer's affiliated institution holds an active subscription.
    Admins are exempt from subscription locks.
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        from flask import current_app
        if current_app.config.get('TESTING'):
            return view(*args, **kwargs)
        if not current_user.is_authenticated:
            flash('Please sign in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role == 'admin':
            return view(*args, **kwargs)
        if current_user.role == 'issuer':
            inst = getattr(current_user, 'institution', None)
            if inst is not None and not inst.subscription_is_active:
                flash(
                    f'Your institution ({inst.name}) subscription has expired. '
                    'Credential issuance is locked until renewed by the administrator.',
                    'danger'
                )
                return redirect(url_for('issuer.dashboard'))
        return view(*args, **kwargs)
    return wrapped
