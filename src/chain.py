import sys
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple

from loguru import logger

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from block import Block  # noqa: E402
from crypto.chicken import chicken_hash  # noqa: E402
from keys import KeyPair  # noqa: E402
from transaction import Transaction  # noqa: E402
from utils.time_tools import get_timestamp  # noqa: E402


class Blockchain:
    """Represents a blockchain holding a sequence of blocks."""

    DIFFICULTY_ADJUSTMENT_INTERVAL = 5
    TARGET_BLOCK_TIME = 120  # Target time for block generation in seconds
    MAX_ADJUSTMENT_FACTOR = 1  # Maximum factor by which the difficulty can adjust

    def __init__(self):
        """Initializes the blockchain with a genesis block."""
        self.chain: List[Block] = []
        self.current_transactions: List[Transaction] = []  # mempool
        self.difficulty = 1  # Initial difficulty
        self.ema_block_time = (
            self.TARGET_BLOCK_TIME
        )  # Initial EMA equals target block time
        self.alpha = 0.5  # Smoothing factor for EMA calculation
        self.min_alpha = 0.001  # Minimum alpha value
        self.max_alpha = 0.5  # Maximum alpha value
        self.alpha_sensitivity = 0.2  # Sensitivity of alpha adjustments
        self.last_block_time = None  # Store the last block time for comparison
        self.scaling_factor = 0.2  # how aggressively the difficulty should adjust

        self.create_genesis_block()

        self.current_block = Block(
            version=1,
            idx=len(self.chain),
            previous_proof=self.chain[-1].proof,
            nonce=0,
            difficulty=self.difficulty,
        )  # Initialize with dummy values

    def create_genesis_block(self):
        """Creates and adds the genesis block to the blockchain."""
        genesis_block = Block(
            version=1, idx=0, previous_proof="0", nonce=0, difficulty=self.difficulty
        )
        genesis_transaction = Transaction(sender="0", recipient="0", amount=1)
        genesis_transaction.sign(KeyPair.new())
        genesis_block.add_transaction(genesis_transaction)
        genesis_block.timestamp = get_timestamp()
        self.chain.append(genesis_block)
        logger.info("Genesis block created.")

    def add_block(self, block: Block):
        """Adds a new block to the blockchain."""
        self.chain.append(block)
        self.adjust_difficulty(block)

    def add_transaction(self, transaction: Transaction) -> None:
        """Adds a transaction to the list of current transactions (mempool)."""
        self.current_transactions.append(transaction)

    def add_transaction_to_current_block(self, transaction: Transaction) -> None:
        """Adds a transaction to the current block's Trie."""
        self.current_block.add_transaction(transaction)

    def fetch_output_amount(self, tx_hash: str, output_index: int) -> Tuple[Decimal, Block]:
        """Fetches the output amount for a given transaction hash and output index from the entire blockchain.
        
        Args:
            tx_hash: The transaction hash as a string.
            output_index: The index of the output in the transaction.
        
        Returns:
            Tuple[Decimal, Block]: The output amount and the Block containing the transaction.
        
        Raises:
            ValueError: If the transaction with the specified hash is not found in the blockchain.
        """
        for block in self.chain:
            try:
                output_amount = block.fetch_output_amount(tx_hash, output_index)
                if output_amount is None:
                    continue
                return output_amount, block

            except ValueError:
                continue
        raise ValueError(f"Transaction with hash {tx_hash} not found in the blockchain.")

    def validate_chain(self) -> bool:
        """Validates the entire blockchain to ensure its integrity."""
        return True

    def create_transaction(
        self, sender: str, recipient: str, amount: Decimal, key_pair: KeyPair
    ) -> Transaction:
        """Creates a new transaction, signs it, and adds it to the list of current transactions."""
        transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
        proof = transaction.hash()
        logger.debug(f"Created transaction: {proof}")
        transaction.sign(key_pair)
        self.add_transaction(transaction)
        return transaction

    def calculate_difficulty(self):
        """Dynamically adjusts the mining difficulty."""
        if (
            len(self.chain) % self.DIFFICULTY_ADJUSTMENT_INTERVAL != 0
            or len(self.chain) < 2
        ):
            return (
                self.difficulty
            )  # Adjust difficulty only at specified intervals and if enough blocks exist

        # Calculate the actual mining time for the last block
        actual_time = self.chain[-1].timestamp - self.chain[-2].timestamp
        self.update_ema(actual_time)  # Update the EMA with the actual mining time

        # Calculate the deviation of the EMA from the target block time
        deviation = (
            self.ema_block_time - self.TARGET_BLOCK_TIME
        ) / self.TARGET_BLOCK_TIME

        # Calculate the adjustment factor based on the deviation, ensuring it's within the allowed range
        adjustment_factor = max(
            min(deviation * self.scaling_factor, self.MAX_ADJUSTMENT_FACTOR),
            -self.MAX_ADJUSTMENT_FACTOR,
        )

        # Apply the adjustment factor to the current difficulty
        if adjustment_factor > 0:
            new_difficulty = min(
                self.difficulty * (1 + adjustment_factor),
                self.difficulty + self.MAX_ADJUSTMENT_FACTOR,
            )
        else:
            new_difficulty = max(
                self.difficulty * (1 + adjustment_factor),
                self.difficulty - self.MAX_ADJUSTMENT_FACTOR,
            )

        new_difficulty = round(new_difficulty)

        # Ensure the new difficulty is at least 1, and no more than 64
        new_difficulty = max(1, min(new_difficulty, 64))

        return new_difficulty

    def adjust_alpha(self, time_difference):
        """Adjusts the alpha value based on the difference in block times."""
        # Normalize time difference based on a predefined scale (e.g., TARGET_BLOCK_TIME)
        normalized_diff = time_difference / self.TARGET_BLOCK_TIME
        # Adjust alpha based on the time difference and sensitivity
        delta_alpha = normalized_diff * self.alpha_sensitivity
        # Ensure alpha stays within the defined range
        self.alpha = max(self.min_alpha, min(self.max_alpha, self.alpha + delta_alpha))
        logger.info(f"Adjusted alpha to: {self.alpha}")

    def update_ema(self, actual_time):
        """Updates the Exponential Moving Average (EMA) of the block times."""
        if self.last_block_time is not None:
            time_difference = abs(actual_time - self.last_block_time)
            self.adjust_alpha(time_difference)

        self.ema_block_time = (self.alpha * actual_time) + (
            (1 - self.alpha) * self.ema_block_time
        )
        logger.info(
            f"Updated EMA block time: {self.ema_block_time} with alpha: {self.alpha}"
        )
        self.last_block_time = actual_time

    def adjust_difficulty(self, block: Block):
        """Adjusts the difficulty based on recent block times."""
        # Check if it's time to adjust the difficulty based on the block index
        if (block.idx + 1) % self.DIFFICULTY_ADJUSTMENT_INTERVAL == 0:
            self.difficulty = self.calculate_difficulty()
            logger.info(f"New difficulty after adjustment: {self.difficulty}")

        return self.difficulty

    def mine(self, block: Block = None):
        """
        Simulates the mining process for the current block, adding it to the blockchain.
        This method adjusts the proof and previous_proof attributes correctly.
        """
        last_block = self.chain[-1]
        new_difficulty = self.calculate_difficulty()

        # Prepare a new block with transactions from the mempool
        if block is None:
            block = Block(
                version=1,
                idx=len(self.chain),
                previous_proof=last_block.proof,
                nonce=0,
                difficulty=new_difficulty,
            )
            for transaction in self.current_transactions:
                block.add_transaction(transaction)

        # After adding transactions, calculate the state root
        block.calculate_state_root()

        # Find a valid nonce for the new block based on its difficulty
        nonce, proof = self.find_valid_nonce(block)
        block.nonce = nonce
        block.proof = proof

        # Add the mined block to the blockchain
        self.add_block(block)
        logger.info(
            f"Block {len(self.chain)} added to chain. EMA block time: {self.ema_block_time}"
        )

        # Prepare for the next block by clearing processed transactions
        self.current_transactions = []
        self.prepare_new_block()
        return block

    def prepare_new_block(self):
        """Prepares a new current block for the blockchain after the previous block has been mined and added to the chain."""
        last_block = self.chain[-1]  # Get the last block in the chain
        new_block_index = len(self.chain)  # The index for the new block
        new_block_previous_proof = (
            last_block.proof
        )  # The proof of the last block becomes the previous proof for the new block

        # Create a new block with the next index, the proof of the last block, and the current difficulty level
        self.current_block = Block(
            version=1,
            idx=new_block_index,
            previous_proof=new_block_previous_proof,
            nonce=0,  # Initial nonce value, will be determined by the mining process
            difficulty=self.calculate_difficulty(),  # Adjust the difficulty based on the current network conditions
        )

        # Since this is a new block, there are no transactions yet
        self.current_transactions = []
        return self.current_block

    def find_valid_nonce(self, block):
        """
        Finds a valid nonce for the given block, satisfying the blockchain's proof-of-work requirement.
        """
        prefix = f"{block.previous_proof}{block.state_root}{block.timestamp}".encode()
        nonce = 0
        while True:
            guess = prefix + str(nonce).encode()
            guess_hash = chicken_hash(guess).hex()
            if guess_hash.startswith("0" * block.difficulty):
                return nonce, guess_hash
            nonce += 1
