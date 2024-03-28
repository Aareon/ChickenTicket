import sys
from pathlib import Path
from typing import Optional

from base58 import b58encode

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from crypto.chicken import chicken_hash  # noqa: E402
from keys import KeyPair  # noqa: E402


class Address:
    """
    Represents a cryptocurrency address, encapsulating the logic for address generation,
    representation, and validation.

    Attributes:
        LENGTH (int): The fixed length for a valid address including the prefix and checksum.
        pubkey (Optional[bytes]): The public key associated with the address, if any.
        prefix (str): The prefix part of the address.
        addr (str): The main part of the address.
        checksum (str): The checksum part of the address for validation.
    """

    LENGTH: int = 32

    def __init__(self, key: Optional[KeyPair] = None, address: Optional[str] = None):
        """
        Initializes an Address instance either from a keypair or a direct address string.

        Args:
            key (Optional[KeyPair]): A KeyPair object or None.
            address (Optional[str]): A direct address string or None.

        Raises:
            ValueError: If neither a key nor an address is provided, or if the provided
                        address does not match the expected length.
        """
        if key is None and address is None:
            raise ValueError("A key or an address must be provided.")

        self.pubkey: Optional[bytes] = None
        self.prefix: str = ""
        self.addr: str = ""
        self.checksum: str = ""

        if key is not None:
            # Ensure the key parameter is actually a KeyPair instance.
            if not isinstance(key, KeyPair):
                raise TypeError("key argument must be an instance of KeyPair.")
            self.pubkey = key.pub.data

        if address is not None:
            if len(address) != self.LENGTH:
                raise ValueError(
                    f"Address '{str(self)}' must be {self.LENGTH} characters long. Is {len(str(self))}"
                )

            self.prefix = address[:2]
            self.addr = address[2:-4]
            self.checksum = address[-4:]
            if not self.is_valid_address(str(self)):
                raise ValueError(f"Address '{str(self)}' checksum is invalid.")

    def __repr__(self) -> str:
        """Returns a string representation of the Address instance."""
        return f'<Address("{str(self)}")>'

    def __str__(self) -> str:
        """Returns the full address string."""
        return f"{self.prefix}{self.addr}{self.checksum}"

    @classmethod
    def new(cls, kp: KeyPair, prefix: str = "0x") -> "Address":
        """
        Generates a new Address instance from a KeyPair with an optional prefix.

        Args:
            kp (KeyPair): The KeyPair object from which to generate the address.
            prefix (str, optional): The prefix to prepend to the address. Defaults to "0x".

        Returns:
            Address: A new Address instance generated from the given KeyPair.
        """
        pub_bytes = kp.pub.data
        pub_hashed = chicken_hash(pub_bytes).hex()[:26]  # First 26 chars of the hash

        # Compute the checksum from the hashed public key
        checksum_bytes = chicken_hash(pub_hashed.encode())
        checksum = b58encode(checksum_bytes).decode()[
            :4
        ]  # First 4 chars of the base58-encoded hash

        addr = pub_hashed  # Use the hashed public key directly as the address part
        return cls(address=f"{prefix}{addr}{checksum}")

    @staticmethod
    def is_valid_address(address: str, expected_prefix: str = "0x") -> bool:
        """
        Validates a cryptocurrency address.

        Args:
            address (str): The address to validate.
            expected_prefix (str, optional): The expected prefix of the address. Defaults to "0x".

        Returns:
            bool: True if the address is valid, False otherwise.
        """
        if len(address) != Address.LENGTH or not address.startswith(expected_prefix):
            return False

        addr_part = address[len(expected_prefix) : -4]
        checksum_part = address[-4:]

        recomputed_checksum_bytes = chicken_hash(addr_part.encode())
        recomputed_checksum = b58encode(recomputed_checksum_bytes).decode()[:4]

        return checksum_part == recomputed_checksum


# Example usage
if __name__ == "__main__":
    kp = KeyPair.new()
    print(kp)
    print(kp.pub.data)
    a1 = Address.new(kp)
    print(a1, "| length", len(str(a1)))
    print(f"Address: {a1} | Valid: {Address.is_valid_address(str(a1))}")
