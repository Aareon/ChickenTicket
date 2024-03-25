import sys
from decimal import Decimal
from loguru import logger
from time import sleep

from src.keys import KeyPair
from src.chain import Blockchain
from src.transaction import Transaction


def main():
    logger.info("Starting blockchain test script...")

    # Initialize blockchain with the genesis block
    blockchain = Blockchain()
    logger.info("Genesis block created. Difficulty set to: {}", blockchain.difficulty)

    # Create a new key pair for our transactions
    key_pair = KeyPair.new()

    # Define a function to simulate transaction creation and addition
    def create_and_add_transaction(sender, recipient, amount, transaction_number):
        logger.info(f"Creating transaction {transaction_number}...")
        transaction = Transaction(sender=sender, recipient=recipient, amount=Decimal(amount))
        transaction.sign(key_pair)
        logger.info(f"Created transaction {transaction_number}: {transaction}")
        logger.info(f"Adding transaction {transaction_number} to the current block...")
        blockchain.add_transaction(transaction)
        logger.info(f"Added transaction {transaction_number} to the current block. Current block transaction count: {len(blockchain.current_block.get_transactions_as_list())}")

    # Create and add the first transaction
    create_and_add_transaction("sender1", "recipient1", "10.0", 1)

    # Simulate a brief wait to mimic transaction time intervals
    logger.info("Simulating transaction interval...")
    sleep(0.5)

    # Create and add the second transaction
    create_and_add_transaction("sender2", "recipient2", "20.0", 2)

    # Simulate mining the current block
    logger.info("Mining a new block, this may take some time...")
    blockchain.mine()
    logger.info("Mined a new block and added it to the blockchain. New blockchain length: {}", len(blockchain.chain))

    # Simulate waiting to mimic real-world block generation time
    sleep(1)

    # Simulate creating and mining more blocks to test difficulty adjustment
    for i in range(3, 6):
        create_and_add_transaction(f"sender{i}", f"recipient{i}", f"{i*10}.0", i)
        logger.info(f"Preparing to mine block {i}, adjusting difficulty based on network conditions. Current difficulty: {blockchain.difficulty}")
        blockchain.mine()
        logger.info(f"Mined block {i} and added it to the blockchain. New blockchain length: {len(blockchain.chain)}")
        sleep(0.5)  # Adjust sleep time to see the effect on mining difficulty

    # Display the blockchain state
    for block in blockchain.chain:
        logger.info(f"Block {block.idx}: {block}")

if __name__ == "__main__":
    main()
