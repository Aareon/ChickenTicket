from dataclasses import dataclass
from decimal import Decimal
import time
from typing import List

import ecdsa

from crypto import hexdigest
from crypto.chicken import chicken_hash
from keys import KeyPair, CURVE


class TXVersion:
    ver1 = 0x1
    ver2 = 0x2
    ver3 = 0x3


@dataclass
class Input:
    tx_hash: str
    output_id: int


@dataclass
class Output:
    recipient: str  # address the amount is to be sent to
    amount: Decimal


class Transaction:
    id: int
    ver: TXVersion
    timestamp: int
    inputs: List[ Input ]  # tx_hash, output_id
    outputs: List[ Output ]  # recipient, amount
    fee: Decimal
    proof: bytes
    signature: bytes
    pubkey: bytes

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.ver = kwargs.get("ver") or kwargs.get("version")
        self.timestamp = kwargs.get("timestamp") or time.time()
        self.inputs = kwargs.get("inputs") or []
        self.outputs = kwargs.get("outputs") or []
        self.fee = kwargs.get("fee")
        self.proof = kwargs.get("proof")
        self.signature = kwargs.get("signature")
        self.pubkey = kwargs.get("pubkey")

    def __str__(self):
        s = f"<Transaction(id: {self.id}, ver: {self.ver}, timestamp: {self.timestamp}, inputs: {self.inputs}, outputs: {self.outputs}, fee: {self.fee}"
        if hasattr(self, "proof"):
            s += f", proof: {self.proof}"
        if hasattr(self, "signature"):
            s += f", signature: {self.signature}"
        if hasattr(self, "pubkey"):
            s += f", pubkey: {self.pubkey}"

        s += ")>"
        return s

    def __repr__(self):
        return str(self)

    def hash(self):
        h = chicken_hash(str(self))
        self.proof = h.hexdigest()
        return h

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
        elif isinstance(key, (bytes, str,)):
            priv_key = key
        else:
            raise TypeError(f"cannot sign transaction with key: {key}")
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(str(priv_key)), curve=CURVE)
        self.signature = hexdigest(sk.sign(bytes(str(self), encoding="utf-8")))
        return self.signature


if __name__ == "__main__":
    # test creating a transaction
    tx = Transaction()
    tx.id = 0
    tx.ver = TXVersion.ver1
    tx.timestamp = int(time.time())
    tx.fee = Decimal("1.0")

    # genesis input and output
    genesis = "genesis"
    ipt = Input(chicken_hash(genesis + "input").hexdigest(), 0)
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
