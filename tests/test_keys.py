import os
import sys

import ecdsa
import pytest

sys.path.append(os.path.abspath("src"))
from keys import PrivKey, PubKey, KeyPair

def test_keypair_generation():
    key_pair = KeyPair.new()
    assert isinstance(key_pair.pub, PubKey), "Public key is not an instance of PubKey."
    assert isinstance(key_pair.priv, PrivKey), "Private key is not an instance of PrivKey."

def test_deterministic_keypair_generation():
    seed = "test seed"
    key_pair1 = KeyPair.from_seed(seed)
    key_pair2 = KeyPair.from_seed(seed)
    assert key_pair1.pub.data == key_pair2.pub.data, "Public keys do not match for the same seed."
    assert key_pair1.priv.data == key_pair2.priv.data, "Private keys do not match for the same seed."

def test_keypair_from_private_key():
    priv_key_str = "4f3c63a196d5085b598f0d3dd5ac39b2dd953ac559fa2171cd6a62d0f4329574"
    key_pair = KeyPair.from_privkey_str(priv_key_str)
    expected_pub_key = ecdsa.SigningKey.from_string(bytes.fromhex(priv_key_str), curve=ecdsa.SECP256k1).get_verifying_key().to_string()
    assert key_pair.pub.data == expected_pub_key, "Public key does not match expected value derived from private key."

def test_pubkey_privkey_hex_representation():
    key_pair = KeyPair.new()
    assert isinstance(key_pair.pub.__str__(), str), "Public key string representation is not a string."
    assert isinstance(key_pair.priv.__str__(), str), "Private key string representation is not a string."

def test_signing_and_validation():
    key_pair = KeyPair.new()
    data = b"test data"
    signature_hex = key_pair.sign(data)
    signature = bytes.fromhex(signature_hex)
    vk = ecdsa.VerifyingKey.from_string(key_pair.pub.data, curve=ecdsa.SECP256k1)
    assert vk.verify(signature, data), "Signature could not be verified with the public key."

def test_signing_with_invalid_data():
    key_pair = KeyPair.new()
    with pytest.raises(ValueError):
        key_pair.sign(b"")

@pytest.mark.parametrize("invalid_data", [None, "", 123])
def test_signing_with_unexpected_data_types(invalid_data):
    key_pair = KeyPair.new()
    with pytest.raises(ValueError):
        key_pair.sign(invalid_data)
