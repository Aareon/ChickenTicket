from pathlib import Path
from typing import List

from keys import KeyPair
from node import Node
from address import Address


class Wallet:
    aliases: List
    addresses: List

    def __init__(self):
        self.aliases = []
        self.addresses = []

    def load_from_der(self, path: Path):
        """Load a wallet.der from filepath `path`"""
        with open(path, "r+") as f:
            dat = f.read()

    def save_to_der(self, path: Path):
        """Save a wallet.der to filepath `path`"""
        with open(path, "w+") as f:
            f.seek(0)
            # write keypair and seeds here
            f.truncate()

    def create_wallet_address(self, kp: KeyPair):
        address = Address.new(kp)
        self.addresses.append([address, kp])
        return address


if __name__ == "__main__":
    wall = Wallet()
    kp = KeyPair.new()
    wall.create_wallet_address(kp)
    print(wall.addresses)
