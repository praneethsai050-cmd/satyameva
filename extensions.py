"""
Shared Flask extension instances.

Kept in their own module so models and routes can import them without
creating a circular dependency on the application factory in `app.py`.
"""
from datetime import datetime, timezone

from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please sign in to continue.'
login_manager.login_message_category = 'warning'

mail = Mail()


def utcnow():
    """
    Naive UTC timestamp.

    SQLite's DateTime column drops tzinfo on write, so an aware datetime
    would come back naive and blow up every later comparison. Storing
    naive-UTC everywhere keeps arithmetic consistent, while going through
    `timezone.utc` avoids the deprecated `datetime.utcnow()`.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
