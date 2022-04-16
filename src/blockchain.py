import time
import json
from crypto.chicken import chicken_hash
from utils.merkles import Merkle
from utils.time_tools import get_timestamp
from transaction import Transaction, dust
from wallet import generate_ECDSA_keys


class Blockchain:
    chain = [create_genesis_block()]
    
    def add_block(self, block):
        self.chain.append(block)

    def __repr__(self):
        return f"<Blockchain(chain={self.chain})>"

if __name__ == '__main__':
    from pprint import pprint
    blockchain = Blockchain()
    for block in blockchain.chain:
        data = json.loads(block.json)
        pprint(data)
