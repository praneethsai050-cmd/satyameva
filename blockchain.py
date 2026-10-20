"""
A robust, database and JSON file backed blockchain with asymmetric cryptography
and multi-node P2P consensus.

The chain lives in the `block` table and synchronizes with `instance/blockchain.json`,
so it survives restarts and can be inspected or imported/exported easily.

Each block commits to its predecessor via `previous_hash`, so editing any
historical record breaks every hash downstream of it — which `validate_chain()` checks.
Each block and credential can also be signed by issuer/miner ECDSA keypairs.
"""
import hashlib
import json
import os
import urllib.request
from datetime import datetime
from urllib.parse import urlparse

from extensions import db, utcnow
from models.block import Block
from security import canonical_payload

GENESIS_PREVIOUS_HASH = '0' * 64
DEFAULT_CHAIN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'blockchain.json')


class Blockchain:
    """
    Core Blockchain implementation with Proof-of-Work, asymmetric ECDSA signatures,
    persistent storage (DB + JSON), and multi-node P2P consensus.
    """
    def __init__(self, storage_file: str = DEFAULT_CHAIN_FILE):
        self.storage_file = storage_file
        self.difficulty = 4
        self.nodes = set()

    @staticmethod
    def compute_block_hash(index: int, timestamp: str, data: str, proof: int, previous_hash: str) -> str:
        """SHA-256 over the block's immutable fields."""
        material = f'{index}|{timestamp}|{data}|{proof}|{previous_hash}'
        return hashlib.sha256(material.encode('utf-8')).hexdigest()

    def proof_of_work(self, previous_proof: int, index: int, difficulty: int | None = None) -> int:
        """
        PoW: search for a nonce whose digest has `difficulty` leading zeros.
        """
        diff = difficulty if difficulty is not None else self.difficulty
        target = '0' * diff
        proof = 1
        while True:
            guess = hashlib.sha256(f'{previous_proof}{proof}{index}'.encode('utf-8')).hexdigest()
            if guess.startswith(target):
                return proof
            proof += 1

    def get_last_block(self) -> Block | None:
        """Highest-index block in the database, or None on an empty chain."""
        try:
            return Block.query.order_by(Block.index.desc()).first()
        except Exception:
            return None

    def chain_length(self) -> int:
        try:
            return Block.query.count()
        except Exception:
            return 0

    def ensure_genesis_block(self) -> Block:
        """Create block #0 if the chain has not been started yet."""
        existing = Block.query.filter_by(index=0).first()
        if existing:
            return existing

        timestamp = utcnow()
        data = canonical_payload({'genesis': True, 'chain': 'satyameva'})
        block = Block(
            index=0,
            timestamp=timestamp,
            data=data,
            proof=1,
            previous_hash=GENESIS_PREVIOUS_HASH,
            doc_hash=None,
            signature=None,
            miner_public_key=None,
        )
        block.hash = self.compute_block_hash(0, timestamp.isoformat(), data, 1, GENESIS_PREVIOUS_HASH)
        db.session.add(block)
        db.session.commit()
        self.save_to_json()
        return block

    def mine_block(self, payload: dict, doc_hash: str | None = None, difficulty: int | None = None,
                   private_key: str | None = None, public_key: str | None = None) -> Block:
        """
        Append a new block committing to `payload` and optional `doc_hash`.
        Optionally signs the block with an ECDSA private key.
        Persists immediately to database and JSON storage file.
        """
        previous = self.get_last_block() or self.ensure_genesis_block()
        index = previous.index + 1
        timestamp = utcnow()
        data = canonical_payload(payload)
        diff = difficulty if difficulty is not None else self.difficulty
        proof = self.proof_of_work(previous.proof, index, diff)
        block_hash = self.compute_block_hash(index, timestamp.isoformat(), data, proof, previous.hash)

        sig = None
        pub = public_key
        if private_key:
            try:
                from services.crypto_service import sign_hash
                sig = sign_hash(private_key, block_hash)
            except Exception:
                sig = None

        block = Block(
            index=index,
            timestamp=timestamp,
            data=data,
            proof=proof,
            previous_hash=previous.hash,
            doc_hash=doc_hash,
            signature=sig,
            miner_public_key=pub,
        )
        block.hash = block_hash
        db.session.add(block)
        db.session.commit()

        self.save_to_json()
        return block

    def get_block_for_doc(self, doc_hash: str) -> Block | None:
        """Find the block that anchored a given document hash."""
        if not doc_hash:
            return None
        return Block.query.filter_by(doc_hash=doc_hash).order_by(Block.index.desc()).first()

    def validate_chain(self) -> tuple[bool, str]:
        """
        Walk the chain and confirm block integrity, unbroken cryptographic links,
        and digital signatures.
        Returns (ok: bool, message: str).
        """
        try:
            blocks = Block.query.order_by(Block.index.asc()).all()
        except Exception as e:
            return False, f'Database error reading blockchain: {e}'

        if not blocks:
            # Try to restore from JSON file if available
            if os.path.exists(self.storage_file):
                self.load_from_json()
                blocks = Block.query.order_by(Block.index.asc()).all()

        if not blocks:
            return False, 'Chain is empty — genesis block missing.'

        for position, block in enumerate(blocks):
            expected = self.compute_block_hash(
                block.index, block.timestamp.isoformat(),
                block.data, block.proof, block.previous_hash,
            )
            if expected != block.hash:
                return False, f'Block #{block.index} hash mismatch — data was altered.'

            if position == 0:
                if block.previous_hash != GENESIS_PREVIOUS_HASH:
                    return False, 'Genesis block has an unexpected parent.'
            else:
                previous = blocks[position - 1]
                if block.previous_hash != previous.hash:
                    return False, f'Block #{block.index} does not link to block #{previous.index}.'
                if block.index != previous.index + 1:
                    return False, f'Chain has a gap before block #{block.index}.'

            # Cryptographic signature check if present
            if getattr(block, 'signature', None) and getattr(block, 'miner_public_key', None):
                from services.crypto_service import verify_signature
                if not verify_signature(block.miner_public_key, block.hash, block.signature):
                    return False, f'Block #{block.index} cryptographic signature verification failed.'

        return True, f'Chain intact — {len(blocks)} blocks verified.'

    def get_chain_data(self) -> list[dict]:
        """Return full chain as serializable list of dictionaries."""
        blocks = Block.query.order_by(Block.index.asc()).all()
        chain_data = []
        for b in blocks:
            chain_data.append({
                'index': b.index,
                'timestamp': b.timestamp.isoformat(),
                'data': b.data,
                'proof': b.proof,
                'previous_hash': b.previous_hash,
                'hash': b.hash,
                'doc_hash': b.doc_hash,
                'signature': getattr(b, 'signature', None),
                'miner_public_key': getattr(b, 'miner_public_key', None),
            })
        return chain_data

    def save_to_json(self, filepath: str | None = None) -> bool:
        """Save the current blockchain state to a JSON file."""
        target_path = filepath or self.storage_file
        try:
            os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
            chain_data = self.get_chain_data()
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(chain_data, f, indent=2)
            return True
        except Exception as e:
            print(f'Error saving blockchain to JSON: {e}')
            return False

    def load_from_json(self, filepath: str | None = None) -> list[dict]:
        """Load blockchain data from JSON file and populate database if missing."""
        target_path = filepath or self.storage_file
        if not os.path.exists(target_path):
            return []
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                chain_data = json.load(f)

            for item in chain_data:
                existing = Block.query.filter_by(index=item['index']).first()
                if not existing:
                    ts = datetime.fromisoformat(item['timestamp'])
                    b = Block(
                        index=item['index'],
                        timestamp=ts,
                        data=item['data'],
                        proof=item['proof'],
                        previous_hash=item['previous_hash'],
                        hash=item['hash'],
                        doc_hash=item.get('doc_hash'),
                        signature=item.get('signature'),
                        miner_public_key=item.get('miner_public_key'),
                    )
                    db.session.add(b)
            db.session.commit()
            return chain_data
        except Exception as e:
            print(f'Error loading blockchain from JSON: {e}')
            return []

    # ─── Multi-Node P2P Consensus ───────────────────────────────────────────────
    def register_node(self, address: str) -> bool:
        """
        Add a new peer node network address, e.g. 'http://192.168.0.5:5000'
        or '127.0.0.1:5001'.
        """
        if not address:
            return False
        parsed = urlparse(address if '://' in address else f'http://{address}')
        if parsed.netloc:
            node_url = f'{parsed.scheme}://{parsed.netloc}'
            self.nodes.add(node_url)
            return True
        return False

    def is_valid_chain(self, chain_data: list[dict]) -> bool:
        """Validate an entire candidate chain dictionary sequence."""
        if not chain_data:
            return False

        for i, b in enumerate(chain_data):
            if i == 0:
                if b.get('previous_hash') != GENESIS_PREVIOUS_HASH:
                    return False
                continue

            prev = chain_data[i - 1]
            if b.get('previous_hash') != prev.get('hash'):
                return False
            if b.get('index') != prev.get('index') + 1:
                return False

            # Verify computed hash
            ts_str = b.get('timestamp')
            computed = self.compute_block_hash(
                b['index'], ts_str, b['data'], b['proof'], b['previous_hash']
            )
            if computed != b.get('hash'):
                return False

            # Verify signature if present
            sig = b.get('signature')
            pub = b.get('miner_public_key')
            if sig and pub:
                from services.crypto_service import verify_signature
                if not verify_signature(pub, b['hash'], sig):
                    return False

        return True

    def resolve_conflicts(self) -> tuple[bool, str, int]:
        """
        Longest Valid Chain rule for P2P consensus.
        Queries all registered peer nodes; replaces local chain if a longer valid chain is found.
        Returns (replaced, message, current_length).
        """
        longest_chain = None
        current_len = self.chain_length()
        max_len = current_len

        for node in list(self.nodes):
            try:
                url = f"{node.rstrip('/')}/blockchain/chain"
                req = urllib.request.Request(url, headers={'User-Agent': 'Satyameva-Consensus/1.0'})
                with urllib.request.urlopen(req, timeout=4) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        chain = data.get('chain', [])
                        length = data.get('length', len(chain))
                        if length > max_len and self.is_valid_chain(chain):
                            max_len = length
                            longest_chain = chain
            except Exception:
                continue

        if longest_chain:
            try:
                Block.query.delete()
                for item in longest_chain:
                    ts = datetime.fromisoformat(item['timestamp'])
                    b = Block(
                        index=item['index'],
                        timestamp=ts,
                        data=item['data'],
                        proof=item['proof'],
                        previous_hash=item['previous_hash'],
                        hash=item['hash'],
                        doc_hash=item.get('doc_hash'),
                        signature=item.get('signature'),
                        miner_public_key=item.get('miner_public_key'),
                    )
                    db.session.add(b)
                db.session.commit()
                self.save_to_json()
                return True, f"Chain replaced with longer valid chain from peer ({max_len} blocks).", max_len
            except Exception as e:
                db.session.rollback()
                return False, f"Failed to persist resolved chain: {e}", current_len

        return False, f"Our chain is authoritative ({current_len} blocks).", current_len


# Global singleton instance
blockchain_instance = Blockchain()

# Module-level helper functions for backwards and cross-compatibility
compute_block_hash = blockchain_instance.compute_block_hash
proof_of_work = blockchain_instance.proof_of_work
get_last_block = blockchain_instance.get_last_block
chain_length = blockchain_instance.chain_length
ensure_genesis_block = blockchain_instance.ensure_genesis_block
mine_block = blockchain_instance.mine_block
get_block_for_doc = blockchain_instance.get_block_for_doc
validate_chain = blockchain_instance.validate_chain
save_to_json = blockchain_instance.save_to_json
load_from_json = blockchain_instance.load_from_json
register_node = blockchain_instance.register_node
resolve_conflicts = blockchain_instance.resolve_conflicts
is_valid_chain = blockchain_instance.is_valid_chain
get_chain_data = blockchain_instance.get_chain_data
