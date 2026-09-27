"""
P2P Multi-Node Consensus and Blockchain Ledger Endpoints.

Provides:
  * GET  /blockchain/chain: Expose the node's full chain
  * POST /blockchain/nodes/register: Register peer nodes in the network
  * GET  /blockchain/nodes: List all active registered peer nodes
  * GET/POST /blockchain/resolve: Run longest valid chain consensus conflict resolution
"""
from flask import Blueprint, jsonify, request
from blockchain import blockchain_instance, get_chain_data, register_node, resolve_conflicts

blockchain_bp = Blueprint('blockchain_api', __name__, url_prefix='/blockchain')


@blockchain_bp.route('/chain', methods=['GET'])
def get_chain():
    """Return the node's current blockchain ledger."""
    chain = get_chain_data()
    return jsonify({
        'chain': chain,
        'length': len(chain),
        'status': 'ok',
    }), 200


@blockchain_bp.route('/nodes/register', methods=['POST'])
def register_nodes():
    """Register peer node addresses."""
    data = request.get_json(silent=True) or {}
    nodes = data.get('nodes')

    # Also support form-encoded input
    if not nodes:
        form_nodes = request.form.get('nodes', '')
        nodes = [n.strip() for n in form_nodes.replace(',', '\n').splitlines() if n.strip()]

    if not nodes or not isinstance(nodes, list):
        return jsonify({'error': 'Please provide a valid list of node addresses in "nodes".'}), 400

    registered = []
    for node in nodes:
        if register_node(node):
            registered.append(node)

    return jsonify({
        'message': f'Registered {len(registered)} new nodes.',
        'registered': registered,
        'total_nodes': list(blockchain_instance.nodes),
    }), 201


@blockchain_bp.route('/nodes', methods=['GET'])
def list_nodes():
    """List all registered peer nodes."""
    return jsonify({
        'nodes': list(blockchain_instance.nodes),
        'count': len(blockchain_instance.nodes),
    }), 200


@blockchain_bp.route('/resolve', methods=['GET', 'POST'])
def consensus_resolve():
    """Run consensus algorithm (longest valid chain rule)."""
    replaced, message, length = resolve_conflicts()
    return jsonify({
        'replaced': replaced,
        'message': message,
        'length': length,
    }), 200
