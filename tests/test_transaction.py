import os
import sys
from decimal import Decimal
import pytest

sys.path.append(os.path.abspath("src"))
from address import Address
from crypto.chicken import chicken_hash
from keys import KeyPair
from transaction import Input, Output, Transaction, TXVersion, TransactionValidationError


@pytest.fixture
def key_pair():
    return KeyPair.new()


@pytest.fixture
def predefined_address_str():
    return "0x123456789000000000000000000000"


@pytest.fixture
def recipient_address(predefined_address_str):
    return Address(address=predefined_address_str)


@pytest.fixture
def valid_inputs_outputs(recipient_address):
    input_tx_hash = chicken_hash(b"input_tx").hex()
    inputs = [Input(tx_hash=input_tx_hash, output_id=0)]
    outputs = [Output(recipient=recipient_address, amount=Decimal('10'))]
    return inputs, outputs


def test_transaction_instantiation():
    """Test that a Transaction can be instantiated with default values."""
    tx = Transaction()
    assert tx.idx == 0
    assert tx.ver == TXVersion.ver1
    assert isinstance(tx.timestamp, int)
    assert tx.inputs == []
    assert tx.outputs == []
    assert tx.fee == Decimal("0")
    assert tx.proof is None
    assert tx.signature is None
    assert tx.pubkey is None


def test_add_input_output(recipient_address):
    """Test adding inputs and outputs to a Transaction."""
    tx = Transaction()
    input_tx_hash = chicken_hash(b"input_tx").hex()
    input_ = Input(tx_hash=input_tx_hash, output_id=0)
    output = Output(recipient=recipient_address, amount=Decimal("10"))
    tx.add_input(input_)
    tx.add_output(output)
    assert len(tx.inputs) == 1
    assert len(tx.outputs) == 1
    assert tx.inputs[0].tx_hash == input_tx_hash
    assert tx.outputs[0].recipient == recipient_address
    assert tx.outputs[0].amount == Decimal("10")


def test_transaction_hashing():
    """Test hashing a Transaction."""
    tx = Transaction()
    tx_hash = tx.hash()
    assert tx_hash == tx.proof
    assert isinstance(tx_hash, str)


def test_transaction_signing():
    """Test signing a Transaction and its effect on the Transaction's attributes."""
    key_pair = KeyPair.new()  # Assuming this generates a new key pair
    tx = Transaction()
    signature = tx.sign(key_pair)

    assert tx.signature == signature
    assert tx.pubkey == key_pair.pub.data
    assert isinstance(signature, str)


def test_validate_successful(predefined_address_str):
    """Test that a transaction passes validation when correctly formed."""
    key_pair = KeyPair.new()
    tx = Transaction()
    tx.add_input(Input("some_tx_hash", 0))
    tx.add_output(Output(Address(address=predefined_address_str), Decimal("10")))
    tx.fee = Decimal("1.0")
    tx.hash()
    tx.sign(key_pair)

    assert tx.validate() is True


def test_validate_fails_no_inputs(predefined_address_str):
    with pytest.raises(TransactionValidationError, match="at least one input and one output"):
        tx = Transaction(outputs=[Output(recipient=Address(address=predefined_address_str), amount=Decimal('10'))], fee=Decimal('0'))
        tx.validate()

def test_validate_fails_no_outputs():
    input_tx_hash = chicken_hash(b"input_tx").hex()
    with pytest.raises(TransactionValidationError, match="at least one input and one output"):
        tx = Transaction(inputs=[Input(tx_hash=input_tx_hash, output_id=0)], fee=Decimal('0'))
        tx.validate()

def test_validate_fails_input_output_mismatch(key_pair, valid_inputs_outputs, recipient_address):
    inputs, _ = valid_inputs_outputs
    outputs = [Output(recipient=recipient_address, amount=Decimal('5'))]  # Less than inputs
    tx = Transaction(inputs=inputs, outputs=outputs, fee=Decimal('4'))  # Fee makes it not equal
    tx.sign(key_pair)

    with pytest.raises(TransactionValidationError, match="Input totals must equal output totals plus transaction fee."):
        tx.validate()

def test_validate_fails_bad_signature(key_pair, valid_inputs_outputs):
    inputs, outputs = valid_inputs_outputs
    tx = Transaction(inputs=inputs, outputs=outputs, fee=Decimal('0'))
    tx.hash()  # Generate the proof
    tx.signature = "bad_signature"  # Invalid signature
    tx.pubkey = key_pair.pub.data

    with pytest.raises(TransactionValidationError, match="Signature verification failed."):
        tx.validate()
