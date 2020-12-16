from dataclasses import dataclass
from typing import List
from transaction import Transaction


@dataclass
class MempoolTx:
    tx: Transaction
    confirmations: int


class Mempool:
    transactions: List[MempoolTx]
    limit: int
    def __init__(self, limit=10):
        self.transactions = []
        self.limit = limit

    def add_transaction(self, tx):
        if len(self.transactions) + 1 > self.limit:
            return None

        mem_tx = MempoolTx(tx, 0)
        self.transactions.append(mem_tx)
        return mem_tx

    def confirm_transaction(self, tx):
        try:
            idx = [m.tx for m in self.transactions].index(tx)
        except ValueError:
            idx = None

        if idx is not None:
            self.transactions[idx].confirmations += 1
            return True
        return False

    def __str__(self):
        return f"Mempool(transactions: {self.transactions}, limit: {self.limit})>"
