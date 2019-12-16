import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from typing import NewType, List, Optional

import requests
from flask import Flask, jsonify, request

BlockId = NewType('BlockId', int)


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
        # Genesis block
        self.chain.append(Block(index=0,
                                transaction=None,
                                proof=100,
                                prev_hash=1))

    def add_block(self, block: Block):
        """
        Adds an already proofed Block to the chain
        """
        self.chain.append(block)
        return block.index
    
    #TODO
    def valid_chain(self, chain: Optional[List[Block]] = None):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'],
                                    last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

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


