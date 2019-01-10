from Cryptodome.Hash import SHA256, BLAKE2b, keccak
from Cryptodome.Util.py3compat import bord

import groestlcoin_hash


class Groestl:
    """ An almost compliant hashlib-like wrapper for the
    Groestl hashing algorithm"""
    __slots__ = ("data", "digest_bits", "hash",)

    def __init__(self):
        self.data = None
        self.digest_bits = None
        self.hash = None

    def new(self, data):
        self.data = data if isinstance(data, bytes) else data.encode("utf-8")
        self.digest_bits = len(data)
        self.hash = groestlcoin_hash.getHash(self.data, self.digest_bits)
        return self
    
    def digest(self):
        return self.hash
    
    def hexdigest(self):
        return "".join(["%02x" % bord(x) for x in self.digest()])
        

def chicken_hash(data: bytes):
    """Hash some data with the chicken algorithm chain

    Args:
        data (bytes)
            The bytes-like data to be hashed
    
    Returns:
        A :class:`Keccak_Hash` hash object
    """
    a = BLAKE2b.new(data=data, digest_bits=256).digest()
    b = keccak.new(data=a, digest_bits=256).digest()
    c = Groestl().new(b).digest()
    return keccak.new(data=c, digest_bits=256)


if __name__ == "__main__":
    print(chicken_hash('test'.encode('utf-8')).hexdigest())
