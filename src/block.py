from dataclasses import dataclass
from decimal import Decimal
import time
from typing import List
from crypto.chicken import chicken_hash
from merkle import MerkleTree
from mempool import MempoolTx


@dataclass
class BlockHeader:
    previous_proof: str
    merkle_root: str
    timestamp: int
    nonce: int


class Block:
    id: int
    previous_proof: str
    merkle_root: str
    timestamp: int
    nonce: int

    def __init__(self, id: int, last_block, nonce, previous_proof: str=None, merkle_root:str=None, timestamp=None, reward: Decimal = None, recipients: List[str] = []):
        self.id = id
        self.last_block = last_block
        self.nonce = nonce
        self.timestamp = timestamp or int(time.time())
        self.tree = MerkleTree(hash_function=chicken_hash)
        self.proof = None
        self.previous_proof = previous_proof
        self.merkle_root = merkle_root
        self.difficulty = self.calculate_difficulty()

        if hasattr(last_block, "proof"):
            self.previous_proof = last_block.proof

        self.transactions = []

    @property
    def is_missing(self) -> List:
        missing = []
        if self.merkle_root is None:
            missing.append("merkle_root")
        if self.proof is None:
            missing.append("proof")
        if self.previous_proof is None:
            missing.append("previous_proof")

        if len(missing) > 0:
            return missing

    @property
    def is_ready(self) -> bool:
        if self.is_missing is not None and len(self.is_missing) > 0:
            return False
        else:
            return True

    @property
    def header(self):
        if not self.tree.is_ready and self.merkle_root is None:
            self.tree.make_tree()

        self.merkle_root = self.tree.get_merkle_root()
        return BlockHeader(self.previous_proof, self.merkle_root, self.timestamp, self.nonce)

    def add_transaction(self, tx):
        if isinstance(tx, MempoolTx):
            tx = tx.tx
        if tx not in self.transactions:
            self.transactions.append(tx)
            self.tree.add_leaf(str(tx), True)

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
        bomb = 2 ** period_count

        # calculation for target
        self.difficulty = (self.last_block.difficulty + offset * sign) + bomb
        return self.difficulty

    def hash(self):
        self.proof = chicken_hash(str(self)).hexdigest()
        return self.proof

    def __str__(self):
        s = f"<Block(id: {self.id}, timestamp: {self.timestamp}, header: <{self.header}>, transactions: {self.transactions}"
        if hasattr(self, "difficulty"):
            s += f", difficulty: {self.difficulty}"
        if hasattr(self, "proof"):
            if self.proof is not None:
                s += f", proof: {self.proof}"
        s += ")>"
        return s

    def __repr__(self):
        return f"{str(self)[:-2]}, is_ready: {self.is_ready})>"


if __name__ == "__main__":
    # test creating a block
    block = Block(0, None, 69420)
    genesis = "genesis"
    block.previous_proof = chicken_hash(genesis + "previous_proof").hexdigest()

    from transaction import Transaction, TXVersion, Input, Output
    tx = Transaction()
    tx.id = 0
    tx.ver = TXVersion.ver1
    tx.fee = Decimal("1.0")

    # genesis input and output
    genesis = "genesis"
    ipt = Input(chicken_hash(genesis + "input").hexdigest(), 0)
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
