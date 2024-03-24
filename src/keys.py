from dataclasses import dataclass

import ecdsa
from ecdsa.util import randrange_from_seed__trytryagain

from .config import Config

CURVE = Config.CURVE


@dataclass
class PubKey:
    """
    Represents a public key in the system.

    Attributes:
        data (bytes): The binary data of the public key.
    """

    data: bytes

    def __str__(self) -> str:
        """Returns the hexadecimal string representation of the public key."""
        return self.data.hex()


@dataclass
class PrivKey:
    """
    Represents a private key in the system.

    Attributes:
        data (bytes): The binary data of the private key.
    """

    data: bytes

    def __str__(self) -> str:
        """Returns the hexadecimal string representation of the private key."""
        return self.data.hex()


@dataclass
class KeyPair:
    """
    Represents a key pair consisting of a public and a private key.

    Attributes:
        pub (PubKey): The public key part of the key pair.
        priv (PrivKey): The private key part of the key pair.
    """

    pub: PubKey
    priv: PrivKey

    @classmethod
    def new(cls) -> "KeyPair":
        """
        Generates a new key pair.

        Returns:
            KeyPair: A new KeyPair instance with a randomly generated public and private key.
        """
        sk = ecdsa.SigningKey.generate(curve=CURVE)
        priv = PrivKey(sk.to_string())
        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub=pub, priv=priv)

    @classmethod
    def from_privkey_str(cls, priv: str) -> "KeyPair":
        """
        Generates a key pair from a hexadecimal string representation of a private key.

        Args:
            priv (str): The hexadecimal string representation of the private key.

        Returns:
            KeyPair: A KeyPair instance generated from the provided private key.
        """
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(priv), curve=CURVE)
        priv = PrivKey(sk.to_string())
        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub=pub, priv=priv)

    @classmethod
    def from_seed(cls, seed: str) -> "KeyPair":
        """
        Generates a deterministic key pair based on a seed string.

        Args:
            seed (str): The seed string used to generate the key pair.

        Returns:
            KeyPair: A KeyPair instance generated deterministically from the given seed.
        """
        secexp = randrange_from_seed__trytryagain(seed, CURVE.order)
        sk = ecdsa.SigningKey.from_secret_exponent(secexp, curve=CURVE)
        priv = PrivKey(sk.to_string())
        vk = sk.get_verifying_key()
        pub = PubKey(vk.to_string())
        return cls(pub=pub, priv=priv)

    def __str__(self) -> str:
        """
        Returns a string representation of the KeyPair, hiding the private key.

        Returns:
            str: A string representation of the KeyPair with the private key redacted.
        """
        return f'<KeyPair(pub="{self.pub}", priv="[REDACTED]")>'

    def sign(self, data: bytes) -> str:
        """
        Signs a given data using the private key of the KeyPair.

        Args:
            data (bytes): The data to be signed.

        Returns:
            str: The hexadecimal string representation of the signature.

        Raises:
            ValueError: If the private key or data is missing.
        """
        if not self.priv:
            raise ValueError("Private key is missing.")
        if not data:
            raise ValueError("Data is invalid.")
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError("Data must be bytes-like.")

        sk = ecdsa.SigningKey.from_string(self.priv.data, curve=CURVE)
        signature = sk.sign(data)
        return signature.hex()


if __name__ == "__main__":
    kp = KeyPair.new()
    print(kp.priv)
    seed = "some secure and unique seed string"
    kp = KeyPair.from_seed(seed)
    print(f"Public Key: {kp.pub}")
    print(f"Private Key: {kp.priv}")
