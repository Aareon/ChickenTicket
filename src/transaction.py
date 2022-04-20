import time
from dataclasses import dataclass
from decimal import Decimal
from typing import List

import ecdsa

from crypto.chicken import chicken_hash
from keys import CURVE, KeyPair

try:
    import ujson as json

    USING_UJSON = True
except ImportError:
    import json

    USING_UJSON = False


@dataclass
class TXVersion:
    ver1 = 0x1
    ver2 = 0x2
    ver3 = 0x3


@dataclass
class Input:
    tx_hash: str
    output_id: int

    def __str__(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def to_dict(self):
        return {"tx": self.tx_hash, "idx": self.output_id}


@dataclass
class Output:
    recipient: str  # address the amount is to be sent to
    amount: Decimal

    def __str__(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def to_dict(self):
        return {"recipient": self.recipient, "amount": str(self.amount)}


class Transaction:
    idx: int
    ver: TXVersion
    timestamp: int
    inputs: List[Input]  # tx_hash, output_id
    outputs: List[Output]  # recipient, amount
    fee: Decimal
    proof: bytes
    signature: bytes
    pubkey: bytes

    def __init__(self, **kwargs):
        self.idx = kwargs.get("idx")
        self.ver = kwargs.get("ver") or kwargs.get("version")
        self.timestamp = kwargs.get("timestamp") or time.time()
        self.inputs = kwargs.get("inputs") or []
        self.outputs = kwargs.get("outputs") or []
        self.fee = kwargs.get("fee")
        self.proof = kwargs.get("proof")
        self.signature = kwargs.get("signature")
        self.pubkey = kwargs.get("pubkey")

    def to_dict(self):
        data = {
            "idx": self.idx,
            "ver": self.ver,
            "time": self.timestamp,
            "in": [inp.to_dict() for inp in self.inputs],
            "out": [out.to_dict() for out in self.outputs],
            "fee": str(self.fee),
            "hash": self.proof,
            "sig": self.signature,
            "pub": str(self.pubkey),
        }
        return data

    def json(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def __repr__(self):
        return self.json()

    def hash(self):
        data = self.to_dict()
        del data["hash"]
        del data["sig"]
        del data["pub"]
        self.proof = chicken_hash(json.dumps(data, sort_keys=True).encode()).hex()
        return self.proof

    def add_input(self, input):
        if not hasattr(self, "inputs"):
            self.inputs = [input]
            return
        self.inputs.append(input)

    def add_output(self, output):
        if not hasattr(self, "outputs"):
            self.outputs = [output]
            return
        self.outputs.append(output)

    def sign(self, key: KeyPair):
        if not hasattr(self, "proof") or self.proof is None:
            self.hash()
        if isinstance(key, KeyPair):
            priv_key = key.priv
            self.pubkey = key.pub
        elif isinstance(key, [bytes, str]):
            priv_key = key
        else:
            raise TypeError(f"cannot sign transaction with key: {key}")
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(str(priv_key)), curve=CURVE)
        self.signature = sk.sign(bytes(str(self), encoding="utf-8")).hex()
        return self.signature


if __name__ == "__main__":
    # test creating a transaction
    tx = Transaction()
    tx.idx = 0
    tx.ver = TXVersion.ver1
    tx.timestamp = int(time.time())
    tx.fee = Decimal("1.0")

    # genesis input and output
    genesis = "genesis"
    ipt = Input(chicken_hash((genesis + "input").encode()).hex(), 0)
    tx.add_input(ipt)

    opt = Output("0x0", Decimal("1.0"))
    tx.add_output(opt)

    # test signing
    tx.hash()
    # tx.sign() will automatically hash the transaction if not already done so.
    # Calling it explicitly is the preferred behavior, though.
    keys = KeyPair.new()
    tx.sign(keys)
    # I'm attempting to make everything easily printable for not only
    # debugging purposes, but for message serialization purposes
    # as well
    print(tx)
