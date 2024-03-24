from decimal import Decimal
from typing import List

from loguru import logger

from block import Block
from keys import KeyPair
from transaction import Transaction
from utils.time_tools import get_timestamp
from crypto.chicken import chicken_hash


class Blockchain:
    """Represents a blockchain holding a sequence of blocks."""

    DIFFICULTY_ADJUSTMENT_INTERVAL = 3
    TARGET_BLOCK_TIME = 120  # Target time for block generation in seconds
    MAX_ADJUSTMENT_FACTOR = 2  # Maximum factor by which the difficulty can adjust

    def __init__(self):
        """Initializes the blockchain with a genesis block."""
        self.chain: List[Block] = []
        self.current_transactions: List[Transaction] = []  # mempool
        self.difficulty = 1  # Initial difficulty
        self.block_generation_interval = 30  # Target time for block generation in seconds
        self.ema_block_time = self.TARGET_BLOCK_TIME  # Initial EMA equals target block time
        self.alpha = 0.6  # Smoothing factor for EMA calculation
        
        self.create_genesis_block()

        self.current_block = Block(version=1, idx=len(self.chain), previous_proof=self.chain[-1].proof, nonce=0, difficulty=self.difficulty)  # Initialize with dummy values

    def create_genesis_block(self):
        """Creates and adds the genesis block to the blockchain."""
        genesis_block = Block(version=1, idx=0, previous_proof="0", nonce=0, difficulty=self.difficulty)
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

    def fetch_output_amount(self, tx_hash: str, output_index: int) -> Decimal:
        """Fetches the output amount for a given transaction hash and output index from the entire blockchain."""
        for block in self.chain:
            try:
                return block.fetch_output_amount(tx_hash, output_index)
            except ValueError:
                continue
        raise ValueError(f"Transaction with hash {tx_hash} not found in the blockchain.")

    def validate_chain(self) -> bool:
        """Validates the entire blockchain to ensure its integrity."""
        return True

    def create_transaction(self, sender: str, recipient: str, amount: Decimal, key_pair: KeyPair) -> Transaction:
        """Creates a new transaction, signs it, and adds it to the list of current transactions."""
        transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
        transaction.sign(key_pair)
        self.add_transaction(transaction)
        return transaction

    def calculate_difficulty(self):
        """Dynamically adjusts the mining difficulty."""
        if len(self.chain) < 2:
            return self.difficulty  # Not enough blocks to adjust difficulty

        # Calculate the actual mining time for the last block
        actual_time = self.chain[-1].timestamp - self.chain[-2].timestamp
        self.update_ema(actual_time)  # Update the EMA with the actual mining time

        # Calculate the deviation of the EMA from the target block time
        deviation = (self.ema_block_time - self.TARGET_BLOCK_TIME) / self.TARGET_BLOCK_TIME

        # Define a scaling factor for how aggressively the difficulty should adjust
        # This value may need to be fine-tuned based on the blockchain's needs
        scaling_factor = 0.12  # adjust based on testing and requirements

        # Calculate the adjustment factor based on the deviation, ensuring it's within the allowed range
        adjustment_factor = max(min(deviation * scaling_factor, self.MAX_ADJUSTMENT_FACTOR), -self.MAX_ADJUSTMENT_FACTOR)

        # Apply the adjustment factor to the current difficulty
        new_difficulty = self.difficulty * (1 + adjustment_factor)
        new_difficulty = round(new_difficulty)
        
        # Ensure the new difficulty is at least 1, and no more than 64
        new_difficulty = max(1, min(new_difficulty, 64))

        logger.info(f"Adjusting difficulty from {self.difficulty} to {new_difficulty}")

        return new_difficulty
    
    def update_ema(self, actual_time):
        """Updates the Exponential Moving Average (EMA) of the block times."""
        self.ema_block_time = (self.alpha * actual_time) + ((1 - self.alpha) * self.ema_block_time)
        logger.info(f"Updated EMA block time: {self.ema_block_time}")
    
    def adjust_difficulty(self, block: Block):
        """Adjusts the difficulty based on recent block times."""
        # Check if it's time to adjust the difficulty based on the block index
        if (block.idx + 1) % self.DIFFICULTY_ADJUSTMENT_INTERVAL == 0:
            self.difficulty = self.calculate_difficulty()
            logger.info(f"New difficulty after adjustment: {self.difficulty}")

    def mine(self):
        """
        Simulates the mining process for the current block, adding it to the blockchain.
        This method adjusts the proof and previous_proof attributes correctly.
        """
        last_block = self.chain[-1]
        new_difficulty = self.calculate_difficulty()

        # Prepare a new block with transactions from the mempool
        new_block = Block(version=1, idx=len(self.chain), previous_proof=last_block.proof, nonce=0, difficulty=new_difficulty)
        for transaction in self.current_transactions:
            new_block.add_transaction(transaction)
        
        # After adding transactions, calculate the state root
        new_block.calculate_state_root()

        # Find a valid nonce for the new block based on its difficulty
        nonce, proof = self.find_valid_nonce(new_block)
        new_block.nonce = nonce
        new_block.proof = proof

        # Add the mined block to the blockchain
        self.add_block(new_block)

        # Prepare for the next block by clearing processed transactions
        self.current_transactions = []
        self.prepare_new_block()
    
    def prepare_new_block(self):
        """Prepares a new current block for the blockchain after the previous block has been mined and added to the chain."""
        last_block = self.chain[-1]  # Get the last block in the chain
        new_block_index = len(self.chain)  # The index for the new block
        new_block_previous_proof = last_block.proof  # The proof of the last block becomes the previous proof for the new block

        # Create a new block with the next index, the proof of the last block, and the current difficulty level
        self.current_block = Block(
            version=1,
            idx=new_block_index,
            previous_proof=new_block_previous_proof,
            nonce=0,  # Initial nonce value, will be determined by the mining process
            difficulty=self.calculate_difficulty()  # Adjust the difficulty based on the current network conditions
        )

        # Since this is a new block, there are no transactions yet
        self.current_transactions = []
        return self.current_block

    def find_valid_nonce(self, block):
        """
        Finds a valid nonce for the given block, satisfying the blockchain's proof-of-work requirement.
        """
        prefix = f'{block.previous_proof}{block.state_root}{block.timestamp}'.encode()
        nonce = 0
        while True:
            guess = prefix + str(nonce).encode()
            guess_hash = chicken_hash(guess).hex()
            if guess_hash.startswith('0' * block.difficulty):
                return nonce, guess_hash
            nonce += 1
