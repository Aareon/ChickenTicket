from hashlib import blake2b as BLAKE2b
from hashlib import sha3_256 as keccak
        

def chicken_hash(data: bytes):
    """Hash some data with the chicken algorithm chain

    Args:
        data (bytes)
            The bytes-like data to be hashed
    
    Returns:
        A :class:`Keccak_Hash` hash object
    """
    a = BLAKE2b(data).digest()
    b = keccak(a).digest()
    return keccak(b)


if __name__ == "__main__":
    print(chicken_hash(bytes("test", encoding="utf-8").hexdigest())
