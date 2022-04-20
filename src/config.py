from dataclasses import dataclass
from pathlib import Path

from ecdsa import SECP256k1


@dataclass
class Config:
    CURVE = SECP256k1
    DEFAULT_WALLET_FP = Path(__file__).parent.parent / "wallet.der"
