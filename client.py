from flask import Flask
from flask import render_template
from flask import request
from os import urandom
from pygost.gost3410 import prv_unmarshal
from config import CANDIDATES_LIST


app = Flask(__name__)


@app.route('/vote', methods=['GET'])
def voting():
    n = len(candidates_list)
    return render_template('generate_key.html', candidates=candidates_list, n=n)


@app.route('/final', methods=['GET'])
def final():
    return render_template('final.html')


@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')


@app.route('/voting', methods=['POST'])
def func1():
    data = request.form
    valid = "MOCK"
    return {'valid': valid}, 200


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
    parser.add_argument('-p', '--port', default=8080, type=int,
                        help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
