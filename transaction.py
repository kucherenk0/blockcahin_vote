
from blockchain import BlockId

class Transaction:
    def __init__(self,
                 sender: str,
                 reciever: str,
                 input: BlockID,
                 amount: int):
        self.sender = sender
        self.reciever = reciever
        self.input = input
        self.amount = amount
        
    def sign(self, key: str):
        '''
        Добавить электронную подпись
        '''
        pass
    
    def validate_signature(self):
        '''
        Добавить проверку корректности транзакции
        с помощью лектронной подписи
        '''        
        pass
    