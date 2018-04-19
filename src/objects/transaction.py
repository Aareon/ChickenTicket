import json
import time

import ecdsa
from crypto.chicken import chicken_hash


class Transaction:
    def __init__(self, height, address, recipient, amount, openfield=''):
        self.height = height
        self.timestamp = int(time.time() * 10000000)
        self.address = address
        self.recipient = recipient
        self.amount = amount
        self.openfield = openfield
        self.proof = None
        self.signature = None

    def __repr__(self):
        return '<Transaction(height={}, timestamp={}, address={}, recipient={}, amount={}, openfield={}'.format(
            self.height, self.timestamp, self.address, self.recipient, self.amount, self.openfield
        )

    @property
    def json(self):
        transaction = {
            'height': self.height,
            'timestamp': self.timestamp,
            'address': self.address,
            'recipient': self.recipient,
            'amount': self.amount,
            'openfield': self.openfield
        }

        if self.proof is not None:
            transaction['proof'] = self.proof
        
        if self.signature is not None:
            transaction['signature'] = self.signature
        
        return json.dumps(transaction)

    def hash(self):
        self.proof = chicken_hash(str(self.json).encode('utf-8')).hexdigest()
        return self

    def sign(self, private_key):
        if self.proof is None:
            return
            
        # signing key, will be used to sign the transaction and generate a signature
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        self.signature = sk.sign(self.json.encode('utf-8'))
        return self
