"""
Adversarial Verification Suite for Satyameva Bulk Issuance
Specialized testing for:
1. Blockchain chain continuity & PoW verification across bulk-issued credentials
2. Cryptographic hashing invariance between issuance and public verification
3. Dual-persistence parity (SQLite vs instance/blockchain.json) & state recovery
4. Tamper resistance: Mutation attacks on block data, links, proof, and doc payloads
5. Stress & Scale: Anti-collision salting, HTTP Bulk Upload All-or-Nothing atomicity, PoW difficulty scaling
"""
import copy
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime

# Set isolated test environment variables before importing app
temp_dir = tempfile.mkdtemp(prefix='satyameva_adv_test_')
test_db_file = os.path.join(temp_dir, 'adv_test.db')
test_json_file = os.path.join(temp_dir, 'blockchain.json')

os.environ['DATABASE_URL'] = f'sqlite:///{test_db_file}'
os.environ['SATYAMEVA_ENV'] = 'development'

from app import create_app
from blockchain import (
    GENESIS_PREVIOUS_HASH,
    Blockchain,
    blockchain_instance,
    compute_block_hash,
    mine_block,
    validate_chain,
)
from extensions import db, mail, utcnow

# Suppress actual SMTP network calls during adversarial testing
mail.send = lambda msg: True

from models.block import Block
from models.document import DOC_TYPES, Doc
from models.notification import Notification
from models.student import Student
from models.user import ROLE_ISSUER, ROLE_STUDENT, User
from models.verification_log import (
    RESULT_EXPIRED,
    RESULT_NOT_FOUND,
    RESULT_QR_EXPIRED,
    RESULT_REVOKED,
    RESULT_TAMPERED,
    RESULT_VALID,
    VerificationLog,
)
from security import (
    canonical_payload,
    check_qr_token,
    create_document_hash,
    generate_salt,
    hash_password,
    hashes_match,
    make_qr_token,
    recompute_document_hash,
)
from services.credential_service import issue_credential
from services.verification_service import verify_hash


