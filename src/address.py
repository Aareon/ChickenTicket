from base58 import b58encode

from crypto.chicken import chicken_hash
from keys import KeyPair


class Address:
    LENGTH: int = 32
    pubkey: str
    prefix: str
    addr: str
    checksum: str

    def __init__(self, key: KeyPair = None, address=None):
        if key is None and address is None:
            return
        if hasattr(key, "pub"):
            self.pubkey = key.pub

        elif isinstance(key, str):
            self.pubkey = key

        if isinstance(address, str) and len(address) == self.LENGTH:
            self.prefix = address[:1]
            self.addr = address[1:28]
            self.checksum = address[28:]
        else:
            raise Exception(
                f"invalid address {address} length {len(address)}. Address must be a `str` and {self.LENGTH} characters. Use Address.new(pubkey, prefix) to generate a new address")

    def __repr__(self):
        return f'<Address("{str(self)}")>'

    def __str__(self):
        return f"{self.prefix}{self.addr}{self.checksum}"

    @classmethod
    def new(cls, kp: KeyPair, prefix="0x"):
        if hasattr(kp, "pub"):
            cls.pubkey = kp.pub

        pub = chicken_hash(cls.pubkey.data).hex()

        cls.prefix = prefix
        cls.addr = pub[38:]
        cls.checksum = b58encode(cls.addr.encode())[:4].decode().lower()
        return cls()


if __name__ == "__main__":
    kp = KeyPair.new()
    a1 = Address.new(kp)
    print(a1, "| length", len(str(a1)))
