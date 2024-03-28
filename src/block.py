import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from loguru import logger
from trie import HexaryTrie

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from crypto.chicken import chicken_hash  # noqa: E402
from utils.time_tools import get_timestamp  # noqa: E402

try:
    import ujson as json
except ImportError:
    import json


@dataclass
class BlockHeader:
    """
    Represents the header of a blockchain block.

    Attributes:
        version (int): The version of the block.
        previous_proof (str): The proof of the previous block in the chain.
        state_root (str): The root hash of the state trie after this block's transactions.
        timestamp (int): The timestamp of the block creation.
        nonce (int): The nonce used for the proof-of-work algorithm.
    """

    version: int
    previous_proof: str
    state_root: str
    timestamp: int
    nonce: int

    def to_dict(self):
        """Converts the block header into a dictionary representation."""
        return {
            "ver": self.version,
            "prev_proof": self.previous_proof,
            "state_root": self.state_root,
            "time": self.timestamp,
            "nonce": self.nonce,
        }

    def json(self):
        """Serializes the block header into a JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)


class Block:
    """
    Represents a block in the blockchain.

    Attributes:
        version (int): The version of the block.
        idx (int): The index of the block in the chain.
        previous_proof (str): The proof of the previous block in the chain.
        nonce (int): The nonce used for the proof-of-work algorithm.
        timestamp (int): The timestamp of the block creation.
        transactions (HexaryTrie): A trie structure containing the block's transactions.
        state_root (str): The root hash of the state trie after this block's transactions.
        proof (None or str): The proof of work for the block.
        difficulty (int): The difficulty target for the proof-of-work algorithm.
        reward (str): The reward for mining the block.
    """

    def __init__(self, **kwargs):
        self.version = kwargs.get("version")
        self.idx = kwargs.get("idx")
        self.previous_proof = kwargs.get("previous_proof")
        self.nonce = kwargs.get("nonce")
        self.timestamp = kwargs.get("timestamp") or get_timestamp()
        self.transactions = HexaryTrie(db={})
        self.state_root = ""
        self.proof = None
        self.difficulty = kwargs.get("difficulty", 1)
        self.reward = kwargs.get("reward", 1)

    def calculate_state_root(self):
        # The state root is the root hash of the transactions trie after all transactions have been added
        self.state_root = self.transactions.root_hash.hex()

    def to_dict(self):
        """Converts the block into a dictionary representation."""
        return {
            "version": self.version,
            "idx": self.idx,
            "previous_proof": self.previous_proof,
            "state_root": self.state_root,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "transactions": self.get_transactions_as_list(),
            "proof": self.proof,
            "difficulty": self.difficulty,
        }

    def __str__(self):
        """Returns a JSON string representation of the block."""
        return self.json()

    def json(self):
        """Serializes the block into a JSON string."""
        try:
            return json.dumps(self.to_dict(), sort_keys=True)
        except TypeError:
            logger.debug(
                type(self.previous_proof), type(self.state_root), type(self.proof)
            )
            raise

    def hash(self):
        """
        Calculates and sets the block's proof.

        Returns:
            str: The hexadecimal string representing the block's hash.
        """
        self.proof = chicken_hash(json.dumps(self.to_dict()).encode()).hex()
        return self.proof

    def add_transaction(self, transaction):
        """
        Adds a transaction to the block.

        Args:
            transaction (Transaction): The transaction to add.
        """
        logger.info(f"Adding transaction to block {transaction.proof}...")
        tx_id_bytes = bytes(transaction.proof, "utf-8")
        transaction_data = transaction.json().encode()
        self.transactions[tx_id_bytes] = transaction_data
        self.state_root = self.transactions.root_hash.hex()
        logger.debug(f"Transaction {transaction.idx} added to Block {self.idx}")

    def get_transactions_as_list(self) -> list:
        """
        Traverses the trie and constructs a list of transactions.

        Returns:
            A list of transactions contained within the block.
        """
        transactions_list = []
        root_node = self.transactions.traverse(())

        # Traverse function to recursively visit each node
        def traverse_node(node, prefix=tuple()):
            if node.value:
                # If this node has a value, it's a leaf node, decode the value (transaction data)
                transactions_list.append(json.loads(node.value.decode("utf-8")))
            else:
                # This node is a branch or extension node, traverse its children
                for sub_segment in node.sub_segments:
                    child_prefix = prefix + sub_segment
                    child_node = self.transactions.traverse(child_prefix)
                    traverse_node(child_node, prefix=child_prefix)

        traverse_node(root_node)

        return transactions_list

    def fetch_output_amount(self, transaction_hash: str, output_index: int) -> Decimal:
        """
        Fetches the output amount for a given transaction hash and output index.

        Args:
            transaction_hash (str): The hash of the transaction.
            output_index (int): The index of the output within the transaction.

        Returns:
            Decimal: The amount associated with the specified transaction output.
        """
        transactions = self.get_transactions_as_list()
        logger.debug(f"Transactions in block: {transactions}")
        if len(transactions) == 0:
            raise ValueError("No transactions found in the block.")
        elif len(transactions) < output_index - 1:
            raise ValueError("Output index out of range.")
        try:
            for i, transaction in enumerate(transactions):
                if transaction["proof"] == transaction_hash:
                    try:
                        return Decimal(transaction["outputs"][output_index]["amount"])
                    except IndexError:
                        raise ValueError("Invalid output index.")
            raise ValueError("Invalid transaction hash or output index.")
        except KeyError:
            raise ValueError("Invalid transaction hash or output index.")

    def validate(self):
        """Validates the block. Currently a placeholder."""
        pass


if __name__ == "__main__":
    # Initialize logging and the blockchain
    from loguru import logger

    from address import Address
    from chain import Blockchain
    from keys import KeyPair

    # Initialize the blockchain with the genesis block
    chain = Blockchain()
    logger.info("Genesis block created.")

    # Create key pairs for Genesis and Aareon
    genesis_key_pair = KeyPair.from_seed("genesis_seed")
    aareon_key_pair = KeyPair.from_seed("aareon_seed")
    genesis_addr = Address(genesis_key_pair)
    aareon_addr = Address(aareon_key_pair)

    # Mine a total of 5 blocks, each with a transaction
    for block_num in range(0, 2):
        # Simulate creating a transaction from Genesis to Aareon
        amount = 100 * block_num  # Vary the amount for demonstration
        transaction = chain.create_transaction(
            genesis_addr, aareon_addr, amount, genesis_key_pair
        )
        transaction.sign(genesis_key_pair)

        # Log the created transaction
        logger.info(f"Block {block_num} - Created transaction: {transaction}")

        block = chain.prepare_new_block()

        # Add the transaction to the current block's Trie and mine the block
        chain.add_transaction_to_current_block(transaction)
        logger.info(f"Block {block_num} - Mining block with transaction {transaction.proof}...")
        block = chain.mine(block)
        chain.add_block(block)

        # Log the newly mined block
        logger.info(
            f"Block {block_num} mined and added to the blockchain. Block: {chain.chain[-1]}"
        )

        amount = chain.fetch_output_amount(transaction.proof, 0)
        logger.info(f"Block {block_num} - Output amount: {amount}")
