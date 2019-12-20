import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from typing import NewType, List, Optional
from transaction import Transaction

import requests
from flask import Flask, jsonify, request

TARGET = 0x00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
DEFAULT_PROOF = 100
DEFAULT_TRANSACTION = Transaction('genesys', 'genesys', 0)
FAIL = -1
SUCCESS = 0


class Block:
    def __init__(self,
                 index: int,
                 transaction: Transaction,
                 proof: int,
                 prev_hash: str):
        self.index = index
        self.transaction = transaction
        self.timestamp = time()
        self.proof = proof
        self.prev_hash = prev_hash
        self.hash = self.hash(self)
        
    def __str__(self):
        return str(self.dict())
        
    def dict(self):
        block = {'index': self.index,
                 'transaction': self.transaction.dict(),
                 'timestamp': self.timestamp,
                 'proof': self.proof,
                 'prev_hash': self.prev_hash}
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
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block.dict(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()



class Blockchain:
    def __init__(self):
        self.transactions_pull = []
        self.chain = []
        self.target = TARGET
        # Genesis block
        self.chain.append(Block(index=0,
                                transaction=DEFAULT_TRANSACTION,
                                proof=DEFAULT_PROOF,
                                prev_hash=1))
        self.dump()

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
            self.chain.append(block)
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
        self.transactions_pull.append(transaction)
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
                self.chain.append(block)
            self.dump()
            return self.chain[block_ind+1:]
        else:
            return []
    
    # DONE
    def validate_transaction(self, transaction: Transaction,
                             chain: Optional[List[Block]] = None):
        chain = chain if chain else self.chain
        sender = transaction.sender
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
        Creates a new block and mines it. Then it adds it ti the chain
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
        while block.hash > self.target:
            block.proof += 1
        return block
        

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


