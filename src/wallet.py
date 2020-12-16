from typing import List, Union

from base58 import b58encode

from crypto.chicken import chicken_hash
from keys import KeyPair
from node import Node


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
    def generate(cls, key: KeyPair, prefix="0x"):
        if hasattr(key, "pub"):
            cls.pubkey = key.pub

        pub = chicken_hash(cls.pubkey).hexdigest()

        cls.prefix = prefix
        cls.addr = pub[38:]
        cls.checksum = b58encode(cls.addr.encode("ascii"))[:4].decode().lower()
        return cls()


class Wallet:
    node: Node
    aliases: List[str]
    addresses: List[Union[str, KeyPair]]

    def __init__(self, node, aliases=[], addresses=[]):
        self.node = node
        self.aliases = aliases
        self.addresses = addresses

    def create_address(self, key: KeyPair):
        addr = Address.generate(key)
        if addr not in self.addresses:
            self.addresses.append(addr)

    def __repr__(self):
        return f"<Wallet(node: {self.node}, aliases: {self.aliases}, addresses: {self.addresses})>"


if __name__ == "__main__":
    node = Node()
    keys = KeyPair.new()
    wallet = Wallet(node)
    wallet.create_address(keys)
    print(repr(wallet))
