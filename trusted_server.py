import requests
import json

from flask import Flask, request, abort, jsonify
from config import CANDIDATES_LIST, TRUSTED_USER, AMOUNT_FOR_SERVER,\
    NODES, KEY_WORDS
from transaction import Transaction

server = Flask(__name__)

@server.route('/', methods=['GET'])
@server.route('/candidates', methods=['GET'])
def candidates():
    return jsonify({'candidates': CANDIDATES_LIST}), 200

@server.route('/nodes', methods=['GET'])
def nodes():
    return jsonify({'nodes': NODES}), 200

@server.route('/count', methods=['GET'])
def count_votes():
    pass

@server.route('/register', methods=['POST'])
def register_voter():
    data = request.get_json() or {}
    if not data:
        abort(400, 'No data!')
    key_word = data['key_word']
    public_key = data['public_key']
    kw_status = KEY_WORDS.get(key_word, 0)
    if not kw_status:
        abort(404, f'No such key-word: {key_word}')
    
    KEY_WORDS[key_word] = kw_status - 1
    for node in NODES:
        t = Transaction(sender=TRUSTED_USER, reciever=public_key, amount=1)
        status = requests.post('http://' + node + '/transaction', json=t.to_json())
        print(f'{node}: {status}')
    return jsonify({'status': 'approved'}), 200
    

if __name__ == '__main__':
    t = Transaction(TRUSTED_USER, TRUSTED_USER, AMOUNT_FOR_SERVER)
    print(t)
    for node in NODES:
        status = requests.post('http://' + node + '/transaction', json=t.to_json())
        print(f'{node}: {status}')
    server.run(host='0.0.0.0', port=8000, threaded=True)