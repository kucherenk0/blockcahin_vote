from flask import Flask, request, jsonify, abort
from blockchain import Blockchain, Block
from transaction import Transaction
from config import FAIL, SUCCESS


node = Flask(__name__)

@node.route('/', methods=['GET'])
@node.route('/blockchain', methods=['GET'])
def get_chain():
    if blockchain:
        return str(blockchain), 200
    else:
        abort(500)
        
@node.route('/transaction', methods=['POST'])
def post_transaction():
    print('HERE!!!')
    data = request.get_json() or {}
    print(data)
    if not data:
        abort(400)
    transaction = Transaction(**data)
    try:
        result = blockchain.add_transaction(transaction)
    except:
        abort(400, f'Incorrect transaction!: {transaction}')
    if result == FAIL:
        abort(400, f'Incorrect transaction: {transaction}')
    else:
        blockchain.new_block()
        return 200
    
@node.route('/block', methods=['POST'])
def post_block():
    data = request.get_data() or {}
    if not data:
        abort(400)
    else:
        try:
            chain = Block.from_json_data(data)
        except:
            abort(400, f'Invalid blocks: {data}')
        else:
            blockchain.resolve_conflicts(chain)
        
    
   
   
if __name__ == '__main__':
    blockchain = Blockchain()
    node.run(host='0.0.0.0', port=5000, threaded=True)