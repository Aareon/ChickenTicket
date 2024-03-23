from decimal import Decimal
from typing import List

from block import Block
from keys import KeyPair
from transaction import Transaction


class Blockchain:
    """Represents a blockchain holding a sequence of blocks.

    Attributes:
        chain (List[Block]): A list of Block objects forming the blockchain.
        current_transactions (List[Transaction]): A list of Transaction objects waiting to be included in the next block.
    """

    def __init__(self):
        """Initializes the blockchain with a genesis block."""
        self.chain: List[Block] = []
        self.current_transactions: List[Transaction] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """Creates and adds the genesis block to the blockchain."""
        genesis_block = Block(version=1, idx=0, previous_proof="1", nonce=100)
        self.chain.append(genesis_block)

    def add_block(self, block: Block):
        """Adds a new block to the blockchain.

        Args:
            block (Block): The block to be added to the chain.
        """
        self.chain.append(block)

    def add_transaction(self, transaction: Transaction) -> None:
        """Adds a transaction to the list of current transactions.

        Args:
            transaction (Transaction): The transaction to be added.
        """
        self.current_transactions.append(transaction)

    def fetch_output_amount(self, tx_hash: str, output_index: int) -> Decimal:
        """Fetches the output amount for a given transaction hash and output index from the entire blockchain.

        Args:
            tx_hash (str): The hash of the transaction to search for.
            output_index (int): The index of the output within the transaction to retrieve the amount for.

        Returns:
            Decimal: The amount of the specified output.

        Raises:
            ValueError: If the transaction with the specified hash is not found.
        """
        for block in self.chain:
            try:
                return block.fetch_output_amount(tx_hash, output_index)
            except ValueError:
                continue
        raise ValueError(f"Transaction with hash {tx_hash} not found in the blockchain.")

    def validate_chain(self) -> bool:
        """Validates the entire blockchain to ensure its integrity.

        Returns:
            bool: True if the blockchain is valid, False otherwise.
        """
        # Here, you would include validation logic such as verifying block hashes,
        # checking that each block's previous hash matches the hash of the preceding block,
        # and other relevant validations depending on your blockchain's design.
        return True

    def create_transaction(
        self, sender: str, recipient: str, amount: Decimal, key_pair: KeyPair
    ) -> Transaction:
        """Creates a new transaction, signs it, and adds it to the list of current transactions.

        Args:
            sender (str): The address of the sender.
            recipient (str): The address of the recipient.
            amount (Decimal): The amount to be transferred.
            key_pair (KeyPair): The key pair of the sender for signing the transaction.

        Returns:
            Transaction: The newly created and signed transaction.
        """
        transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
        transaction.sign(key_pair)
        self.add_transaction(transaction)
        return transaction

    def mine(self):
        """Simulates the mining process, creating a new block and adding it to the blockchain."""
        # This method would include the logic to select transactions from current_transactions,
        # find a valid nonce for the new block according to the proof-of-work algorithm,
        # and add the newly mined block to the chain.
        pass
