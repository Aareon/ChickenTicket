import time
import json
from crypto.chicken import chicken_hash
from decimal import Decimal, getcontext
from utils.merkles import Merkle

getcontext().prec = 4

VERSION = 1

class Block:
    def __init__(self, last_block=None, transactions=None, proof=None):
        self.last_block = last_block

        # primarily for handling genesis block creation
        if last_block is not None:
            self.index = last_block.height + 1
            self.previous_proof = last_block.proof
        else:
            self.index = 0
            self.previous_proof = '0'

        self.transactions = transactions
        self.timestamp = Decimal(time.time() * 10000000)
        self.proof = proof

        if last_block is not None:
            self.difficulty = self.calculate_difficulty()
        else:
            self.difficulty = 20

        self.merkle_tree = Merkle(chicken_hash)


    def __repr__(self):
        return '<Transaction(index={}, timestamp={}, previous_proof={}, proof={}, difficulty={}, transactions={}'.format(
               self.index, self.timestamp, self.previous_proof, self.proof, self.difficulty, self.transactions
        )


    @property
    def json(self):
        block = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_proof': self.previous_proof,
            'difficulty': self.calculate_difficulty() if self.last_block is not None else 1,
            'merkle_root': self.merkle_root
        }

        if self.proof is not None:
            block['proof'] = self.proof
        
        return json.dumps(block)


    @property
    def merkle_root(self):
        if not self.merkle_tree.is_ready:
            self.merkle_tree.make_tree()
        return self.merkle_tree.get_merkle_root()

    @property
    def header(self):
        return '{}{}{}{}'
    
    def calculate_difficulty(self):
        # the factor to move difficulty, how much it should be moved at one time
        offset = self.last_block.difficulty // 2048

        # difference between block timestamps
        # turn the time_diff into an integer, we only care about a difference of 10 seconds
        time_diff = (self.timestamp - self.last_block.timestamp) // 10000000

        # get exponent to move difficulty (i.e. up or down)
        if time_diff < 10:
            sign = 1
        else:
            sign = -1
        
        # calculation for bomb
        # bomb is the amount to add to diff every n blocks
        # in this case, its every 150000th block
        period_count = (self.last_block.index + 1) // 101000
        period_count -= 2 # free periods, how many times the bomb can be ignored
        bomb = 2**(period_count)

        # calculation for target
        self.difficulty = (self.last_block.difficulty + offset * sign) + bomb
        return self


    def hash(self):
        data = str(self.json).encode('ascii')
        self.proof = chicken_hash(data).hexdigest()
        return self
        

    def create_genesis_block(self):
        pass
        


class Blockchain:
    chain = [Block().create_genesis_block()]
