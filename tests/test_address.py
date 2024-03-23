import sys
import os

sys.path.append(os.path.abspath('src'))
from address import Address
from keys import KeyPair, PubKey, PrivKey

def test_address_generation():
    # Assuming you have a way to generate or specify a deterministic KeyPair
    # For the sake of example, let's pretend we can directly use a known public key
    known_pub_key = PubKey(data=b'known_public_key_bytes')
    known_priv_key = PrivKey(data=b'known_private_key_bytes')
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


def test_address_from_private_key_string():
    # Known private key string (hexadecimal)
    known_priv_key_str = "f00e54641c1f57cc9e727ff83fa36b17b9c2f93aceb2b043e0a6b79015f50f27"
    
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
    assert len(str(address)) == Address.LENGTH, "Total address length does not match expected value"
