from dataclasses import dataclass
from pathlib import Path

from ecdsa import SECP256k1


@dataclass
class Config:
    CURVE = SECP256k1
    DEFAULT_WALLET_FP = Path(__file__).parent.parent / "wallet.der"
    MAGIC = "\xDapper\x00".encode(
        "utf-8"
    )  # We intercept the traffic if it starts with these bytes
    TESTNET = True
