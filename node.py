import threading
import hashlib
import json
import requests

from time import time
from typing import List, Optional
from transaction import Transaction
from config import TARGET, DEFAULT_PROOF, FAIL, \
    SUCCESS, DEFAULT_HASH, TRUSTED_USER, TRUSTED_URL

from flask import Flask, request, jsonify, abort


blockhain_lock = threading.Lock()
transactions_pull_lock = threading.Lock()   
node = Flask(__name__)


'''
Enter Blochain and Block classes here for the purposes of threading
'''

DEFAULT_TRANSACTION = Transaction([10, 10], 'genesys', 0)


class Block:
    def __init__(self,
                 index: int,
                 transaction: Transaction,
                 proof: int,
                 prev_hash: str,
                 hash: Optional[str] = None):
        self.index = index
        self.transaction = transaction
        self.timestamp = time()
        self.proof = proof
        self.prev_hash = prev_hash
        self.hash = hash if hash else self.hash(self)
        
    def __str__(self):
        return str(self.dict())
    
    def compare_to(self, other):
        return (self.index == other.index and
                self.prev_hash == other.prev_hash)
        
    def dict(self):
        block = {'index': self.index,
                 'transaction': self.transaction.dict(),
                 'proof': self.proof,
                 'timestamp': self.timestamp,
                 'prev_hash': self.prev_hash,
                 'hash': self.hash}
        return block
    
    def validate(self):
        return self.hash(self) == self.hash
    
    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        :return: str hash of the block
        """
        dct = {'index': block.index,
               'transaction': block.transaction.dict(),
               'proof': block.proof,
               'prev_hash': block.prev_hash}
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(dct, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def from_json_dict(chain):
        chain_ = []
        for block in chain:
            block_ = Block(index=int(block['index']),
                           transaction=Transaction(**block['transaction']),
                           proof=int(block['proof']),
                           prev_hash=block['prev_hash'],
                           hash=block['hash'])
            chain_.append(block_)
        return chain_
    
    @staticmethod
    def to_json_dict(chain):
        chain_ = []
        for block in chain:
            block_ = {'index': self.index,
                      'transaction': self.transaction,
                      'proof': self.proof,
                      'prev_hash': self.prev_hash,
                      'hash': self.hash}
            chain_.append(block_)
        return {'chain': chain_}



class Blockchain:
    def __init__(self):
        self.transactions_pull = []
        self.chain = []
        self.target = TARGET
        # Genesis block
        self.chain.append(Block(index=0,
                                transaction=DEFAULT_TRANSACTION,
                                proof=DEFAULT_PROOF,
                                prev_hash=1,
                                hash=DEFAULT_HASH))
        self.dump()

    # DONE
    def __str__(self):
        output = {'transactions_pull': [str(i) for i in 
                                        self.transactions_pull],
                  'chain': [str(i) for i in self.chain],
                  'traget': self.target}
        return str(output)
        
    # DONE
    def dump(self):
        with open('blockchain_dump.txt', 'w') as fd:
            fd.write(str(self))
        
    # DONE
    def add_block(self, block: Block):
        """
        Adds an already proofed Block to the chain
        """
        if block.index == self.last_ind + 1 and \
            block.prev_hash == self.last_block.hash:
            
            blockhain_lock.acquire()
            self.chain.append(block)
            blockhain_lock.release()
            
            self.dump()
            
            return block.index
        else:
            return None

    # DONE
    def add_transaction(self, transaction: Transaction):
        if not (transaction.verify_signature() and 
                self.validate_transaction(transaction) and
                transaction not in self.transactions_pull):
            return FAIL
        
        transactions_pull_lock.acquire()
        self.transactions_pull.append(transaction)
        transactions_pull_lock.release()
        
        self.dump()
        return SUCCESS
    
    # DONE
    def valid_chain(self, chain: Optional[List[Block]] = None):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """
        chain = chain if chain else self.chain
        # Check if blocks themselves are correct
        validity = True
        for block in chain:
            validity = validity and block.validate()
            validity = validity and block.transaction.validate_signature()
            validity = validity and (self.validate_transaction(block.transaction, chain) or
                                     self.validate_transaction(block.transaction))
        
        # Check hash sequences
        length = len(chain)
        for i in range(length - 1):
            validity = validity and (chain[i+1].prev_hash == chain[i].hash)
        return validity

    # DONE
    def resolve_conflicts(self, blocks: List[Block]):
        """
        :return: List[int], the indexes of removed blocks.
            If it is empty, then no blocks were removed
        """
        if not self.valid_chain(blocks):
            return []
        ind = self.last_ind
        if blocks[-1].index <= ind:
            return []
        block_ind = blocks[0].index
        if self.chain[block_ind].compare_to(blocks[0]):
            for i in range(self.last_ind, block_ind, -1):
                self.transactions_pull.append(self.chain[i].transaction)
                del self.chain[i]
            for i, block in enumerate(blocks):
                if i == 0:
                    continue
                
                blockhain_lock.acquire()
                self.chain.append(block)
                blockhain_lock.release()
            
            self.dump()
            return self.chain[block_ind+1:]
        else:
            return []
    
    # DONE
    def validate_transaction(self, transaction: Transaction,
                             chain: Optional[List[Block]] = None):
        chain = chain if chain else self.chain
        sender = transaction.sender
        if sender == TRUSTED_USER[1]:
            return True
        transactions = [block.transaction for block in chain if
                        block.transaction.sender == sender or
                        block.transaction.reciever == sender]
        summ = 0
        for trans in transactions:
            if trans.sender == sender:
                summ -= trans.amount
            elif trans.reciever == sender:
                summ += trans.amount
        if summ - transaction.amount >= 0:
            return True
        else:
            return False

    # TODO: Update this shit for multiprocessing!
    def new_block(self):
        '''
        Creates a new block and mines it. Then it adds it to the chain
        '''
        block = self.proof_of_work()
        if not self.add_block(block):
            raise ValueError(f'Something wrong with the block:\n {block}')
        return block.index
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    @property
    def last_ind(self):
        assert self.last_block.index == len(self.chain) - 1
        return self.last_block.index
    
    # TODO: Update for multiprocessing!
    def proof_of_work(self):
        transaction = self.transactions_pull[0]
        block = Block(self.last_ind+1, transaction,
                      DEFAULT_PROOF, self.last_block.hash)
        while int(block.hash, 16) > self.target:
            block.proof += 1
            block.hash = Block.hash(block)
        
        transactions_pull_lock.acquire()
        self.transactions_pull.pop(0)
        transactions_pull_lock.release()
        
        return block


