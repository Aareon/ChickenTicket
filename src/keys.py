from dataclasses import dataclass

import ecdsa
from ecdsa.util import randrange_from_seed__trytryagain

from config import Config

CURVE = Config.CURVE


@dataclass
class PubKey:
    data: str

    def __init__(self, data):
        self.data = data.hex()

    def __str__(self):
        return self.data


@dataclass
class PrivKey:
    data: str

    def __init__(self, data):
        self.data = data.hex()

    def __str__(self):
        return self.data


@dataclass
class KeyPair:
    pub: PubKey
    priv: PrivKey

    @classmethod
    def new(cls):
        """Generates a new keypair
        TODO add support for deterministic keys"""
        if hasattr(cls, "pub") or hasattr(cls, "priv"):
            raise Exception("Can not use KeyPair.new() on existing KeyPair")

        sk = ecdsa.SigningKey.generate(curve=CURVE)
        priv = PrivKey(sk.to_string())

        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub, priv)

    @classmethod
    def from_privkey_str(cls, priv):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(priv), curve=CURVE)
        priv = PrivKey(sk.to_string())

        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub, priv)

    @classmethod
    def from_seed(cls, seed):
        secexp = randrange_from_seed__trytryagain(seed, CURVE.order)
        sk = ecdsa.SigningKey.from_secret_exponent(secexp, curve=CURVE)
        priv = PrivKey(sk.to_string())

        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub, priv)

    def __str__(self):
        # BEWARE MALICIOUS USE
        # return f'<Keypair(pub: "{str(self.pub)}", priv: "{str(self.priv)}")>'
        return self

    def sign(self, data: str):
        if not hasattr(self, "priv"):
            raise AttributeError("Can not sign using KeyPair (has no priv attribute)")

        if not data:
            raise Exception("Can not sign data. Data is invalid")

        sk = ecdsa.SigningKey.from_string(bytes.fromhex(str(self.priv)), curve=CURVE)
        sig = sk.sign(bytes(str(self), encoding="utf-8")).hex()
        return sig
