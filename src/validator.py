import sys
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import ecdsa

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config import Config  # noqa: E402

if TYPE_CHECKING:
    from chain import Blockchain
    from transaction import Transaction


class TransactionValidationError(Exception):
    """Exception raised for errors in the transaction validation."""


class TransactionValidator:
    @staticmethod
    def validate_inputs_outputs(transaction, chain: "Blockchain"):
        """Validates that the transaction's inputs and outputs are correctly formed."""
        if not transaction.inputs or not transaction.outputs:
            raise TransactionValidationError(
                "Transaction must have at least one input and one output."
            )

        input_total = Decimal("0")
        for inp in transaction.inputs:
            referenced_output_amount = chain.fetch_output_amount(
                inp.tx_hash, inp.output_id
            )
            input_total += referenced_output_amount

        output_total = sum(out.amount for out in transaction.outputs)

        if input_total != output_total + transaction.fee:
            raise TransactionValidationError(
                "Input totals must equal output totals plus transaction fee."
            )

    @staticmethod
    def check_signature_validity(transaction: "Transaction"):
        """
        Verifies the transaction's signature against the public key and the transaction hash.

        Raises:
            TransactionValidationError: If the signature is invalid.
        """
        if not transaction.signature or not transaction.pubkey:
            raise TransactionValidationError("Transaction must be signed.")

        try:
            vk = ecdsa.VerifyingKey.from_string(transaction.pubkey, curve=Config.CURVE)
            vk.verify(bytes.fromhex(transaction.signature), transaction.hash().encode())
        except ecdsa.BadSignatureError:
            raise TransactionValidationError("Signature verification failed.")

    @staticmethod
    def validate(transaction: "Transaction", blockchain: "Blockchain") -> bool:
        """Validates a transaction against a blockchain and it's state."""
        try:
            TransactionValidator.validate_inputs_outputs(transaction, blockchain)
            TransactionValidator.check_signature_validity(transaction)
            return True
        except TransactionValidationError:
            return False
