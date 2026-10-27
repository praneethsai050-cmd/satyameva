"""
Configuration for the Satyameva Student Portal.

Pick an environment with the SATYAMEVA_ENV variable ('development',
'production'); anything else falls back to 'default' (= development).
"""
import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load .env file if present (local dev convenience)
load_dotenv(os.path.join(BASE_DIR, '.env'), override=False)


class BaseConfig:
    # ---- Core Flask ----
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'satyameva-dev-key-change-in-production'

    # ---- Database ----
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'satyameva.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- Uploads ----
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024          # 16 MB per document
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'webp'}

    # ---- Security ----
    PASSWORD_ITERATIONS = 100_000                  # PBKDF2-HMAC-SHA256 rounds
    SESSION_TIMEOUT_SECONDS = 5 * 60               # 5-minute idle timeout
    TRUST_PROXY_HEADERS = os.environ.get('TRUST_PROXY_HEADERS', '').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ---- Dynamic QR ----
    QR_TOKEN_TTL_SECONDS = 60                      # QR payload expires in 1 minute

    # ---- Blockchain ----
    POW_DIFFICULTY = 4                             # leading '0's required in proof hash

    # ---- Notifications ----
    EXPIRY_WARNING_DAYS = 30                       # "expiring soon" window

    # ---- Email (Flask-Mail) ----
    MAIL_SERVER   = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS',  'true').lower() == 'true'
    MAIL_USE_SSL  = os.environ.get('MAIL_USE_SSL',  'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')     # None → Flask-Mail skips auth
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = (
        os.environ.get('MAIL_SENDER_NAME', 'Satyameva • Jaypee Credentials'),
        os.environ.get('MAIL_DEFAULT_SENDER', 'satyameva-noreply@jaypeecredentials.in')
    )
    MAIL_SUPPRESS_SEND  = False                         # set True in tests

    # ---- Branding ----
    INSTITUTION_NAME = 'Satyameva'
    BRAND_TAGLINE = 'Blockchain-Backed Truth'

    # ---- Gemini AI ----
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

    # ---- OAuth (Google) ----
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

    # ---- OAuth (Microsoft) ----
    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID', '')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET', '')
    MICROSOFT_TENANT = os.environ.get('MICROSOFT_TENANT', 'common')


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    POW_DIFFICULTY = 1


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
