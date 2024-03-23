import os
import sys

import pytest

sys.path.append(os.path.abspath("src"))
from address import Address
from keys import KeyPair, PrivKey, PubKey


def test_address_generation():
    # Assuming you have a way to generate or specify a deterministic KeyPair
    # For the sake of example, let's pretend we can directly use a known public key
    known_pub_key = PubKey(data=b"known_public_key_bytes")
    known_priv_key = PrivKey(data=b"known_private_key_bytes")
    kp = KeyPair(pub=known_pub_key, priv=known_priv_key)

    # Generate address
    address = Address.new(kp)

    # Expected values based on the deterministic input
    expected_prefix = "0x"
    expected_addr = "4971ed9095380762d78de5af41"
    expected_checksum = "EXfh"

    # Assertions
    assert address.prefix == expected_prefix
    assert address.addr == expected_addr
    assert address.checksum == expected_checksum
    assert len(str(address)) == Address.LENGTH


def test_address_constructor_and_serialization():
    # Test valid KeyPair initialization
    key_pair = KeyPair.new()
    address_from_key = Address.new(key_pair)
    assert isinstance(
        address_from_key, Address
    ), "Address object was not created from KeyPair."

    # Serialize to string
    address_str = str(address_from_key)
    assert isinstance(address_str, str), "Serialization did not produce a string."
    assert len(address_str) == Address.LENGTH, "Serialized address has incorrect length."

    # Test initialization from a valid address string
    try:
        address_from_str = Address(address=address_str)
    except ValueError:
        pytest.fail(
            "Constructor raised ValueError unexpectedly for valid address string."
        )

    # Ensure deserialized object matches the original
    assert (
        address_from_str.addr == address_from_key.addr
    ), "Deserialized address does not match original."
    assert (
        address_from_str.prefix == address_from_key.prefix
    ), "Prefix mismatch after deserialization."
    assert (
        address_from_str.checksum == address_from_key.checksum
    ), "Checksum mismatch after deserialization."

    # Test initialization with invalid inputs
    with pytest.raises(ValueError):
        Address()  # Neither key nor address provided

    with pytest.raises(ValueError):
        Address(address="invalid_length")  # Invalid address length

    with pytest.raises(ValueError):
        addr = f"0x{'1' * (Address.LENGTH - 2)}"
        Address(
            address=addr
        )  # Correct length but likely invalid checksum


def test_invalid_address_deserialization():
    invalid_address_str = "0x1234567890"  # Incorrect length
    with pytest.raises(ValueError, match=f"must be {Address.LENGTH} characters long."):
        Address(address=invalid_address_str)

    # Assuming '0x1234abcd' is an example of an invalid address format for your application
    invalid_checksum_address = "0x" + "1" * (Address.LENGTH - 6) + "abcd"  # Correct length but incorrect checksum
    with pytest.raises(ValueError, match="checksum"):
        Address(address=invalid_checksum_address)


def test_address_from_private_key_string():
    # Known private key string (hexadecimal)
    known_priv_key_str = (
        "f00e54641c1f57cc9e727ff83fa36b17b9c2f93aceb2b043e0a6b79015f50f27"
    )

    # Generate KeyPair from the known private key string
    kp = KeyPair.from_privkey_str(known_priv_key_str)

    # Generate Address from the KeyPair
    address = Address.new(kp)

    # Expected values based on the deterministic private key string
    expected_prefix = "0x"  # Adjust as needed
    expected_addr = "e352b1bec5cb7fcf1f71230351"  # Adjust as needed
    expected_checksum = "2RxL"  # Adjust as needed

    # Assertions to verify the address components
    assert address.prefix == expected_prefix, "Prefix does not match expected value"
    assert address.addr == expected_addr, "Address part does not match expected value"
    assert address.checksum == expected_checksum, "Checksum does not match expected value"
    assert (
        len(str(address)) == Address.LENGTH
    ), "Total address length does not match expected value"


def test_valid_address():
    """
    Test to ensure that an address generated from a deterministic key pair
    is correctly identified as valid.
    """
    # Generate a deterministic KeyPair from a predefined seed
    seed = "a fixed seed value for testing"
    kp = KeyPair.from_seed(seed)

    # Generate an address from the deterministic KeyPair
    address = Address.new(kp)
    address_str = str(address)

    # Validate the generated address
    is_valid = Address.is_valid_address(address_str)
    assert is_valid, f"Address: {address_str} was incorrectly identified as invalid."


def test_invalid_address():
    # Assuming '0x1234abcd' is an example of an invalid address format for your application
    invalid_address = "0x1234abcd"  # Incorrect length and potentially incorrect checksum

    # Validate the incorrect address
    assert not Address.is_valid_address(
        invalid_address
    ), "Invalid address was incorrectly identified as valid."


def test_address_boundary_conditions():
    """
    Test addresses at various boundary conditions to ensure the address validation
    correctly identifies valid and invalid addresses.
    """
    # Generate a deterministic KeyPair from a predefined seed
    seed = "a fixed seed value for testing"
    kp = KeyPair.from_seed(seed)

    # Generate address from KeyPair
    address = Address.new(kp)
    address_str = str(address)

    # Test 1: Altering the last character (assumed to affect checksum)
    altered_checksum_address = address_str[:-1] + "x"
    assert not Address.is_valid_address(
        altered_checksum_address
    ), "Address with altered checksum incorrectly passed validation."

    # Test 2: Incorrect prefix but correct length and checksum
    invalid_prefix_address = (
        "1Y" + address_str[2:]
    )  # Replace the prefix with an invalid one
    assert not Address.is_valid_address(
        invalid_prefix_address
    ), "Address with incorrect prefix incorrectly passed validation."

    # Test 3: Correct prefix and checksum but one character too short
    short_address = address_str[:-1]
    assert not Address.is_valid_address(
        short_address
    ), "Shortened address incorrectly passed validation."

    # Test 4: Correct prefix and checksum but one character too long
    long_address = address_str + "f"
    assert not Address.is_valid_address(
        long_address
    ), "Lengthened address incorrectly passed validation."
