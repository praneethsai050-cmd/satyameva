"""
End-to-End integration test suite for Satyameva:
Tests Student, Issuer, and Verifier portals, blockchain persistence, and verification notifications.
"""
import io
import json
import os
import sys

from app import create_app
from blockchain import Blockchain, blockchain_instance, validate_chain
from extensions import db
from models import Doc, Document, FraudReport, Notification, Student, User, VerificationLog


def run_tests():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    client = app.test_client()

    with app.app_context():
        print("=== Test 1: Blockchain Persistence & Genesis Block ===")
        ok, msg = validate_chain()
        assert ok, f"Blockchain validation failed: {msg}"
        assert os.path.exists("instance/blockchain.json"), "instance/blockchain.json not found"
        print(" -> Blockchain is valid and synced to JSON file.")

        print("\n=== Test 2: User Registration (Unified Form for 3 Roles) ===")
        # Register new student
        resp = client.post('/register', data={
            'role': 'student',
            'username': 'test.student',
            'email': 'test.student@test.ac.in',
            'password': 'password123',
            'full_name': 'Test Student',
            'roll_number': 'TEST2026',
            'program': 'B.Tech IT',
        }, follow_redirects=True)
        assert resp.status_code == 200
        student_user = User.query.filter_by(username='test.student').first()
        assert student_user is not None
        assert student_user.student is not None
        assert student_user.student.roll_number == 'TEST2026'
        print(" -> Student registration successful.")

        # Register new issuer
        client.get('/logout')
        resp = client.post('/register', data={
            'role': 'issuer',
            'username': 'test.issuer',
            'email': 'test.issuer@test.ac.in',
            'password': 'password123',
            'organization': 'Apex University',
        }, follow_redirects=True)
        assert resp.status_code == 200
        issuer_user = User.query.filter_by(username='test.issuer').first()
        assert issuer_user is not None
        assert issuer_user.role == 'issuer'
        print(" -> Issuer registration successful.")

        # Register new verifier
        client.get('/logout')
        resp = client.post('/register', data={
            'role': 'verifier',
            'username': 'test.verifier',
            'email': 'test.verifier@testcorp.com',
            'password': 'password123',
            'organization': 'Global Tech Corp',
        }, follow_redirects=True)
        assert resp.status_code == 200
        verifier_user = User.query.filter_by(username='test.verifier').first()
        assert verifier_user is not None
        assert verifier_user.role == 'verifier'
        print(" -> Verifier registration successful.")

        print("\n=== Test 3: Issuer Portal - Issue Document & Blockchain Mining ===")
        client.get('/logout')
        client.post('/login', data={'identifier': 'test.issuer', 'password': 'password123'})

        fake_file = (io.BytesIO(b'dummy certificate content image/png'), 'degree_cert.png')
        resp = client.post('/issuer/issue', data={
            'roll_number': 'TEST2026',
            'student_name': 'Test Student',
            'doc_type': 'DEGREE',
            'title': 'Bachelor of Technology in Information Technology',
            'validity_days': '3650',
            'document': fake_file,
        }, follow_redirects=True)
        assert resp.status_code == 200

        doc = Doc.query.filter_by(student_id=student_user.student.id).first()
        assert doc is not None
        assert doc.block_index is not None
        assert doc.doc_hash is not None
        print(f" -> Document issued and anchored to Block #{doc.block_index} (Hash: {doc.doc_hash[:16]}...)")

        print("\n=== Test 4: Student Portal - Dashboard, QR Codes, and Details ===")
        client.get('/logout')
        client.post('/login', data={'identifier': 'test.student', 'password': 'password123'})

        resp = client.get('/student/dashboard')
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'Test Student' in html
        assert doc.title in html
        assert 'Download' in html
        assert 'data:image/png;base64' in html  # QR code data URI rendered on card
        print(" -> Student dashboard rendered issued document with QR code and download options.")

        resp = client.get(f'/student/document/{doc.id}')
        assert resp.status_code == 200
        detail_html = resp.get_data(as_text=True)
        assert 'Blockchain record' in detail_html or 'Ledger anchor' in detail_html
        assert f'#{doc.block_index}' in detail_html
        print(" -> Student document detail displays blockchain proof and digital stamp.")

        print("\n=== Test 5: Verifier Portal - Scanning, Verification & Notifications ===")
        client.get('/logout')
        client.post('/login', data={'identifier': 'test.verifier', 'password': 'password123'})

        # Verifier checks dashboard
        resp = client.get('/verifier/dashboard')
        assert resp.status_code == 200

        # Verifier checks document hash
        resp = client.get(f'/verifier/v/{doc.doc_hash}')
        assert resp.status_code == 200
        result_html = resp.get_data(as_text=True)
        assert 'Authentic credential' in result_html
        assert 'Global Tech Corp' in result_html or 'test.verifier' in result_html
        print(" -> Verifier successfully validated credential against blockchain.")

        # Check VerificationLog
        vlog = VerificationLog.query.filter_by(doc_id=doc.id, verifier_id=verifier_user.id).first()
        assert vlog is not None
        assert vlog.result == 'VALID'
        print(" -> Verification logged in VerificationLog.")

        # Check that Student received Notification
        notif = Notification.query.filter_by(student_id=student_user.student.id, doc_id=doc.id).first()
        assert notif is not None
        assert 'Verified' in notif.title
        print(f" -> Student Notification created: '{notif.title}' - '{notif.message}'")

        # Verifier views history
        resp = client.get('/verifier/history')
        assert resp.status_code == 200
        history_html = resp.get_data(as_text=True)
        assert doc.title in history_html
        print(" -> Verifier history lists verified documents.")

        # Verifier reports fraud on invalid hash
        resp = client.post('/verifier/report-fraud', data={
            'doc_hash': 'e' * 64,
            'notes': 'Suspicious forged marksheet detected in application'
        }, follow_redirects=True)
        assert resp.status_code == 200
        fraud = FraudReport.query.filter_by(doc_hash='e' * 64).first()
        assert fraud is not None
        assert fraud.verifier_id == verifier_user.id
        print(" -> Fraud report submitted and logged to registry.")

        print("\n=== Test 6: Student Views Notification & Badge Count ===")
        client.get('/logout')
        client.post('/login', data={'identifier': 'test.student', 'password': 'password123'})

        resp = client.get('/student/notifications')
        assert resp.status_code == 200
        notif_html = resp.get_data(as_text=True)
        assert 'Global Tech Corp' in notif_html or 'Verified' in notif_html
        print(" -> Student notifications page displays real-time verification alert.")

        print("\n=== Test 7: Batch Verification (Pasted Hashes & CSV) ===")
        client.get('/logout')
        client.post('/login', data={'identifier': 'test.verifier', 'password': 'password123'})

        # Test batch verify with text hashes
        resp = client.post('/verifier/batch', data={
            'raw_hashes': f"{doc.doc_hash}\n{'0'*64}\n{'f'*64}"
        })
        assert resp.status_code == 200
        batch_html = resp.get_data(as_text=True)
        assert 'Batch Verification Results' in batch_html
        assert 'Authentic' in batch_html
        assert 'Not Found' in batch_html
        print(" -> Batch verification successfully validated multiple credential hashes simultaneously.")

        print("\n=== Test 8: Export Verification CSV & Official Audit Report ===")
        resp = client.get('/verifier/history/export.csv')
        assert resp.status_code == 200
        assert resp.mimetype == 'text/csv'
        assert 'Verification ID' in resp.get_data(as_text=True)
        print(" -> Verification history successfully exported to CSV.")

        resp = client.get('/verifier/history/audit-report')
        assert resp.status_code == 200
        report_html = resp.get_data(as_text=True)
        assert 'Verification Audit Statement' in report_html
        assert 'Audit Proof Hash' in report_html
        print(" -> Cryptographic verification audit report successfully rendered.")

        print("\n=== Test 9: P2P Multi-Node Consensus API ===")
        # Query chain
        resp = client.get('/blockchain/chain')
        assert resp.status_code == 200
        chain_json = resp.get_json()
        assert chain_json['status'] == 'ok'
        assert chain_json['length'] >= 1
        print(f" -> P2P Ledger exposed with {chain_json['length']} verified blocks.")

        # Register peer nodes
        resp = client.post('/blockchain/nodes/register', json={
            'nodes': ['http://127.0.0.1:5001', 'http://node2.satyameva.org:5000']
        })
        assert resp.status_code == 201
        reg_json = resp.get_json()
        assert len(reg_json['registered']) >= 1
        print(" -> Peer blockchain nodes successfully registered.")

        # Run consensus resolve
        resp = client.get('/blockchain/resolve')
        assert resp.status_code == 200
        resolve_json = resp.get_json()
        assert 'message' in resolve_json
        print(f" -> Consensus conflict resolution verified: {resolve_json['message']}")

        print("\n=== Test 10: PWA Manifest & Offline Shell ===")
        resp = client.get('/static/manifest.json')
        assert resp.status_code == 200
        manifest = resp.get_json()
        assert manifest['short_name'] == 'Satyameva'
        assert manifest['display'] == 'standalone'
        print(" -> PWA Web App Manifest verified.")

        resp = client.get('/static/sw.js')
        assert resp.status_code == 200
        assert 'satyameva-cache' in resp.get_data(as_text=True)
        print(" -> PWA Service Worker (sw.js) verified.")

        resp = client.get('/offline')
        assert resp.status_code == 200
        assert 'You Are Currently Offline' in resp.get_data(as_text=True)
        print(" -> Offline fallback shell verified.")

        print("\n=== Test 11: Asymmetric ECDSA secp256k1 Signatures ===")
        from services.crypto_service import generate_keypair, sign_hash, verify_hash_signature
        priv, pub = generate_keypair()
        test_digest = 'a' * 64
        sig = sign_hash(priv, test_digest)
        assert verify_hash_signature(pub, test_digest, sig), "Valid signature rejected"
        assert not verify_hash_signature(pub, 'b' * 64, sig), "Forged hash signature accepted"
        print(" -> Asymmetric secp256k1 digital signatures verified.")

        print("\n=======================================================")
        print(">>> ALL 11 BOOST END-TO-END SUITES PASSED WITH 100%! <<<")
        print("=======================================================")


if __name__ == '__main__':
    run_tests()