class AdversarialTestRunner:
    def __init__(self):
        self.orig_storage = blockchain_instance.storage_file
        self.orig_diff = blockchain_instance.difficulty
        blockchain_instance.storage_file = test_json_file
        blockchain_instance.difficulty = 2

        self.app = create_app(test_config={
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'MAIL_SUPPRESS_SEND': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{test_db_file}',
            'POW_DIFFICULTY': 2,
            'SERVER_NAME': 'localhost',
        })
        
        self.passed_tests = []
        self.failed_tests = []
        self.findings = []

    def log_pass(self, name, detail=""):
        print(f"[PASS] {name} {detail}")
        self.passed_tests.append((name, detail))

    def log_fail(self, name, error):
        print(f"[FAIL] {name}: {error}")
        self.failed_tests.append((name, str(error)))

    def record_finding(self, severity, title, detail):
        self.findings.append({'severity': severity, 'title': title, 'detail': detail})

    def run_all(self):
        with self.app.app_context():
            print("=" * 75)
            print("  SATYAMEVA ADVERSARIAL CHALLENGE SUITE: BLOCKCHAIN & LEDGER INTEGRITY")
            print("=" * 75)
            
            # Setup fresh tables & genesis
            db.drop_all()
            db.create_all()
            if os.path.exists(test_json_file):
                os.remove(test_json_file)
                
            blockchain_instance.ensure_genesis_block()
            
            # Setup test issuer & student
            salt, digest, iters = hash_password('pass123')
            issuer_user = User(
                username='apex.test.issuer',
                email='test_issuer@apex.edu',
                role=ROLE_ISSUER,
                organization='Apex University of Technology',
                password_salt=salt,
                password_hash=digest,
                password_iterations=iters,
            )
            db.session.add(issuer_user)
            db.session.commit()
            self.issuer = issuer_user

            # 1. Test Blockchain Continuity & PoW
            self.test_1_blockchain_continuity_and_pow()

            # 2. Test Cryptographic Hashing Invariance & Determinism
            self.test_2_cryptographic_hashing_invariance()

            # 3. Test Dual-Persistence Parity & Resilience
            self.test_3_dual_persistence_sync_and_recovery()

            # 4. Test Tamper Resistance (Block & Doc Mutations)
            self.test_4_tamper_resistance_attacks()

            # 5. Stress & Edge Scenarios (HTTP Bulk Upload Atomicity, Anti-Collision, PoW Scaling)
            self.test_5_stress_and_advanced_adversarial_vectors()

            # Print Summary
            print("=" * 75)
            print(f"ADVERSARIAL SUITE RESULTS: {len(self.passed_tests)} Passed, {len(self.failed_tests)} Failed")
            print("=" * 75)

        # Cleanup
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

        return len(self.failed_tests) == 0

    # --------------------------------------------------------------------------
    # VECTOR 1: Blockchain Continuity & PoW
    # --------------------------------------------------------------------------
    def test_1_blockchain_continuity_and_pow(self):
        print("\n--- VECTOR 1: Blockchain Continuity & PoW Difficulty ---")
        try:
            # 1.1 Genesis block validation
            genesis = Block.query.filter_by(index=0).first()
            assert genesis is not None, "Genesis block missing from database."
            assert genesis.previous_hash == GENESIS_PREVIOUS_HASH, f"Genesis previous_hash is {genesis.previous_hash}"
            assert genesis.proof == 1, f"Genesis proof is {genesis.proof}"
            
            expected_gen_hash = compute_block_hash(
                0, genesis.timestamp.isoformat(), genesis.data, 1, GENESIS_PREVIOUS_HASH
            )
            assert genesis.hash == expected_gen_hash, "Genesis block hash mismatch."
            self.log_pass("1.1 Genesis Block Invariant Check")

            # 1.2 Bulk Issuance Block Mining (Multiple batches of diverse types)
            batch_sizes = [3, 5, 2] # 10 total credentials issued across 3 batches
            initial_count = Block.query.count()
            
            mined_docs = []
            valid_doc_types = list(DOC_TYPES.keys())
            with self.app.test_request_context('/issuer/bulk-issue'):
                for b_idx, size in enumerate(batch_sizes):
                    for i in range(size):
                        roll = f"CS2026_{b_idx}_{i:03d}"
                        dtype = valid_doc_types[(b_idx * 5 + i) % len(valid_doc_types)]
                        student = Student.query.filter_by(roll_number=roll).first()
                        if not student:
                            user = User(
                                username=f"student.{roll}".lower(),
                                email=f"{roll.lower()}@apex.edu",
                                role=ROLE_STUDENT,
                                organization='Apex University of Technology',
                                password_salt=generate_salt(16),
                                password_hash='dummyhash',
                                password_iterations=1000,
                            )
                            db.session.add(user)
                            db.session.flush()
                            student = Student(
                                user_id=user.id,
                                full_name=f"Student {roll}",
                                roll_number=roll,
                                institution='Apex University of Technology',
                            )
                            db.session.add(student)
                            db.session.flush()

                        doc = issue_credential(
                            student=student,
                            issuer=self.issuer,
                            doc_type=dtype,
                            title=f"{DOC_TYPES[dtype][0]} in CS - {roll}",
                            file_bytes=None,
                            difficulty=2,
                        )
                        mined_docs.append(doc)

            total_expected_blocks = initial_count + len(mined_docs)
            current_block_count = Block.query.count()
            assert current_block_count == total_expected_blocks, f"Expected {total_expected_blocks} blocks, found {current_block_count}"
            self.log_pass("1.2 Bulk Issuance Mining Count Check", f"({len(mined_docs)} blocks mined)")

            # 1.3 Strict Chain Continuity & Linkage Verification
            blocks = Block.query.order_by(Block.index.asc()).all()
            for idx, block in enumerate(blocks):
                assert block.index == idx, f"Block index gap: expected {idx}, found {block.index}"
                
                expected_hash = compute_block_hash(
                    block.index, block.timestamp.isoformat(), block.data, block.proof, block.previous_hash
                )
                assert block.hash == expected_hash, f"Block #{block.index} hash mismatch."
                
                if idx > 0:
                    prev_block = blocks[idx - 1]
                    assert block.previous_hash == prev_block.hash, f"Block #{block.index} previous_hash does not match block #{prev_block.index} hash."
                    guess = hashlib.sha256(f"{prev_block.proof}{block.proof}{block.index}".encode('utf-8')).hexdigest()
                    assert guess.startswith('0' * 2), f"Block #{block.index} PoW invalid: digest {guess} does not meet difficulty 2."
                    assert block.timestamp >= prev_block.timestamp, f"Block #{block.index} timestamp {block.timestamp} is before block #{prev_block.index} {prev_block.timestamp}"

            self.log_pass("1.3 Full Chain Linkage & PoW Difficulty Invariance", f"({len(blocks)} blocks verified)")

            # 1.4 validate_chain() system call
            ok, msg = validate_chain()
            assert ok, f"validate_chain() failed: {msg}"
            assert f"{len(blocks)} blocks verified" in msg, f"validate_chain message: {msg}"
            self.log_pass("1.4 System validate_chain() Execution", f"('{msg}')")

        except Exception as e:
            self.log_fail("VECTOR 1 (Blockchain Continuity)", e)

    # --------------------------------------------------------------------------
    # VECTOR 2: Cryptographic Hashing Invariance
    # --------------------------------------------------------------------------
    def test_2_cryptographic_hashing_invariance(self):
        print("\n--- VECTOR 2: Cryptographic Hashing Invariance ---")
        try:
            # 2.1 Standard Text-Only Credential Hashing Invariance
            roll = "TEST_HASH_001"
            student = Student.query.filter_by(roll_number=roll).first()
            if not student:
                user = User(
                    username=f"student.{roll}".lower(),
                    email=f"{roll.lower()}@apex.edu",
                    role=ROLE_STUDENT,
                    organization='Apex University of Technology',
                    password_salt=generate_salt(16),
                    password_hash='dummyhash',
                    password_iterations=1000,
                )
                db.session.add(user)
                db.session.flush()
                student = Student(
                    user_id=user.id,
                    full_name="Alice Invariant",
                    roll_number=roll,
                    institution='Apex University of Technology',
                )
                db.session.add(student)
                db.session.commit()

            with self.app.test_request_context('/issuer/issue'):
                doc = issue_credential(
                    student=student,
                    issuer=self.issuer,
                    doc_type='MARKSHEET',
                    title="Official Academic Marksheet 2026",
                    file_bytes=None,
                    difficulty=2,
                )

            # Check that create_document_hash equals recompute_document_hash
            metadata = json.loads(doc.payload)
            hash_on_issue = create_document_hash(None, metadata, doc.hash_salt)
            hash_on_recompute = recompute_document_hash(doc)

            assert hash_on_issue == doc.doc_hash, f"Hash on issue {hash_on_issue} != stored doc.doc_hash {doc.doc_hash}"
            assert hash_on_recompute == doc.doc_hash, f"Recomputed hash {hash_on_recompute} != stored doc.doc_hash {doc.doc_hash}"
            assert hashes_match(hash_on_recompute, doc.doc_hash), "hashes_match returned False"
            assert doc.file_digest is None, f"Expected doc.file_digest to be None for text-only credential, got {doc.file_digest}"
            
            self.log_pass("2.1 Text-Only Credential Hash Invariance", f"(Hash: {doc.doc_hash[:16]}...)")

            # 2.2 Public Verification Service on Text-Only Credential
            with self.app.test_request_context(f'/v/{doc.doc_hash}'):
                outcome = verify_hash(doc.doc_hash)
                assert outcome['ok'] is True, f"verify_hash failed: {outcome}"
                assert outcome['result'] == RESULT_VALID, f"Expected RESULT_VALID, got {outcome['result']}"
                assert outcome['chain_ok'] is True, f"Expected chain_ok True, got {outcome['chain_ok']}"
                assert outcome['doc'].id == doc.id, "Returned wrong doc"
                assert outcome['block'].index == doc.block_index, "Returned wrong block"
            self.log_pass("2.2 Public Verification Service Result for Text-Only Credential")

            # 2.3 Dynamic QR Token Verification on Bulk-Issued Credential
            with self.app.test_request_context(f'/v/{doc.doc_hash}'):
                token, exp = make_qr_token(doc.doc_hash, self.app.config['SECRET_KEY'], ttl=60)
                qr_outcome = verify_hash(doc.doc_hash, method='QR', qr_token=token)
                assert qr_outcome['ok'] is True and qr_outcome['result'] == RESULT_VALID, "Valid dynamic QR verification failed"
                
                # Test expired QR token
                expired_token, _ = make_qr_token(doc.doc_hash, self.app.config['SECRET_KEY'], ttl=-10)
                exp_outcome = verify_hash(doc.doc_hash, method='QR', qr_token=expired_token)
                assert exp_outcome['ok'] is False and exp_outcome['result'] == RESULT_QR_EXPIRED, "Expired QR token not rejected"
                
                # Test forged QR token
                forged_token = f"{int(time.time())+60}.{'0'*32}"
                forged_outcome = verify_hash(doc.doc_hash, method='QR', qr_token=forged_token)
                assert forged_outcome['ok'] is False and forged_outcome['result'] == RESULT_QR_EXPIRED, "Forged QR signature not rejected"
            self.log_pass("2.3 Dynamic QR Token Public Verification on Text-Only Credential")

            # 2.4 Edge Cases: Unicode, Non-ASCII Characters, Special Symbols
            edge_cases = [
                {"name": "Devanagari Unicode", "student_name": "सत्यमेव जयते", "title": "अकादमिक प्रमाणपत्र", "extra": {"श्रेणी": "प्रथम"}},
                {"name": "Accented & Emojis", "student_name": "Émilie Nöel 🎓", "title": "Diplôme d'Honneur #2026 & <special>", "extra": {"grade": "A+"}},
                {"name": "Punctuation & Slashing", "student_name": "O'Connor / Smith-Jones", "title": "Certificate: (Honors) [Level-4] \"Distinction\"", "extra": None},
                {"name": "Empty string fields in extra", "student_name": "Bob Normal", "title": "Standard Diploma", "extra": {"notes": "", "honors": ""}},
            ]

            with self.app.test_request_context('/issuer/issue'):
                for case in edge_cases:
                    edge_roll = f"EDGE_{abs(hash(case['name'])) % 100000:05d}"
                    user = User(
                        username=f"student.{edge_roll}".lower(),
                        email=f"{edge_roll.lower()}@apex.edu",
                        role=ROLE_STUDENT,
                        organization='Apex University of Technology',
                        password_salt=generate_salt(16),
                        password_hash='dummyhash',
                        password_iterations=1000,
                    )
                    db.session.add(user)
                    db.session.flush()
                    edge_student = Student(
                        user_id=user.id,
                        full_name=case['student_name'],
                        roll_number=edge_roll,
                        institution='Apex University of Technology',
                    )
                    db.session.add(edge_student)
                    db.session.commit()

                    edge_doc = issue_credential(
                        student=edge_student,
                        issuer=self.issuer,
                        doc_type='BONAFIDE',
                        title=case['title'],
                        file_bytes=None,
                        extra=case['extra'],
                        difficulty=2,
                    )

                    meta = json.loads(edge_doc.payload)
                    h_issue = create_document_hash(None, meta, edge_doc.hash_salt)
                    h_recomp = recompute_document_hash(edge_doc)
                    assert h_issue == edge_doc.doc_hash == h_recomp, f"Hash mismatch on {case['name']}"
                    
                    with self.app.test_request_context(f'/v/{edge_doc.doc_hash}'):
                        v_out = verify_hash(edge_doc.doc_hash)
                        assert v_out['ok'] is True and v_out['result'] == RESULT_VALID, f"Verification failed for {case['name']}"

            self.log_pass("2.4 Unicode, Special Characters & Metadata Edge Invariance")

            # 2.5 Deterministic Canonical JSON ordering check
            d1 = {"b": 2, "a": 1, "nested": {"z": 10, "y": 20}}
            d2 = {"nested": {"y": 20, "z": 10}, "a": 1, "b": 2}
            assert canonical_payload(d1) == canonical_payload(d2) == '{"a":1,"b":2,"nested":{"y":20,"z":10}}', "canonical_payload not strictly deterministic"
            self.log_pass("2.5 Canonical Payload Determinism Invariance")

        except Exception as e:
            self.log_fail("VECTOR 2 (Cryptographic Hashing Invariance)", e)

    # --------------------------------------------------------------------------
    # VECTOR 3: Dual-Persistence Parity & State Recovery
    # --------------------------------------------------------------------------
    def test_3_dual_persistence_sync_and_recovery(self):
        print("\n--- VECTOR 3: Dual-Persistence Parity & State Recovery ---")
        try:
            # 3.1 Strict Parity Check between SQLite and instance/blockchain.json
            assert os.path.exists(test_json_file), f"Blockchain JSON file not found at {test_json_file}"
            with open(test_json_file, 'r', encoding='utf-8') as f:
                json_blocks = json.load(f)

            db_blocks = Block.query.order_by(Block.index.asc()).all()
            assert len(db_blocks) == len(json_blocks), f"Count mismatch: DB has {len(db_blocks)}, JSON has {len(json_blocks)}"

            for db_b, js_b in zip(db_blocks, json_blocks):
                assert db_b.index == js_b['index'], f"Index mismatch: DB {db_b.index} vs JSON {js_b['index']}"
                assert db_b.hash == js_b['hash'], f"Hash mismatch at block #{db_b.index}"
                assert db_b.previous_hash == js_b['previous_hash'], f"Previous hash mismatch at block #{db_b.index}"
                assert db_b.data == js_b['data'], f"Data payload mismatch at block #{db_b.index}"
                assert db_b.proof == js_b['proof'], f"Proof mismatch at block #{db_b.index}"
                assert db_b.timestamp.isoformat() == js_b['timestamp'], f"Timestamp mismatch at block #{db_b.index}"
                assert db_b.doc_hash == js_b.get('doc_hash'), f"Doc hash mismatch at block #{db_b.index}"

            self.log_pass("3.1 Exact Parity: SQLite `block` Table == `instance/blockchain.json`", f"({len(db_blocks)} blocks matching)")

            # 3.2 State Recovery Scenario A: JSON file deleted -> Resync from DB via save_to_json()
            backup_json = copy.deepcopy(json_blocks)
            os.remove(test_json_file)
            assert not os.path.exists(test_json_file), "Failed to delete JSON file for test."
            
            res = blockchain_instance.save_to_json(test_json_file)
            assert res is True, "save_to_json returned False"
            assert os.path.exists(test_json_file), "JSON file was not recreated."
            
            with open(test_json_file, 'r', encoding='utf-8') as f:
                restored_json = json.load(f)
            assert restored_json == backup_json, "Restored JSON file does not match backup."
            self.log_pass("3.2 State Recovery Scenario A: JSON reconstruction from DB")

            # 3.3 State Recovery Scenario B: Database blocks deleted -> Resync from JSON via load_from_json()
            db_blocks_count_before = Block.query.count()
            Block.query.delete()
            db.session.commit()
            assert Block.query.count() == 0, "Failed to empty Block table for recovery test."

            # Calling validate_chain() automatically triggers load_from_json() when DB is empty
            ok, msg = validate_chain()
            assert ok, f"validate_chain failed after DB clear: {msg}"
            
            restored_db_count = Block.query.count()
            assert restored_db_count == db_blocks_count_before, f"Expected {db_blocks_count_before} restored blocks, got {restored_db_count}"
            self.log_pass("3.3 State Recovery Scenario B: DB reconstruction from JSON during validate_chain()")

        except Exception as e:
            self.log_fail("VECTOR 3 (Dual-Persistence & Recovery)", e)

    # --------------------------------------------------------------------------
    # VECTOR 4: Adversarial Tamper Resistance & Mutation Attacks
    # --------------------------------------------------------------------------
    def test_4_tamper_resistance_attacks(self):
        print("\n--- VECTOR 4: Adversarial Tamper Resistance & Attack Scenarios ---")
        try:
            # Pick a middle block to mutate
            target_block = Block.query.filter(Block.index > 1).first()
            assert target_block is not None, "Need at least 2 blocks to test middle block mutation."
            target_index = target_block.index
            original_data = target_block.data
            original_hash = target_block.hash
            original_prev_hash = target_block.previous_hash
            original_proof = target_block.proof

            # ATTACK 4.1: Modify Block Data payload in SQLite DB without altering block hash
            print("  -> Testing Attack 4.1: Silent DB Block Data modification...")
            tampered_data = json.dumps({"forged": True, "original": original_data})
            target_block.data = tampered_data
            db.session.commit()

            ok, msg = validate_chain()
            assert ok is False, "validate_chain() failed to detect modified block data payload!"
            assert f"Block #{target_index} hash mismatch" in msg, f"Unexpected message: {msg}"
            self.log_pass("4.1 Attack Detected: Block payload tampering caught by validate_chain()")

            # Revert 4.1
            target_block.data = original_data
            db.session.commit()
            ok, _ = validate_chain()
            assert ok is True, "Revert failed"

            # ATTACK 4.2: Break Previous Hash Linkage in DB
            print("  -> Testing Attack 4.2: Breaking block previous_hash pointer...")
            target_block.previous_hash = "f" * 64
            target_block.hash = compute_block_hash(
                target_block.index, target_block.timestamp.isoformat(),
                target_block.data, target_block.proof, target_block.previous_hash
            )
            db.session.commit()

            ok, msg = validate_chain()
            assert ok is False, "validate_chain() failed to detect broken chain linkage!"
            assert f"Block #{target_index} does not link to block #{target_index - 1}" in msg, f"Unexpected msg: {msg}"
            self.log_pass("4.2 Attack Detected: Broken chain pointer caught by validate_chain()")

            # Revert 4.2
            target_block.previous_hash = original_prev_hash
            target_block.hash = original_hash
            db.session.commit()
            ok, _ = validate_chain()
            assert ok is True, "Revert failed"

            # ATTACK 4.3: Tamper with Proof-of-Work Nonce
            print("  -> Testing Attack 4.3: Proof-of-work tampering...")
            target_block.proof = target_block.proof + 99999
            db.session.commit()

            ok, msg = validate_chain()
            assert ok is False, "validate_chain() failed to detect PoW proof tampering!"
            assert f"Block #{target_index} hash mismatch" in msg, f"Unexpected msg: {msg}"
            self.log_pass("4.3 Attack Detected: PoW proof tampering caught by validate_chain()")

            # Revert 4.3
            target_block.proof = original_proof
            db.session.commit()
            ok, _ = validate_chain()
            assert ok is True, "Revert failed"

            # ATTACK 4.4: Corrupt Genesis Block Previous Hash
            print("  -> Testing Attack 4.4: Genesis block corruption...")
            gen_block = Block.query.filter_by(index=0).first()
            orig_gen_prev = gen_block.previous_hash
            orig_gen_hash = gen_block.hash
            
            gen_block.previous_hash = "1" * 64
            gen_block.hash = compute_block_hash(
                0, gen_block.timestamp.isoformat(), gen_block.data, gen_block.proof, gen_block.previous_hash
            )
            db.session.commit()

            ok, msg = validate_chain()
            assert ok is False, "validate_chain() failed to detect corrupted genesis block!"
            assert "Genesis block has an unexpected parent" in msg, f"Unexpected msg: {msg}"
            self.log_pass("4.4 Attack Detected: Corrupted genesis parent caught by validate_chain()")

            # Revert 4.4
            gen_block.previous_hash = orig_gen_prev
            gen_block.hash = orig_gen_hash
            db.session.commit()
            ok, _ = validate_chain()
            assert ok is True, "Revert failed"

            # ATTACK 4.5: Document Payload Tampering (Doc Table vs Blockchain Anchor)
            print("  -> Testing Attack 4.5: Document table metadata alteration...")
            test_doc = Doc.query.first()
            assert test_doc is not None, "Need at least 1 Doc record"
            orig_payload = test_doc.payload
            
            tampered_meta = json.loads(orig_payload)
            tampered_meta['title'] = "TAMPERED DEGREE - FORGED TITLE"
            test_doc.payload = canonical_payload(tampered_meta)
            db.session.commit()

            with self.app.test_request_context(f'/v/{test_doc.doc_hash}'):
                recomputed = recompute_document_hash(test_doc)
                assert recomputed != test_doc.doc_hash, f"Recomputed hash should differ after tampering: {recomputed} == {test_doc.doc_hash}"

                ver_res = verify_hash(test_doc.doc_hash)
                assert ver_res['ok'] is False, "verify_hash returned ok=True on tampered document!"
                assert ver_res['result'] == RESULT_TAMPERED, f"Expected RESULT_TAMPERED, got {ver_res['result']}"
                assert "Integrity check failed" in ver_res['message'], f"Unexpected message: {ver_res['message']}"
            self.log_pass("4.5 Attack Detected: Stored Doc payload alteration caught by verification service")

            # Revert 4.5
            test_doc.payload = orig_payload
            db.session.commit()
            with self.app.test_request_context(f'/v/{test_doc.doc_hash}'):
                ver_res = verify_hash(test_doc.doc_hash)
                assert ver_res['ok'] is True and ver_res['result'] == RESULT_VALID, "Revert failed for Doc payload"

            # ATTACK 4.6: Alter doc.hash_salt or doc.file_digest
            print("  -> Testing Attack 4.6: Altering document hash salt and file digest...")
            orig_salt = test_doc.hash_salt
            test_doc.hash_salt = "0000000000000000"
            db.session.commit()
            with self.app.test_request_context(f'/v/{test_doc.doc_hash}'):
                ver_res_salt = verify_hash(test_doc.doc_hash)
                assert ver_res_salt['ok'] is False and ver_res_salt['result'] == RESULT_TAMPERED, "Salt tampering not detected"

            test_doc.hash_salt = orig_salt
            test_doc.file_digest = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            db.session.commit()
            with self.app.test_request_context(f'/v/{test_doc.doc_hash}'):
                ver_res_digest = verify_hash(test_doc.doc_hash)
                assert ver_res_digest['ok'] is False and ver_res_digest['result'] == RESULT_TAMPERED, "File digest injection on text-only doc not detected"

            # Revert 4.6
            test_doc.file_digest = None
            db.session.commit()
            with self.app.test_request_context(f'/v/{test_doc.doc_hash}'):
                ver_res_clean = verify_hash(test_doc.doc_hash)
                assert ver_res_clean['ok'] is True and ver_res_clean['result'] == RESULT_VALID, "Clean revert failed"
            self.log_pass("4.6 Attack Detected: Hash salt and file digest mutation detected")

            # ATTACK 4.7: Chain Gap Detection (Delete a block in the middle)
            print("  -> Testing Attack 4.7: Block deletion causing gap...")
            os.rename(test_json_file, test_json_file + '.bak')
            deleted_block = Block.query.filter_by(index=2).first()
            if deleted_block:
                db.session.delete(deleted_block)
                db.session.commit()
                ok, msg = validate_chain()
                assert ok is False, "validate_chain failed to detect missing block / index gap!"
                assert "does not link to" in msg or "Chain has a gap" in msg or "hash mismatch" in msg, f"Unexpected msg: {msg}"
                self.log_pass("4.7 Attack Detected: Chain gap detected by validate_chain()")

            # Restore
            os.rename(test_json_file + '.bak', test_json_file)
            Block.query.delete()
            db.session.commit()
            ok, msg = validate_chain()
            assert ok is True, f"Full restore from JSON failed: {msg}"
            self.log_pass("4.8 State Restoration: Full restore and validate_chain() after gap attack")

        except Exception as e:
            self.log_fail("VECTOR 4 (Tamper Resistance Attacks)", e)

    # --------------------------------------------------------------------------
    # VECTOR 5: Stress & Advanced Adversarial Vectors
    # --------------------------------------------------------------------------
    def test_5_stress_and_advanced_adversarial_vectors(self):
        print("\n--- VECTOR 5: Stress, Scale & Advanced Vectors ---")
        try:
            # 5.1 Anti-Rainbow Table & Salting Uniqueness Test
            print("  -> 5.1 Testing Salt Collision Resistance across 50 identical credentials...")
            hashes = set()
            salts = set()
            dummy_meta = {
                'student_name': 'Same Student',
                'roll_number': 'SAME_ROLL_001',
                'program': 'Same Program',
                'department': 'Same Dept',
                'institution': 'Apex University',
                'doc_type': 'DEGREE',
                'title': 'Same Degree',
                'issuer': 'Apex University',
                'issued_on': '2026-08-29T00:00:00',
            }
            for _ in range(50):
                s = generate_salt(16)
                h = create_document_hash(None, dummy_meta, s)
                salts.add(s)
                hashes.add(h)

            assert len(salts) == 50, f"Salt collision detected: {len(salts)} / 50"
            assert len(hashes) == 50, f"Hash collision on identical metadata: {len(hashes)} / 50"
            self.log_pass("5.1 Anti-Collision & Salting Uniqueness (50/50 unique hashes for identical metadata)")

            # 5.2 PoW Difficulty Scaling Test (1 to 4 leading zeros)
            print("  -> 5.2 Testing PoW Difficulty Scaling (1, 2, 3, 4)...")
            prev_proof = 100
            for diff in [1, 2, 3, 4]:
                t0 = time.time()
                nonce = blockchain_instance.proof_of_work(prev_proof, index=999, difficulty=diff)
                t_elapsed = time.time() - t0
                digest = hashlib.sha256(f"{prev_proof}{nonce}999".encode('utf-8')).hexdigest()
                assert digest.startswith('0' * diff), f"PoW failed for difficulty {diff}: {digest}"
                prev_proof = nonce
            self.log_pass("5.2 PoW Difficulty Invariant (Levels 1 to 4 validated)")

            # 5.3 HTTP Bulk Issue Endpoint: All-or-Nothing Atomicity Stress Test
            print("  -> 5.3 Testing HTTP /issuer/bulk-issue All-or-Nothing Atomicity via Test Client...")
            client = self.app.test_client()
            
            # Authenticate via /login route using form identifier
            login_resp = client.post('/login', data={
                'identifier': self.issuer.username,
                'password': 'pass123',
            }, follow_redirects=True)
            assert login_resp.status_code == 200, f"Login failed: {login_resp.status_code}"

            doc_count_before = Doc.query.count()
            block_count_before = Block.query.count()

            # Corrupted CSV with missing roll_number in middle row
            corrupt_csv = (
                "roll_number,doc_type,title,student_name\n"
                "STRESS_001,DEGREE,B.Tech 1,Student 1\n"
                "STRESS_002,DEGREE,B.Tech 2,Student 2\n"
                ",DEGREE,B.Tech 3,Student 3\n" # Missing roll_number
                "STRESS_004,DEGREE,B.Tech 4,Student 4\n"
            )
            
            resp = client.post(
                '/issuer/bulk-issue',
                data={'csv_file': (io.BytesIO(corrupt_csv.encode('utf-8')), 'corrupt.csv')},
                content_type='multipart/form-data',
            )
            assert resp.status_code == 400, f"Expected HTTP 400 on invalid batch, got {resp.status_code}"
            
            # Verify 0 documents created and 0 blocks mined
            doc_count_after = Doc.query.count()
            block_count_after = Block.query.count()
            assert doc_count_after == doc_count_before, f"Atomicity violated: doc count changed from {doc_count_before} to {doc_count_after}"
            assert block_count_after == block_count_before, f"Atomicity violated: block count changed from {block_count_before} to {block_count_after}"
            
            ok, msg = validate_chain()
            assert ok is True, f"Chain corrupted after rejected bulk upload: {msg}"
            self.log_pass("5.3 HTTP Bulk Issue All-or-Nothing Atomicity: 0 Docs, 0 Blocks Created on Rejected Batch")

            # 5.4 HTTP Bulk Issue Endpoint: Valid 5-row Batch Upload via Test Client
            print("  -> 5.4 Testing HTTP /issuer/bulk-issue Valid Batch via Test Client...")
            valid_csv = (
                "roll_number,doc_type,title,student_name,validity_days\n"
                "BULK_HTTP_001,DEGREE,B.Tech CS,Student H1,3650\n"
                "BULK_HTTP_002,MARKSHEET,Semester 8 Marksheet,Student H2,3650\n"
                "BULK_HTTP_003,BONAFIDE,Bonafide Certificate,Student H3,90\n"
                "BULK_HTTP_004,INTERNSHIP,Internship Certificate,Student H4,730\n"
                "BULK_HTTP_005,TC,Transfer Certificate,Student H5,180\n"
            )
            resp = client.post(
                '/issuer/bulk-issue',
                data={'csv_file': (io.BytesIO(valid_csv.encode('utf-8')), 'valid_batch.csv')},
                content_type='multipart/form-data',
                follow_redirects=True,
            )
            assert resp.status_code == 200, f"Expected HTTP 200 after redirect, got {resp.status_code}"
            
            doc_count_final = Doc.query.count()
            block_count_final = Block.query.count()
            assert doc_count_final == doc_count_before + 5, f"Expected +5 docs, got {doc_count_final - doc_count_before}"
            assert block_count_final == block_count_before + 5, f"Expected +5 blocks, got {block_count_final - block_count_before}"

            ok, msg = validate_chain()
            assert ok is True, f"Chain validation failed after valid bulk upload: {msg}"
            self.log_pass("5.4 HTTP Bulk Issue Valid Batch: Exactly 5 Docs & 5 Blocks Mined with Intact Chain")

        except Exception as e:
            self.log_fail("VECTOR 5 (Stress & Advanced Vectors)", e)
        finally:
            blockchain_instance.storage_file = self.orig_storage
            blockchain_instance.difficulty = self.orig_diff
            os.environ.pop('DATABASE_URL', None)
            shutil.rmtree(temp_dir, ignore_errors=True)

        return len(self.failed_tests) == 0


if __name__ == '__main__':
    runner = AdversarialTestRunner()
    success = runner.run_all()
    if not success:
        sys.exit(1)
    else:
        print("\nALL ADVERSARIAL CHALLENGES PASSED EMPIRICALLY!")
