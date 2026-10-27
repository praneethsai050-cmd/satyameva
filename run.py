"""
Development entry point.

    python run.py            # http://127.0.0.1:5000
    PORT=8000 python run.py
"""
import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'

    # Startup banner
    gemini_ok = bool(app.config.get('GEMINI_API_KEY'))
    google_ok = bool(app.config.get('GOOGLE_CLIENT_ID') and app.config.get('GOOGLE_CLIENT_SECRET'))
    mail_ok = bool(app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'))

    admin_user = os.environ.get('ADMIN_USERNAME', 'superadmin')
    admin_email = os.environ.get('ADMIN_EMAIL', 'superadmin@satyameva.in')

    print()
    print('  +--------------------------------------------------+')
    print('  |  Satyameva - Blockchain Credential Verification  |')
    print('  |  Production Node - Jaypee Multi-Campus Network   |')
    print('  +--------------------------------------------------+')
    print(f'  > System Endpoint:       http://{host}:{port}')
    print(f'  > Gmail SMTP Service:    {"[OK] Online" if mail_ok else "[--] Offline"}')
    print(f'  > Gemini AI Extraction:  {"[OK] Online" if gemini_ok else "[--] Offline"}')
    print(f'  > Google OAuth Login:    {"[OK] Online" if google_ok else "[--] Offline"}')
    print()
    print('  Active Campuses: JIIT (Noida) | JUIT (Waknaghat) | JUET (Guna)')
    print(f'  Master Administrator: {admin_user} ({admin_email})')
    print('  Environment: Production Mode (Live Cryptographic Ledger)')
    print()

    app.run(host=host, port=port, debug=debug)
