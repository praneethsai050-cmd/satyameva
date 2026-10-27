"""
Model Context Protocol (MCP) Server for Satyameva Aegis.

Implements the official Model Context Protocol (JSON-RPC 2.0 stdio transport)
enabling AI agents, evaluators, and LLM orchestration tools (Claude Desktop,
Antigravity, Cursor, etc.) to query the decentralized blockchain ledger,
verify credentials, audit blocks, inspect telemetry, and extract documents.

Usage:
    python mcp_server.py             # Runs standard stdio JSON-RPC 2.0 MCP server
    python mcp_server.py --test      # Runs self-test of all MCP tools and resources
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from blockchain import blockchain_instance, get_chain_data, validate_chain
from extensions import db, utcnow
from models.block import Block
from models.document import Doc
from models.fraud_report import FraudReport
from models.institution import Institution
from models.student import Student
from models.verification_log import VerificationLog
from services.verification_service import verify_hash

# Configure logging to stderr so stdout remains pure JSON-RPC
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [MCP] %(message)s'
)
logger = logging.getLogger('satyameva-mcp')

# Global Flask application context
_flask_app = None


def get_app():
    global _flask_app
    if _flask_app is None:
        _flask_app = create_app()
    return _flask_app


# ─── Tool Implementations ───────────────────────────────────────────────────────

def tool_verify_credential(doc_hash: str, qr_token: Optional[str] = None) -> Dict[str, Any]:
    """Cryptographically verify a credential against the Satyameva blockchain ledger."""
    app = get_app()
    with app.app_context():
        res = verify_hash(doc_hash, method='QR' if qr_token else 'HASH', qr_token=qr_token, label='MCP Agent')
        doc = res.get('doc')
        block = res.get('block')
        is_valid = res.get('ok', False)
        result_code = res.get('result', 'UNKNOWN')

        data: Dict[str, Any] = {
            'doc_hash': doc_hash,
            'result': result_code,
            'is_valid': is_valid,
            'message': res.get('message', ''),
            'chain_ok': res.get('chain_ok', True),
            'chain_message': res.get('chain_message', ''),
            'reveals_holder': is_valid,
        }

        if doc:
            data.update({
                'title': doc.title,
                'doc_type': doc.doc_type,
                'type_label': doc.type_label,
                'block_index': doc.block_index,
                'issued_on': doc.issued_on.isoformat() if doc.issued_on else None,
                'valid_until': doc.valid_until.isoformat() if doc.valid_until else None,
                'is_revoked': doc.revoked,
                'verification_count': doc.verification_count,
                'issuer_name': doc.issuer_name,
                'has_digital_signature': bool(doc.signature),
                'signature': doc.signature,
                'issuer_public_key': doc.issuer_public_key,
            })
            if is_valid and doc.student:
                data['student'] = {
                    'full_name': doc.student.full_name,
                    'roll_number': doc.student.roll_number,
                    'program': doc.student.program,
                    'department': doc.student.department,
                    'institution': doc.student.institution,
                }
        if block:
            data['block'] = {
                'index': block.index,
                'hash': block.hash,
                'proof': block.proof,
                'timestamp': block.timestamp.isoformat() if block.timestamp else None,
            }
        return data


def tool_get_blockchain_info() -> Dict[str, Any]:
    """Get real-time health, height, difficulty, and consensus validity of the blockchain."""
    app = get_app()
    with app.app_context():
        ok, msg = validate_chain()
        chain = get_chain_data()
        last_block = blockchain_instance.get_last_block()
        return {
            'is_valid': ok,
            'validation_message': msg,
            'total_blocks': len(chain),
            'difficulty': blockchain_instance.difficulty,
            'last_block_index': last_block.index if last_block else None,
            'last_block_hash': last_block.hash if last_block else None,
            'storage_file': blockchain_instance.storage_file,
            'registered_nodes': list(blockchain_instance.nodes),
        }


def tool_get_block_by_index(block_index: int) -> Dict[str, Any]:
    """Inspect full cryptographic block header, proof, previous hash, and transactions."""
    app = get_app()
    with app.app_context():
        blk = Block.query.filter_by(index=block_index).first()
        if not blk:
            return {'error': f'Block #{block_index} not found on the ledger.'}
        return {
            'index': blk.index,
            'timestamp': blk.timestamp.isoformat() if blk.timestamp else None,
            'data': blk.data,
            'proof': blk.proof,
            'hash': blk.hash,
            'previous_hash': blk.previous_hash,
            'doc_hash': blk.doc_hash,
            'signature': blk.signature,
            'miner_public_key': blk.miner_public_key,
        }


def tool_audit_student_records(roll_number: str) -> Dict[str, Any]:
    """Audit academic credential inventory for a student roll number."""
    app = get_app()
    with app.app_context():
        student = Student.query.filter_by(roll_number=roll_number.strip()).first()
        if not student:
            return {'error': f'No student found with roll number: {roll_number}'}

        docs = []
        for d in student.documents:
            docs.append({
                'id': d.id,
                'doc_type': d.doc_type,
                'title': d.title,
                'doc_hash': d.doc_hash,
                'block_index': d.block_index,
                'issued_on': d.issued_on.isoformat() if d.issued_on else None,
                'valid_until': d.valid_until.isoformat() if d.valid_until else None,
                'revoked': d.revoked,
                'verification_count': d.verification_count,
            })

        return {
            'student_name': student.full_name,
            'roll_number': student.roll_number,
            'program': student.program,
            'department': student.department,
            'institution': student.institution,
            'batch': student.batch,
            'documents_count': len(docs),
            'documents': docs,
        }


def tool_submit_fraud_report(doc_hash: str, reason: str, reporter_email: Optional[str] = None) -> Dict[str, Any]:
    """Submit an immutable fraud telemetry alert for a suspected or forged credential."""
    app = get_app()
    with app.app_context():
        doc = Doc.query.filter_by(doc_hash=doc_hash.strip()).first()
        report = FraudReport(
            doc_id=doc.id if doc else None,
            doc_hash=doc_hash.strip(),
            reported_by_id=None,
            reporter_email=reporter_email or 'mcp-agent@satyameva.in',
            reason=reason.strip(),
            ip_address='127.0.0.1',
            user_agent='Satyameva MCP Server / 1.0',
            status='PENDING',
        )
        db.session.add(report)
        db.session.commit()
        return {
            'report_id': report.id,
            'status': 'PENDING',
            'doc_hash': doc_hash,
            'message': 'Fraud report successfully registered in forensic audit queue.',
        }


def tool_extract_academic_document(file_path: str) -> Dict[str, Any]:
    """Extract academic fields from an uploaded document scan using Gemini 2.0 Flash."""
    app = get_app()
    with app.app_context():
        api_key = app.config.get('GEMINI_API_KEY')
        if not api_key:
            return {'error': 'GEMINI_API_KEY is not configured on this node.'}
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}

        from services.gemini_service import extract_document_fields
        with open(file_path, 'rb') as f:
            bytes_data = f.read()

        mime = 'application/pdf' if file_path.lower().endswith('.pdf') else 'image/png'
        extracted = extract_document_fields(bytes_data, mime, api_key)
        return {'file_path': file_path, 'extracted': extracted}


# ─── MCP Definition Schema ──────────────────────────────────────────────────────

MCP_TOOLS = [
    {
        'name': 'verify_credential',
        'description': 'Cryptographically verify an academic credential by its 64-char SHA-256 hash or dynamic QR token.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'doc_hash': {'type': 'string', 'description': 'The 64-character hexadecimal credential hash'},
                'qr_token': {'type': 'string', 'description': 'Optional dynamic 60s QR token string (expiry.signature)'},
            },
            'required': ['doc_hash'],
        },
    },
    {
        'name': 'get_blockchain_info',
        'description': 'Get live blockchain state, proof-of-work difficulty, total height, and cryptographic consensus integrity.',
        'inputSchema': {
            'type': 'object',
            'properties': {},
        },
    },
    {
        'name': 'get_block_by_index',
        'description': 'Retrieve block details and transaction bindings for a specific block index on the chain.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'block_index': {'type': 'integer', 'description': 'Block index number (e.g. 0 for Genesis, 1, 2, ...)'},
            },
            'required': ['block_index'],
        },
    },
    {
        'name': 'audit_student_records',
        'description': 'Retrieve complete academic credential portfolio and on-chain verification logs for a student roll number.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'roll_number': {'type': 'string', 'description': 'The university student roll number (e.g. 22103050)'},
            },
            'required': ['roll_number'],
        },
    },
    {
        'name': 'submit_fraud_report',
        'description': 'Register an adversarial tamper alert or fraud report for a fraudulent or manipulated academic certificate.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'doc_hash': {'type': 'string', 'description': 'Target 64-character credential hash'},
                'reason': {'type': 'string', 'description': 'Detailed forensic reason or evidence of tampering'},
                'reporter_email': {'type': 'string', 'description': 'Contact email of the verifier or auditing entity'},
            },
            'required': ['doc_hash', 'reason'],
        },
    },
    {
        'name': 'extract_academic_document',
        'description': 'Parse scanned degree or marksheet PDFs/images using Google Gemini 2.0 Flash AI multimodal parser.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'file_path': {'type': 'string', 'description': 'Absolute path to local PDF or image document'},
            },
            'required': ['file_path'],
        },
    },
]

MCP_RESOURCES = [
    {
        'uri': 'satyameva://blockchain/ledger',
        'name': 'Blockchain Ledger',
        'description': 'Full active Proof-of-Work blockchain ledger containing all mined blocks and transaction proofs.',
        'mimeType': 'application/json',
    },
    {
        'uri': 'satyameva://institutions/registry',
        'name': 'Approved Institutions Registry',
        'description': 'Official registry of pre-approved academic institutions (JIIT, JUIT, JUET) authorized to issue credentials.',
        'mimeType': 'application/json',
    },
    {
        'uri': 'satyameva://stats/telemetry',
        'name': 'Verification Telemetry',
        'description': 'Aggregated operational metrics including total credentials issued, verification attempts, and active nodes.',
        'mimeType': 'application/json',
    },
]

MCP_PROMPTS = [
    {
        'name': 'audit_credential',
        'description': 'Conduct a comprehensive cryptographic audit of a student academic credential.',
        'arguments': [
            {'name': 'doc_hash', 'description': 'The 64-character SHA-256 hash of the credential', 'required': True},
        ],
    },
    {
        'name': 'institution_compliance_check',
        'description': 'Audit institutional issuance authority, subscription validity, and cryptographic signature keypair.',
        'arguments': [
            {'name': 'short_code', 'description': 'Institution campus code (e.g. JUIT, JIIT, JUET)', 'required': True},
        ],
    },
]


# ─── Resource Handlers ──────────────────────────────────────────────────────────

def read_resource(uri: str) -> str:
    app = get_app()
    with app.app_context():
        if uri == 'satyameva://blockchain/ledger':
            return json.dumps(get_chain_data(), indent=2)
        elif uri == 'satyameva://institutions/registry':
            insts = Institution.query.all()
            data = [
                {
                    'id': i.id,
                    'name': i.name,
                    'short_code': i.short_code,
                    'domain': i.domain,
                    'is_approved': i.is_approved,
                    'subscription_is_active': i.subscription_is_active,
                }
                for i in insts
            ]
            return json.dumps(data, indent=2)
        elif uri == 'satyameva://stats/telemetry':
            doc_count = Doc.query.count()
            verif_count = VerificationLog.query.count()
            block_count = Block.query.count()
            student_count = Student.query.count()
            data = {
                'total_credentials_anchored': doc_count,
                'total_verifications_logged': verif_count,
                'blockchain_height': block_count,
                'registered_students': student_count,
                'timestamp': utcnow().isoformat(),
            }
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f'Unknown resource URI: {uri}')


# ─── JSON-RPC Protocol Dispatcher ──────────────────────────────────────────────

def handle_rpc_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = req.get('method')
    req_id = req.get('id')
    params = req.get('params', {})

    if method == 'initialize':
        return {
            'jsonrpc': '2.0',
            'id': req_id,
            'result': {
                'protocolVersion': '2024-11-05',
                'serverInfo': {
                    'name': 'satyameva-aegis-mcp',
                    'version': '1.0.0',
                },
                'capabilities': {
                    'tools': {'listChanged': False},
                    'resources': {'subscribe': False, 'listChanged': False},
                    'prompts': {'listChanged': False},
                },
            },
        }

    elif method == 'tools/list':
        return {
            'jsonrpc': '2.0',
            'id': req_id,
            'result': {'tools': MCP_TOOLS},
        }

    elif method == 'tools/call':
        name = params.get('name')
        args = params.get('arguments', {})

        try:
            if name == 'verify_credential':
                content = tool_verify_credential(args.get('doc_hash', ''), args.get('qr_token'))
            elif name == 'get_blockchain_info':
                content = tool_get_blockchain_info()
            elif name == 'get_block_by_index':
                content = tool_get_block_by_index(int(args.get('block_index', 0)))
            elif name == 'audit_student_records':
                content = tool_audit_student_records(args.get('roll_number', ''))
            elif name == 'submit_fraud_report':
                content = tool_submit_fraud_report(args.get('doc_hash', ''), args.get('reason', ''), args.get('reporter_email'))
            elif name == 'extract_academic_document':
                content = tool_extract_academic_document(args.get('file_path', ''))
            else:
                return {
                    'jsonrpc': '2.0',
                    'id': req_id,
                    'error': {'code': -32601, 'message': f'Method not found: {name}'},
                }

            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'content': [{'type': 'text', 'text': json.dumps(content, indent=2)}],
                    'isError': False,
                },
            }
        except Exception as exc:
            logger.error('Error executing tool %s: %s', name, exc, exc_info=True)
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'content': [{'type': 'text', 'text': f'Tool execution error: {str(exc)}'}],
                    'isError': True,
                },
            }

    elif method == 'resources/list':
        return {
            'jsonrpc': '2.0',
            'id': req_id,
            'result': {'resources': MCP_RESOURCES},
        }

    elif method == 'resources/read':
        uri = params.get('uri')
        try:
            text = read_resource(uri)
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'contents': [{'uri': uri, 'mimeType': 'application/json', 'text': text}],
                },
            }
        except Exception as exc:
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'error': {'code': -32602, 'message': str(exc)},
            }

    elif method == 'prompts/list':
        return {
            'jsonrpc': '2.0',
            'id': req_id,
            'result': {'prompts': MCP_PROMPTS},
        }

    elif method == 'prompts/get':
        pname = params.get('name')
        pargs = params.get('arguments', {})
        if pname == 'audit_credential':
            h = pargs.get('doc_hash', '<DOC_HASH>')
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'description': 'Audit credential on Satyameva Aegis',
                    'messages': [
                        {
                            'role': 'user',
                            'content': {
                                'type': 'text',
                                'text': f"Perform a comprehensive cryptographic verification and audit for credential hash '{h}'. Check blockchain anchoring, previous block continuity, and student ownership.",
                            },
                        }
                    ],
                },
            }
        elif pname == 'institution_compliance_check':
            code = pargs.get('short_code', '<CAMPUS>')
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'description': 'Audit institutional compliance',
                    'messages': [
                        {
                            'role': 'user',
                            'content': {
                                'type': 'text',
                                'text': f"Audit the operational compliance, active subscription status, and ECDSA signing key integrity for campus '{code}'.",
                            },
                        }
                    ],
                },
            }
        else:
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'error': {'code': -32601, 'message': f'Prompt {pname} not found'},
            }

    elif method == 'notifications/initialized':
        return None

    else:
        return {
            'jsonrpc': '2.0',
            'id': req_id,
            'error': {'code': -32601, 'message': f'Unhandled MCP method: {method}'},
        }


# ─── Main Execution & Self-Test ─────────────────────────────────────────────────

def run_self_test():
    """Runs a standalone diagnostic suite checking all MCP tools and resources."""
    print('====================================================')
    print('  Satyameva Aegis MCP Server Self-Diagnostic Suite  ')
    print('====================================================')

    # Test 1: get_blockchain_info
    print('[1/5] Testing tool: get_blockchain_info...')
    info = tool_get_blockchain_info()
    assert info['is_valid'] is True, f"Chain invalid: {info}"
    print(f"      [OK] Total Blocks: {info['total_blocks']} | Valid: {info['is_valid']}")

    # Test 2: get_block_by_index
    print('[2/5] Testing tool: get_block_by_index #0 (Genesis)...')
    genesis = tool_get_block_by_index(0)
    assert genesis['index'] == 0, f"Genesis error: {genesis}"
    print(f"      [OK] Genesis Hash: {genesis['hash'][:16]}... | Proof: {genesis['proof']}")

    # Test 3: audit_student_records
    print('[3/5] Testing tool: audit_student_records for 22103050...')
    student_res = tool_audit_student_records('22103050')
    assert 'documents' in student_res, f"Student audit failed: {student_res}"
    print(f"      [OK] Student: {student_res['student_name']} | Docs: {student_res['documents_count']}")

    # Test 4: verify_credential
    if student_res['documents']:
        target_hash = student_res['documents'][0]['doc_hash']
        print(f'[4/5] Testing tool: verify_credential ({target_hash[:16]}...)...')
        verif = tool_verify_credential(target_hash)
        assert verif['is_valid'] is True, f"Verification failed: {verif}"
        print(f"      [OK] Result: {verif['result']} | Title: {verif.get('title')}")

    # Test 5: read_resource
    print('[5/5] Testing resource: satyameva://stats/telemetry...')
    stats_json = read_resource('satyameva://stats/telemetry')
    stats = json.loads(stats_json)
    assert 'total_credentials_anchored' in stats, f"Stats error: {stats}"
    print(f"      [OK] Anchored Docs: {stats['total_credentials_anchored']} | Verified Blocks: {stats['blockchain_height']}")

    print('====================================================')
    print('  ALL MCP TOOLS & RESOURCES PASSED SELF-DIAGNOSTIC! ')
    print('====================================================\n')


def main():
    if '--test' in sys.argv:
        run_self_test()
        return

    logger.info('Starting Satyameva Aegis MCP Server (stdio transport)...')

    # Read line-by-line JSON-RPC messages from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_rpc_request(req)
            if res is not None:
                sys.stdout.write(json.dumps(res) + '\n')
                sys.stdout.flush()
        except json.JSONDecodeError:
            err = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {'code': -32700, 'message': 'Parse error: Invalid JSON'},
            }
            sys.stdout.write(json.dumps(err) + '\n')
            sys.stdout.flush()
        except Exception as exc:
            logger.error('Unhandled server exception: %s', exc, exc_info=True)


if __name__ == '__main__':
    main()
