from dataclasses import dataclass

import ecdsa

CURVE = ecdsa.SECP256k1


@dataclass
class PubKey:
    data: str

    def __init__(self, data):
        self.data = data.hex()

    def __str__(self):
        return self.data.hex()


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
        if hasattr(cls, "pub") or hasattr(cls, "priv"):
            raise Exception("Can not use KeyPair.new() on existing KeyPair")

        sk = ecdsa.SigningKey.generate(curve=CURVE)
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
