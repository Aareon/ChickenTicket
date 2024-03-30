import sys
from decimal import Decimal
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from address import Address  # noqa: E402
from block import Block  # noqa: E402
from chain import Blockchain  # noqa: E402
from keys import KeyPair  # noqa: E402
from transaction import Output  # noqa: E402


@pytest.fixture
def blockchain():
    """
    Provides a fresh instance of the Blockchain class for each test case.
    """
    return Blockchain()


@pytest.fixture
def sender_key_pair():
    """Generates a new key pair for the sender."""
    return KeyPair.from_seed("pytest sender keypair")


@pytest.fixture
def recipient_key_pair():
    """Generates a new key pair for the recipient."""
    return KeyPair.from_seed("pytest recipient keypair")


@pytest.fixture
def sender_address(sender_key_pair: KeyPair):
    """Generates a sender address from the sender's key pair."""
    return Address.new(sender_key_pair)

@pytest.fixture
def basic_output(sender_address: Address):
    """Generates a basic output."""
    return Output(sender_address, Decimal("10.0"))


@pytest.fixture
def recipient_address(recipient_key_pair: KeyPair):
    """Generates a recipient address from the recipient's key pair."""
    return Address.new(recipient_key_pair)


def test_create_genesis_block(blockchain: Blockchain):
    """
    Test if the blockchain is initialized with a genesis block.

    Args:
        blockchain (Blockchain): The blockchain fixture.
    """
    assert len(blockchain.chain) == 1  # Assuming the genesis block is added in __init__


def test_add_block(blockchain: Blockchain, sender_key_pair: KeyPair, sender_address: Address, recipient_address: Address):
    """
    Test adding a block to the blockchain.

    Args:
        blockchain (Blockchain): The blockchain fixture.
    """
    new_block = Block(
        version=1, idx=len(blockchain.chain), previous_proof="123", nonce=100
    )
    transaction = blockchain.create_transaction(
        str(sender_address), str(recipient_address), Decimal("10.0"), sender_key_pair
    )
    new_block.add_transaction(
        transaction
    )  # Use a method that properly adds a transaction
    blockchain.add_block(new_block)


def test_add_transaction_to_current_block(blockchain: Blockchain, sender_key_pair: KeyPair, basic_output: Output):
    """
    Test adding a transaction to the current block's transaction list.

    Args:
        blockchain (Blockchain): The blockchain fixture.
        sender_key_pair (KeyPair): Fixture to generate cryptographic key pairs.
    """
    amount = Decimal("10.0")
    transaction = blockchain.create_transaction(
        str(sender_address), str(recipient_address), amount, sender_key_pair
    )
    transaction.add_output(basic_output)
    transaction.sign(sender_key_pair)
    blockchain.add_transaction_to_current_block(transaction)
    assert len(blockchain.current_transactions) == 1


def test_fetch_output_amount(blockchain: Blockchain, sender_key_pair: KeyPair, recipient_address: Address, basic_output):
    """
    Test fetching an output amount from a transaction stored in the blockchain.

    Args:
        blockchain (Blockchain): The blockchain fixture.
        sender_key_pair (KeyPair): Fixture to generate cryptographic key pairs.
        recipient_address (Address): Fixture to provide a recipient address.
    """
    # Setup: Create a transaction and add it to the blockchain
    sender = str(
        sender_key_pair.pub
    )  # Assuming sender's address is derived from the public key
    recipient = str(recipient_address)
    amount = Decimal("10.0")
    transaction = blockchain.create_transaction(
        sender, recipient, amount, sender_key_pair
    )
    transaction.add_output(basic_output)
    blockchain.add_transaction(transaction)

    # Manually mine a block to include the transaction in the blockchain
    new_block = blockchain.prepare_new_block()
    new_block.add_transaction(transaction)
    blockchain.add_block(new_block)

    # Fetch the output amount from the transaction we added
    # Assuming transaction outputs are indexed starting at 0 and the test transaction has a single output
    fetched_amount, _ = blockchain.fetch_output_amount(transaction.proof, 0)  # Assuming the method returns a tuple (Decimal, Block)
    assert (
        fetched_amount == amount
    ), "Fetched output amount does not match the expected value."


def test_validate_chain(blockchain: Blockchain):
    """
    Test the validation of the blockchain.

    Args:
        blockchain (Blockchain): The blockchain fixture.
    """
    # Assuming the validate_chain method returns True if the chain is valid
    assert blockchain.validate_chain() is True


# Add more tests as necessary for other methods and edge cases
