from hashlib import (
    blake2b as BLAKE2b,
    sha3_256 as Keccak,
)
        

def chicken_hash(data: bytes):
    """Hash some data with the chicken algorithm chain

    Args:
        data (bytes)
            The bytes-like data to be hashed
    
    Returns:
        A :class:`Keccak_Hash` hash object
    """
    a = BLAKE2b(data).digest()
    b = Keccak(a).digest()
    return Keccak(b)


if __name__ == "__main__":
    print(chicken_hash(b"test").hexdigest())
