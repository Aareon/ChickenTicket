import time
import json
from crypto.chicken import chicken_hash
from utils.merkles import Merkle
from transaction import Transaction, dust
from wallet import generate_ECDSA_keys

VERSION = 1


class BlockException(Exception):
    pass


class Block:
    def __init__(self, last_block=None, transactions=[], proof=None, nonce=None):
        self.last_block = last_block

        # primarily for handling genesis block creation
        if last_block is not None:
            self.index = last_block.index + 1
            self.previous_proof = last_block.proof
        else:
            self.index = 0
            self.previous_proof = '0'

        self.transactions = transactions
        self.timestamp = int(time.time() * 100000)
        self.proof = proof

        if last_block is not None:
            self.difficulty = self.calculate_difficulty()
        else:
            self.difficulty = 20

        self.merkle_tree = Merkle(chicken_hash)
        self.merkle_root = None
        self.nonce = 0


    def __repr__(self):
        return '<Block(index={}, timestamp={}, previous_proof={}, proof={}, difficulty={}, transactions={}'.format(
               self.index, self.timestamp, self.previous_proof, self.proof, self.difficulty, self.transactions
        )


    def is_ready(self):
        if self.nonce is None:
            return False, 'nonce'

        return True, None


    @property
    def json(self):
        is_ready, missing = self.is_ready()
        if not is_ready:
            raise BlockException('Block is not ready. Missing {}'.format(missing))

        block = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_proof': self.previous_proof,
            'difficulty': self.difficulty,
            'proof': self.proof,
            'merkle_root': self.get_merkle_root(),
            'header': self.header,
            'nonce': self.nonce
        }
        
        return json.dumps(block, sort_keys=True)


    def get_merkle_root(self):
        for tx in self.transactions:
            data = tx.encode('utf-8')
            tx_hash = chicken_hash(data).hexdigest()
            self.merkle_tree.add_leaf(tx_hash)

        if not self.merkle_tree.is_ready:
            self.merkle_tree.make_tree()
        self.merkle_root = self.merkle_tree.get_merkle_root()
        return self.merkle_root


    @property
    def header(self):
        if self.merkle_root is not None:
            return '{}{}{}{}'.format(self.previous_proof, self.merkle_root, self.timestamp, self.nonce)
        else:
            raise AttributeError('Must get merkle root before getting header')

    
    def calculate_difficulty(self):
        # the factor to move difficulty, how much it should be moved at one time
        offset = self.last_block.difficulty // 2048

        # difference between block timestamps
        # turn the time_diff into an integer, we only care about a difference of 10 seconds
        time_diff = (self.timestamp - self.last_block.timestamp) // 100000

        # get exponent to move difficulty (i.e. up or down)
        sign = 1 if time_diff < 10 else -1
        
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
        data = str(self.json).encode('utf-8')
        self.proof = chicken_hash(data).hexdigest()
        return self
        

    def add_transactions(self, *transactions):
        for tx in transactions:
            self.transactions.append(tx.json)
        return self


    def create_genesis_block(self):
        self.timestamp = 152519919871659
        self.previous_proof = '0'
        self.difficulty = 1
        self.nonce = 0

        _, private_key = generate_ECDSA_keys()

        tx = Transaction(0, 'genesis', '0x34cf5eeb59c58e5f017a63dbb87VPJ', dust(1), openfield='genesis')
        tx.create_genesis_transaction(self.timestamp, private_key)
        tx.hash()

        self.add_transactions(tx)
        self.hash()
        return self


class Blockchain:
    chain = [Block().create_genesis_block()]

    def __repr__(self):
        return '<Blockchain(chain={})>'.format(self.chain)

if __name__ == '__main__':
    from pprint import pprint
    blockchain = Blockchain()
    for block in blockchain.chain:
        data = json.loads(block.json)
        pprint(data)