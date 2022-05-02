from dataclasses import dataclass
from decimal import Decimal
from typing import List

from crypto.chicken import chicken_hash
from utils.merkle import MerkleTree
from utils.time_tools import get_timestamp

try:
    import ujson as json

    USING_UJSON = True
except ImportError:
    import json

    USING_UJSON = False


class BlockException(Exception):
    """Base class for block related exceptions"""


@dataclass
class BlockHeader:
    version: int
    previous_proof: str
    merkle_root: str
    timestamp: int
    nonce: int

    def to_dict(self):
        return {
            "ver": self.version,
            "prev_proof": self.previous_proof,
            "merkle": self.merkle_root,
            "time": self.timestamp,
            "nonce": self.nonce,
        }

    def json(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def __str__(self):
        return self.json()


class Block:
    version = int
    idx: int
    previous_proof: str
    merkle_root: str
    timestamp: int
    header: BlockHeader

    def __init__(self, **kwargs):
        self.version = kwargs.get("ver") or kwargs.get("version")
        self.idx = kwargs.get("idx")
        self.last_block = kwargs.get("last_block")
        self.nonce = kwargs.get("nonce")
        self.timestamp = kwargs.get("timestamp") or get_timestamp()
        self.tree = MerkleTree()  # sha256 hashed merkle tree
        self.previous_proof = kwargs.get("previous_proof")
        self.merkle_root = kwargs.get("merkle_root")
        self.proof = None
        self.difficulty = self.calculate_difficulty()
        self.reward = None
        self.transactions = kwargs.get("transactions") or kwargs.get("txs") or []

        if hasattr(self.last_block, "proof"):
            self.previous_proof = last_block.proof

    def to_dict(self):
        return {
            "idx": self.idx,
            "header": self.header.to_dict(),
            "last_block": self.last_block,
            "reward": self.reward,
            "txs": [tx.to_dict() for tx in self.transactions]
            if self.transactions
            else None,
            "hash": self.proof,
            "difficulty": self.difficulty,
        }

    def json(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    @property
    def header(self):
        if not self.tree.is_ready and self.merkle_root is None:
            self.tree.make_tree()

        self.merkle_root = self.tree.get_merkle_root()
        return BlockHeader(
            self.version,
            self.previous_proof,
            self.merkle_root,
            self.timestamp,
            self.nonce,
        )

    def add_transaction(self, tx):
        if self.transactions is not None and tx not in self.transactions:
            self.transactions.append(tx)
            self.tree.add_leaf(tx.json(), True)

    def calculate_difficulty(self):
        if isinstance(self.last_block, Block):
            last_diff = self.last_block.difficulty
        elif self.last_block is None:
            self.difficulty = 20
            return self.difficulty

        # the factor to move difficulty, how much it should be moved at one time
        offset = last_diff.difficulty // 2048

        # difference between block timestamps
        # turn the time_diff into an integer, we only care about a difference of 10 seconds
        time_diff = (self.timestamp - self.last_block.timestamp) // 100000

        # get exponent to move difficulty (i.e. up or down)
        sign = 1 if time_diff < 10 else -1

        # calculation for bomb
        # bomb is the amount to add to diff every n blocks
        # in this case, its every 150000th block
        period_count = (self.last_block.index + 1) // 101000
        period_count -= 2  # free periods, how many times the bomb can be ignored
        bomb = 2**period_count

        # calculation for target
        self.difficulty = (self.last_block.difficulty + offset * sign) + bomb
        return self.difficulty

    def hash(self):
        data = self.to_dict()
        # header contains the miner rewardee's address and
        # can't be included in the process that validates the block
        del data["header"]
        del data["hash"]
        self.proof = chicken_hash(json.dumps(data).encode()).hex()
        return self.proof

    @classmethod
    def from_json(cls, data):
        try:
            return cls(**json.loads(data))
        except:
            raise

    def validate(self):
        # TODO
        # check height
        # check proof
        # check transactions
        raise NotImplementedError

    def __str__(self):
        return self.json()


if __name__ == "__main__":
    # test creating a block
    block = Block(0, None, 69, reward=69)
    genesis = "genesis"
    block.previous_proof = chicken_hash((genesis + "previous_proof").encode()).hex()

    from transaction import Input, Output, Transaction, TXVersion

    tx = Transaction()
    tx.idx = 0
    tx.ver = TXVersion.ver1
    tx.fee = Decimal("1.0")

    # genesis input and output
    genesis = "genesis"
    ipt = Input(chicken_hash((genesis + "input").encode()).hex(), 0)
    tx.add_input(ipt)

    opt = Output("0x0", Decimal("1.0"))
    tx.add_output(opt)

    # create a key just to sign the tx
    from keys import KeyPair

    keys = KeyPair.new()
    tx.sign(keys)

    block.add_transaction(tx)
    block.hash()
    print(block)
