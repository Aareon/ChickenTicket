import pytest
from decimal import Decimal
import os
import sys
sys.path.append(os.path.abspath("src"))
from address import Address
from chain import Blockchain
from transaction import Transaction, Input, Output
from keys import KeyPair

@pytest.fixture
def blockchain():
    """
    Provides a fresh instance of the Blockchain class for each test case.
    """
    return Blockchain()

@pytest.fixture
def key_pair():
    """
    Generates a new key pair for signing transactions.
    """
    return KeyPair.new()


@pytest.fixture
def predefined_address_str():
    return "0x123456789000000000000000000000"


@pytest.fixture
def recipient_address(predefined_address_str):
    return Address(address=predefined_address_str)


def test_create_genesis_block(blockchain):
    """
    Test if the blockchain is initialized with a genesis block.

    Args:
        blockchain (Blockchain): The blockchain fixture.
    """
    assert len(blockchain.chain) == 1  # Assuming the genesis block is added in __init__

def test_add_block(blockchain):
    """
    Test adding a block to the blockchain.

    Args:
        blockchain (Blockchain): The blockchain fixture.
    """
    new_block = blockchain.create_block()
    blockchain.add_block(new_block)
    assert len(blockchain.chain) == 2

def test_add_transaction_to_current_block(blockchain, key_pair):
    """
    Test adding a transaction to the current block's transaction list.

    Args:
        blockchain (Blockchain): The blockchain fixture.
        key_pair (KeyPair): Fixture to generate cryptographic key pairs.
    """
    amount = Decimal("10.0")
    transaction = blockchain.create_transaction(sender, recipient, amount, key_pair)
    blockchain.add_transaction_to_current_block(transaction)
    assert len(blockchain.current_transactions) == 1

def test_fetch_output_amount(blockchain, key_pair):
    """
    Test fetching an output amount from a transaction stored in the blockchain.

    Args:
        blockchain (Blockchain): The blockchain fixture.
        key_pair (KeyPair): Fixture to generate cryptographic key pairs.
    """
    # Setup: Add a transaction with known output to the blockchain
    sender = "sender_address"
    recipient = "recipient_address"
    amount = Decimal("10.0")
    transaction = blockchain.create_transaction(sender, recipient, amount, key_pair)
    blockchain.add_transaction_to_current_block(transaction)

    # Mine a block containing the transaction to add it to the blockchain
    blockchain.mine()

    # Fetch the output amount from the transaction we added
    fetched_amount = blockchain.fetch_output_amount(transaction.hash(), 0)  # Assuming output_index is 0
    assert fetched_amount == amount

def test_validate_chain(blockchain):
    """
    Test the validation of the blockchain.

    Args:
        blockchain (Blockchain): The blockchain fixture.
    """
    # Assuming the validate_chain method returns True if the chain is valid
    assert blockchain.validate_chain() is True

# Add more tests as necessary for other methods and edge cases
