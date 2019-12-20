from blockchain import BlockId
from config import ELEPTIC_CURVE
from pygost import gost34112012256
from pygost.gost3410 import verify, pub_unmarshal

import json


class Transaction:
    def __init__(self,
                 sender: str,
                 reciever: str,
                 amount: int,
                 signature: str = None):
        signature = signature if signature else 'unsigned'
        self._signature = signature
        self.sender = sender
        self.reciever = reciever
        self.amount = amount

    def __eq__(self, other: Transaction):
        if not isinstance(other, Transaction):
            return False
        return (self._signature == other._signature and
                self.sender == other.sender and
                self.reciever == other.reciever and
                self.amount == other.amount)

    def __str__(self):
        return str(self.dict())
    
    def sign(self, prv_key: str):
        '''
        Добавить электронную подпись
        '''
        # self._signature
        pass

    def verify_signature(self):
        '''
        Добавить проверку корректности транзакции
        с помощью лектронной подписи
        '''
        pub_key = pub_unmarshal(self.sender.encode())
        data_for_signing = json.dump(self.dict(), sort_keys=True)
        dgst = gost34112012256.new(data_for_signing).digest()
        encoded_sign = self.signature.encode()

        return verify(ELEPTIC_CURVE, pub_key, dgst, encoded_sign, mode=2012)

    def dict(self):
        transaction = {'sender': self.sender,
                       'reciever': self.reciever,
                       'amount': self.amount,
                       'signature': self._signature}
        return transaction
