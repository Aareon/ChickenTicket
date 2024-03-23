from decimal import Decimal
import pytest

import sys
import os

sys.path.append(os.path.abspath("src"))
from block import Block
from transaction import Transaction, Input, Output
from address import Address


@pytest.fixture
def basic_block():
    """Fixture for creating a basic block with default parameters."""
    return Block(version=1, idx=0, previous_proof='0000', nonce=100, reward="50")


@pytest.fixture
def predefined_address_str():
    """Fixture for a predefined address string."""
    return "0x9af9a62f65f9f18bd13213db79A1t2"


@pytest.fixture
def recipient_address(predefined_address_str):
    """Fixture for creating an Address instance."""
    return Address(address=predefined_address_str)


@pytest.fixture
def basic_transaction(recipient_address):
    """
    Fixture for creating a basic transaction.
    
    Assumes the Address class has been correctly implemented.
    """
    input_tx_hash = "abc123"  # Example previous transaction hash
    return Transaction(
        inputs=[Input(tx_hash=input_tx_hash, output_id=0)],
        outputs=[Output(recipient=recipient_address, amount=Decimal('10'))]
    )


def test_block_creation(basic_block):
    """
    Test the creation of a Block and its initial state.
    """
    block = basic_block
    assert block.version == 1
    assert block.idx == 0
    assert block.previous_proof == '0000'
    assert block.nonce == 100
    assert isinstance(block.timestamp, int)
    assert block.state_root == ""  # Assuming initial state root is empty or has a default value
    assert block.proof is None
    assert block.difficulty == 1  # Or your default difficulty
    assert block.get_transactions_as_list() == []


def test_block_transactions(basic_block, basic_transaction):
    """
    Test adding transactions to the block and retrieving them.
    """
    block = basic_block
    block.add_transaction(basic_transaction)
    transactions = block.get_transactions_as_list()

    assert len(transactions) == 1
    assert transactions[0]['inputs'][0]['tx'] == "abc123"
    assert Decimal(transactions[0]['outputs'][0]['amount']) == Decimal('10')
    assert block.state_root != ""  # The state root should change when a transaction is added


def test_block_hashing(basic_block, basic_transaction):
    """
    Test the hashing of a Block.
    """
    block = basic_block
    block.add_transaction(basic_transaction)
    block_hash = block.hash()  # Assuming hash method exists and updates the block's proof attribute

    assert block_hash == block.proof
    assert isinstance(block_hash, str)
