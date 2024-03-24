import time
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

import ecdsa

try:
    import ujson as json
except ImportError:
    import json

from address import Address
from crypto.chicken import chicken_hash
from config import Config
from keys import KeyPair
from validator import TransactionValidator


@dataclass
class TXVersion:
    """Defines transaction version constants."""

    ver1: int = 0x1
    ver2: int = 0x2
    ver3: int = 0x3


@dataclass
class Input:
    """
    Represents an input in a transaction, referring to a previous transaction's output.

    Attributes:
        tx_hash (str): The hash of the previous transaction.
        output_id (int): The index of the output in the previous transaction.
    """

    tx_hash: str
    output_id: int

    def to_dict(self) -> dict:
        """Converts the Input instance into a dictionary."""
        return {"tx": self.tx_hash, "idx": self.output_id}


@dataclass
class Output:
    """
    Represents an output in a transaction, specifying a recipient and an amount.

    Attributes:
        recipient (Address): The address of the recipient.
        amount (Decimal): The amount to be sent to the recipient.
    """

    recipient: Address
    amount: Decimal

    def to_dict(self) -> dict:
        """Converts the Output instance into a dictionary."""
        return {"recipient": str(self.recipient), "amount": str(self.amount)}


class Transaction:
    """
    Represents a transaction in the blockchain.

    Attributes:
        idx (int): The index of the transaction.
        ver (TXVersion): The version of the transaction.
        timestamp (int): The timestamp of the transaction.
        inputs (List[Input]): A list of inputs for the transaction.
        outputs (List[Output]): A list of outputs for the transaction.
        fee (Decimal): The transaction fee.
        proof (Optional[str]): The hash of the transaction.
        signature (Optional[str]): The signature of the transaction.
        pubkey (Optional[bytes]): The public key associated with the transaction.
    """

    def __init__(self, **kwargs):
        self.idx: int = kwargs.get("idx", 0)
        self.ver: TXVersion = kwargs.get("ver", TXVersion.ver1)
        self.timestamp: int = kwargs.get("timestamp", int(time.time()))
        self.inputs: List[Input] = kwargs.get("inputs", [])
        self.outputs: List[Output] = kwargs.get("outputs", [])
        self.fee: Decimal = kwargs.get("fee", Decimal("0"))
        self.proof: Optional[str] = kwargs.get("proof")
        self.signature: Optional[str] = kwargs.get("signature")
        self.pubkey: Optional[bytes] = kwargs.get("pubkey")

        self.validator = TransactionValidator()
    
    def __str__(self) -> str:
        """Returns the JSON representation of the transaction."""
        return json.dumps(self.to_dict(), sort_keys=True)

    def add_input(self, input: Input):
        """
        Adds an input to the transaction.

        Args:
            input (Input): The input to add to the transaction.
        """
        self.inputs.append(input)

    def add_output(self, output: Output):
        """
        Adds an output to the transaction.

        Args:
            output (Output): The output to add to the transaction.
        """
        self.outputs.append(output)
    
    def get_all_transactions(self):
        transactions_list = []

        def _traverse_node(node_prefix):
            node = self.transactions.traverse(node_prefix)

            # If it's a leaf node, decode and append the transaction
            if node.is_leaf:
                # Assuming transaction data is stored directly at leaves
                transactions_list.append(json.loads(node.value.decode()))
            else:
                # Otherwise, recursively traverse through sub-segments (children)
                for sub_segment in node.sub_segments:
                    _traverse_node(node_prefix + sub_segment)

        # Start traversal from the root
        _traverse_node(())
        return transactions_list

    def to_dict(self) -> dict:
        """Converts the Transaction instance into a dictionary."""
        return {
            "idx": self.idx,
            "ver": self.ver,
            "time": self.timestamp,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "outputs": [out.to_dict() for out in self.outputs],
            "fee": str(self.fee),
            "proof": self.proof,
            "signature": self.signature,
            "pubkey": self.pubkey.hex() if self.pubkey else None,
        }
    
    def json(self) -> str:
        """Serializes the transaction to a JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)

    def hash(self) -> str:
        """Calculates and returns the hash of the transaction."""
        self.proof = chicken_hash(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hex()
        return self.proof

    def sign(self, key: KeyPair):
        """
        Signs the transaction using a given KeyPair.

        Args:
            key (KeyPair): The KeyPair to sign the transaction with.

        Returns:
            The signature as a hexadecimal string.
        """
        if self.proof is None:
            self.hash()
        sk = ecdsa.SigningKey.from_string(key.priv.data, curve=Config.CURVE)
        self.signature = sk.sign(json.dumps(self.to_dict()).encode("utf-8")).hex()
        self.pubkey = key.pub.data
        return self.signature
