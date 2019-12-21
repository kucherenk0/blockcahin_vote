from config import ELLIPTIC_CURVE
from os import urandom
from pygost.utils import hexenc
from pygost.gost3410 import public_key, sign, prv_unmarshal, verify, \
    pub_unmarshal, verify, pub_marshal, hexdec
from transaction import Transaction


valid_transactions = []


with open('valid_transactions.txt', 'w') as fd:
    for i in range(10):
        prv_raw = urandom(32)
        prv = prv_unmarshal(prv_raw)
        pub = public_key(ELLIPTIC_CURVE, prv)
        t = Transaction(amount=1, sender=list(pub), reciever='1488')
        t.sign(prv)
        if t.verify_signature():
            fd.write(str(t.to_json()) + "\n")