'''
End of Blockchain and Block classes
'''



def mine(blockchain: Blockchain = None):
    if not blockchain:
        raise ValueError('No blockchain!!!!')
    nodes, status = requests.get('http://' + TRUSTED_URL + '/nodes')
    if status == 200:
        nodes = nodes['nodes']
    else:
        raise ValueError('No nodes from trusted server!!!')
    while True:
        if blockchain.transactions_pull:
            print(f'Started mining block {blockchain.last_ind+1}')
            index = blockchain.new_block()
            
            for node in nodes:
                requests.post('http://' + node + '/post_block', 
                              json.dumps(Block(blockchain.chain[-2:])))
            


@node.route('/', methods=['GET'])
@node.route('/blockchain', methods=['GET'])
def get_chain():
    if blockchain:
        return str(blockchain), 200
    else:
        abort(500)
        
@node.route('/transaction', methods=['POST'])
def post_transaction():
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
        return jsonify({'status': 'transaction added to the queue'}), 200
    
@node.route('/block', methods=['POST'])
def post_block():
    data = request.get_data() or {}
    if not data:
        abort(400, 'No data!')
    else:
        try:
            chain = Block.from_json_data(data)
        except:
            abort(400, f'Invalid blocks: {data}')
        else:
            blockchain.resolve_conflicts(chain)
        
    
   
   
if __name__ == '__main__':
    blockchain = Blockchain()
    thread_mine = threading.Thread(target=mine, args=(blockchain, ))
    thread_node = threading.Thread(target=node.run(host='0.0.0.0', port=5000, threaded=True))
    thread_node.start()
    thread_mine.start()
