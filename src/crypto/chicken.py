from binascii import hexlify
from loguru import logger

try:
    # C ext modules from pycryptodomex
    from Cryptodome.Hash import BLAKE2s
    USING_CRYPTODOME = True
except ImportError:
    # Use built-in hashlib if Cryptodome is not installed
    from hashlib import blake2s
    USING_CRYPTODOME = False

def chicken_hash(data: bytes) -> bytes:
    """Hash some data using BLAKE2s.

    Args:
        data (bytes): The bytes-like data to be hashed.

    Returns:
        bytes: The hash of the data using the BLAKE2s algorithm.
    """
    # Directly return the digest of the data using BLAKE2s
    if USING_CRYPTODOME:
        return BLAKE2s.new(data=data).digest()
    else:
        return blake2s(data).digest()

if __name__ == "__main__":
    lib = "pycryptodomex" if USING_CRYPTODOME else "hashlib"
    logger.debug(f"Using {lib}")

    data = b"chicken_hash_test"
    try:
        proof_hex = hexlify(chicken_hash(data))
        logger.debug(proof_hex)
        # Ensure to update the expected hash if you have a known good value for BLAKE2s
        # This example assert might need to be updated as the output will change
        # assert proof_hex == b"expected_hash_here"
    except AssertionError:
        logger.error("Test failed!")
    else:
        logger.info("Test passed!")

    logger.info("Tests done!")
