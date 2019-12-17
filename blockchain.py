import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from typing import NewType, List, Optional
from transaction import Transaction

import requests
from flask import Flask, jsonify, request

BlockId = NewType('BlockId', int)
Target = 10e8


class Block:
    def __init__(self,
                 index: int,
                 transaction: Transaction,
                 proof: int,
                 prev_hash: str):
        self.index = index
        self.transaction = transaction
        self.proof = proof
        self.prev_hash = prev_hash
        self.hash = self.hash(self)
        
    def dict(self):
        block = {'index': self.index,
                 'transaction': self.transaction.dict(),
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
        self.target = Target
        # Genesis block
        self.chain.append(Block(index=0,
                                transaction=None,
                                proof=100,
                                prev_hash=1))

    def add_block(self, block: Block):
        """
        Adds an already proofed Block to the chain
        """
        if block.index == self.last_ind + 1 and \
            block.prev_hash == self.last_block.hash:
            self.chain.append(block)
            return block.index
        else:
            return None

    def valid_chain(self, chain: Optional[List[Block]] = self.chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """
        # Check if blocks themselves are correct
        validity = True
        for block in chain:
            validity = validity and block.validate()
            validity = validity and block.transaction.validate_signature()
            validity = validity and self.validate_transaction(chain)
        
        # Check hash sequences
        length = len(chain)
        for i in range(length - 1):
            validity = validity and (chain[i+1].prev_hash == chain[i].hash)
        return validity

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
            return self.chain[block_ind+1:]
        else:
            return []


    def validate_transaction(self, transaction: Transaction):
        pass

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.transactions_pull.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]
    
    @property
    def last_ind(self):
        assert self.last_block.index == len(self.chain) - 1
        return self.last_block.index
    
    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
         
        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

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


