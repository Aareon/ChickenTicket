from dataclasses import dataclass
import ecdsa
from ecdsa.util import randrange_from_seed__trytryagain
from config import Config

CURVE = Config.CURVE

@dataclass
class PubKey:
    data: bytes

    def __str__(self):
        return self.data.hex()

@dataclass
class PrivKey:
    data: bytes

    def __str__(self):
        return self.data.hex()

@dataclass
class KeyPair:
    pub: PubKey
    priv: PrivKey

    @classmethod
    def new(cls):
        """Generates a new keypair"""
        sk = ecdsa.SigningKey.generate(curve=CURVE)
        priv = PrivKey(sk.to_string())

        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub=pub, priv=priv)

    @classmethod
    def from_privkey_str(cls, priv: str):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(priv), curve=CURVE)
        priv = PrivKey(sk.to_string())

        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub=pub, priv=priv)

    @classmethod
    def from_seed(cls, seed: str):
        secexp = randrange_from_seed__trytryagain(seed, CURVE.order)
        sk = ecdsa.SigningKey.from_secret_exponent(secexp, curve=CURVE)
        priv = PrivKey(sk.to_string())

        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub=pub, priv=priv)

    def __str__(self):
        # Safely returning a descriptive representation
        return f'<KeyPair(pub="{self.pub}", priv="[REDACTED]")>'

    def sign(self, data: bytes) -> str:
        """Signs data using the private key."""
        if not self.priv or not data:
            raise ValueError("Private key is missing or data is invalid.")

        sk = ecdsa.SigningKey.from_string(self.priv.data, curve=CURVE)
        signature = sk.sign(data)
        return signature.hex()


if __name__ == "__main__":
    kp = KeyPair.new()
    print(kp.priv)
