from dataclasses import dataclass
import ecdsa
from crypto import hexdigest

CURVE = ecdsa.SECP256k1


@dataclass
class PubKey:
    data: str

    def __repr__(self):
        return str(self)

    def __str__(self):
        return hexdigest(self.data)


@dataclass
class PrivKey:
    data: str

    def __str__(self):
        return str(self.data)

@dataclass
class KeyPair:
    pub: PubKey
    priv: PrivKey

    @classmethod
    def new(cls):
        if hasattr(cls, "pub") or hasattr(cls, "priv"):
            raise Exception("Can not use KeyPair.new() on existing KeyPair")

        sk = ecdsa.SigningKey.generate(curve=CURVE)
        priv = PrivKey(sk.to_string().hex())

        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub, priv)

    def __str__(self):
        # BEWARE MALICIOUS USE
        return f'<Keypair(pub: "{self.pub}", priv: "{self.priv}")>'

    def sign(self, data: str):
        if not hasattr(self, "priv"):
            raise AttributeError("Can not sign using KeyPair (has no priv attribute)")

        if not data:
            raise Exception("Can not sign data. Data is invalid")

        sk = ecdsa.SigningKey.from_string(bytes.fromhex(str(self.priv)), curve=CURVE)
        sig = hexdigest(sk.sign(bytes(str(self), encoding="utf-8")))
        return sig
