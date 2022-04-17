import logging

# set up logger
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(message)s"
)  # include timestamp

try:
    # C ext modules
    from Cryptodome.Hash import SHA3_256, BLAKE2s

    USING_CRYPTODOME = True
except ImportError:
    # built-in
    from hashlib import (
        sha3_256,
        blake2s,
    )

    USING_CRYPTODOME = False


if USING_CRYPTODOME:

    def chicken_hash(data: bytes):
        """Hash some data with the chicken algorithm chain

        Args:
            data (bytes)
                The bytes-like data to be hashed

        Returns:
            bytes-like hash
        """
        return SHA3_256.new(data=BLAKE2s.new(data=data).digest()).digest()

else:

    def chicken_hash(data: bytes):
        return sha3_256(blake2s(data).digest()).digest()


if __name__ == "__main__":
    # test stuff
    from binascii import hexlify

    lib = "hashlib"
    if USING_CRYPTODOME:
        lib = "pycryptodomex"

    logging.debug(f"Using {lib}")

    data = b"chicken_hash_test"
    try:
        proof = chicken_hash(data)
        proof_hex = hexlify(chicken_hash(data))
        assert (
            proof_hex
            == b"5c93a073bb49ccdb82f0df269a91eba9d15d707ff98580cdefc5fd96b3022a90"
        )
    except AssertionError:
        logging.error("Test failed!")
    finally:
        logging.debug(proof_hex)

    logging.info("Tests done!")
