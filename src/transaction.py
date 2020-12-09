import time

import ecdsa
from crypto.chicken import chicken_hash
from utils.time_tools import get_timestamp

try:
    import ujson as json
except ImportError:
    import json


def dust(amount):
    """Multiply an amount according to dust"""
    return amount*100000000


class Transaction:
    __slots__ = (
        "index",
        "timestamp",
        "sender",
        "recipient",
        "amount",
        "openfield",
        "proof",
        "signature",
    )

    def __init__(self, index, sender, recipient, amount, openfield=''):
        self.index = index
        self.timestamp = get_timestamp()
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.openfield = openfield
        self.proof = None
        self.signature = None

    def __repr__(self):
        return '<Transaction(index={}, timestamp={}, sender={}, recipient={}, amount={}, openfield={})>'.format(
            self.index, self.timestamp, self.sender, self.recipient, self.amount, self.openfield
        )

    @property
    def json(self):
        transaction = {
            "index": self.index,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "openfield": self.openfield,
            "proof": self.proof or "",
            "signature": self.signature or "",
        }
        
        return json.dumps(transaction, sort_keys=True)

    def hash(self):
        data = str(self.json).encode('utf-8')
        self.proof = chicken_hash(data).hexdigest()
        return self

    def sign(self, private_key):
        if self.proof is None:
            return

        # signing key, will be used to sign the transaction and generate a signature
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        self.signature = sk.sign(self.json.encode('utf-8')).hex()

        return self

    def create_genesis_transaction(self, timestamp, private_key):
        self.timestamp = timestamp
        self.hash()

        self.signature = '5a0f2ea2036c74bb866a524b5028868648eb85938609466032cd316a89da7bd7d7e2fec0d3973023f5cdf9604315b9c78bde57df08c95c9b61f816775ac85a06'

        return self.json
