from flask import Flask
from flask import render_template
from flask import request
import requests

from os import urandom
from pygost.gost3410 import prv_unmarshal, public_key, pub_marshal
from pygost.utils import hexenc
from transaction import Transaction
from config import CANDIDATES_LIST, ELLIPTIC_CURVE, LIST_OF_NODES


app = Flask(__name__)


@app.route('/vote', methods=['GET'])
def voting():
    prv_raw = urandom(32)
    prv = prv_unmarshal(prv_raw)
    hex_prv_key = hexenc(prv_raw)
    publ_key = public_key(ELLIPTIC_CURVE, prv)
    hex_pbl_key = hexenc(pub_marshal(publ_key))
    return render_template('page.html', private_key=hex_prv_key,
                           public_key=hex_pbl_key)


@app.route('/final', methods=['GET'])
def final():
    return render_template('final.html')


@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')


@app.route('/vote', methods=['POST'])
def vote():
    data = request.form
    prv_key = data['private_key']
    publ_key = public_key(ELLIPTIC_CURVE, prv_key)
    candidate_public_key = CANDIDATES_LIST[data['vote']]
    t = Transaction(amount=1, sender=list(publ_key), reciever=candidate_public_key)
    t.sign()
    for node in LIST_OF_NODES:
        res = requests.post(f'http://{node}/transaction', json=t.to_json())
    return res, 200


@app.route('/keygen', methods=['POST'])
def generate_key():
    prv_raw = urandom(32)
    prv = prv_unmarshal(prv_raw)
    return prv, 200


@app.route('/', methods=['GET'])
def generation_page():
    return render_template('generate_key.html')

# @app.route('/voting', methods=['POST'])
# def func():
#     data = request.form
#     valid = main(data['user'])
#     if valid:
#         db[data['vote']] = db.get(data['vote'], 0) + 1
#         print(db[data['vote']])
#     return {'valid': valid}, 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int,
                        help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
