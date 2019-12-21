from flask import Flask
from flask import render_template
from flask import request
import requests

from os import urandom
from pygost.gost3410 import prv_unmarshal, public_key, pub_marshal
from pygost.utils import hexenc, hexdec
from transaction import Transaction
from config import CANDIDATES_LIST, ELLIPTIC_CURVE, NODES, TRUSTED_URL


app = Flask(__name__)


@app.route('/vote', methods=['GET'])
def voting():
    keyword = request.args.get('keyword', default='', type=str)
    prv_raw = urandom(32)
    prv = prv_unmarshal(prv_raw)
    hex_prv_key = hexenc(prv_raw)
    publ_key = public_key(ELLIPTIC_CURVE, prv)
    hex_pbl_key = hexenc(pub_marshal(publ_key))

    data = {'key_word': keyword,
            'public_key': Transaction.list_to_string(publ_key)}
    try:
        res = requests.post(f'http://{TRUSTED_URL}/register', json=data)
        if res.status_code == 200:
            return render_template('page.html', private_key=hex_prv_key,
                                 public_key=hex_pbl_key,
                                 n=len(CANDIDATES_LIST),
                                 candidates = CANDIDATES_LIST)
        elif res.status_code == 404:
            return render_template('generate_key.html', keyword=False)

    except ConnectionError:
        return render_template('error.html')


@app.route('/final', methods=['GET'])
def final():
    return render_template('final.html')


@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')


@app.route('/vote', methods=['POST'])
def vote():
    data = request.form
    print(data)
    prv_key = data['private_key']
    publ_key = public_key(ELLIPTIC_CURVE, prv_unmarshal(hexdec(prv_key)))
    candidate_public_key = CANDIDATES_LIST[int(data['vote'])]
    t = Transaction(amount=1, sender=list(publ_key), reciever=candidate_public_key)
    t.sign(prv_unmarshal(hexdec(prv_key)))

    for node in NODES:
        requests.post(f'http://{node}/transaction', json=t.to_json())
    return "OK", 200


@app.route('/', methods=['GET'])
def generation_page():
    return render_template('generate_key.html', keyword=True)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int,
                        help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
