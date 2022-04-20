from pathlib import Path
from typing import List

from keys import KeyPair
from address import Address


class Wallet:
    aliases: List
    addresses: List

    def __init__(self):
        self.aliases = []
        self.addresses = []

    def load_from_der(self, path: Path):
        """Load a wallet.der from filepath `path`
        wallet.der contains a list of private keys

        TODO add encryption"""
        privs = []
        with open(path, "r+") as f:
            privs = f.read().splitlines()
        
        # using loaded priv keys, generate addresses associated with them
        # this requires recreating the KeyPair first
        kps = []
        for priv in privs:
            kps.append(KeyPair.from_privkey_str(priv))

        # generate the addresses list,
        # joining the keypair as the 2nd element for ease of use
        for kp in kps:
            self.addresses.append([Address.new(kp), kp])
        
        return self

    def save_to_der(self, path: Path):
        """Save a wallet.der to filepath `path`
        Overwrites file with new data
        TODO add encryption"""
        with open(path, "w+") as f:
            f.seek(0)
            for addy in self.addresses:
                kp = addy[1]  # keypair is stored in a list w owning address
                f.write(kp.priv.data + "\n")
            f.truncate()

    def create_wallet_address(self, kp: KeyPair):
        address = Address.new(kp)
        self.addresses.append([address, kp])
        return address


if __name__ == "__main__":
    wall1 = Wallet()
    kp = KeyPair.new()
    wall1.create_wallet_address(kp)
    #print(wall1.addresses)

    wallet_fp = Path(__file__).parent.parent / "wallet.der"
    #print(wallet_fp)
    wall1.save_to_der(wallet_fp)

    wall2 = Wallet()
    wall2.load_from_der(wallet_fp)
    #print(wall2.addresses)

    print("Wallet1:", wall1.addresses)
    print("Wallet2:", wall2.addresses)
