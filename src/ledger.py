import logging

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, filename="wallet.log", format='%(asctime)s %(message)s') # include timestamp

Base = declarative_base()

class Ledger(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, nullable=False)
    height = Column(Integer, nullable=False)
    timestamp = Column(Integer, nullable=False)
    address = Column(String(length=64), nullable=False)
    recipient = Column(String(length=64), nullable=False)
    amount = Column(Integer, nullable=False)
    signature = Column(String, nullable=False) # signing key used to sign the transaction (PKCS1_v1_5)
    public_key = Column(String(length=88), nullable=False)
    block_hash = Column(String, nullable=False, unique=True)
    fee = Column(Integer, nullable=False)
    reward = Column(Integer, nullable=False)

    def __repr__(self):
        return '<Transaction(id=\'{}\', height=\'{}\', timestamp=\'{}\', address=\'{}\', recipient=\'{}\', amount=\'{}\', signature=\'{}\', public_key=\'{}\', block_hash=\'{}\', fee=\'{}\', reward=\'{}\')>'.format(
            self.id, self.height, self.timestamp, self.address,
            self.recipient, self.amount, self.signature, self.public_key,
            self.block_hash, self.fee, self.reward
        )