import requests
import json

from flask import Flask, request, abort, jsonify
from config import CANDIDATES_LIST, TRUSTED_USER, AMOUNT_FOR_SERVER, NODES
from transaction import Transaction

server = Flask(__name__)

@server.route('/', methods=['GET'])
@server.route('/candidates', methods=['GET'])
def candidates():
    pass

@server.route('/nodes', methods=['GET'])
def nodes():
    pass

@server.route('/count', methods=['GET'])
def count_votes():
    pass


if __name__ == '__main__':
    t = Transaction(TRUSTED_USER, TRUSTED_USER, AMOUNT_FOR_SERVER)
    print(t)
    for node in NODES:
        status = requests.post('http://' + node + '/transaction', json=t.to_json())
        print(f'{node}: {status}')
    server.run(host='0.0.0.0', port=8000, threaded=True)