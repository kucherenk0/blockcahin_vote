from config import ELLIPTIC_CURVE
from pygost import gost34112012256
from pygost.gost3410 import verify, pub_unmarshal, sign, hexdec
from pygost.utils import hexenc
from typing import List

import json


class Transaction:
    def __init__(self,
                 sender: List[int],
                 reciever: str,
                 amount: int,
                 signature: str = None):
        signature = signature if signature else 'unsigned'
        self._signature = signature
        self.sender = self._list_to_string(sender)
        self._sender = tuple([int(i) for i in sender])
        self.reciever = reciever
        self.amount = int(amount)

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return (self._signature == other._signature and
                self.sender == other.sender and
                self.reciever == other.reciever and
                self.amount == other.amount)

    def __str__(self):
        return str(self.dict())

    def sign(self, prv_key: int):
        '''
        Создается электронная подпись, в данных для подписи учитываются только
        sender, reciever и amount
        '''
        data = self.bytes_public_data()
        hashed_data = gost34112012256.new(data).digest()
        signature = sign(ELLIPTIC_CURVE, prv_key, hashed_data, mode=2012)
        self._signature = hexenc(signature)

    def verify_signature(self):
        '''
        Добавить проверку корректности транзакции
        с помощью лектронной подписи
        '''

        pub_key = self._sender
        data = self.bytes_public_data()
        hashed_data = gost34112012256.new(data).digest()
        decoded_sign = hexdec(self._signature)
        return verify(ELLIPTIC_CURVE, pub_key, hashed_data, decoded_sign,
                      mode=2012)

    def bytes_public_data(self):
        return json.dumps({'sender': self.sender,
                           'reciever': self.reciever,
                           'amount': self.amount}, sort_keys=True).encode()

    def _list_to_string(self, lst: list):
        return (str(lst[0]) + str(lst[1]))[-10:]

    def to_json(self):
        result = {'sender': self._sender,
                  'reciever': self.reciever,
                  'amount': self.amount,
                  'signature': self._signature
                  }



    def dict(self):
        transaction = {'sender': self.sender,
                       'reciever': self.reciever,
                       'amount': self.amount,
                       'signature': self._signature}
        return transaction
