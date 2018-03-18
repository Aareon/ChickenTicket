import logging

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, filename="wallet.log", format='%(asctime)s %(message)s') # include timestamp

Base = declarative_base()

class Mempool(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, nullable=False)
    timestamp = Column(Integer, nullable=False)
    address = Column(String(length=64), nullable=False)
    recipient = Column(String(length=64), nullable=False)
    amount = Column(Integer, nullable=False)
    signature = Column(String, nullable=False) # signing key used to sign the transaction (PKCS1_v1_5)
    public_key = Column(String(length=88), nullable=False)
    openfield = Column(String, nullable=True)

    def __repr__(self):
        return '<Transaction(id=\'{}\', timestamp=\'{}\', address=\'{}\', recipient=\'{}\', amount=\'{}\', signature=\'{}\', public_key=\'{}\', openfield=\'{}\')>'.format(
            self.id, self.timestamp, self.address, self.recipient,
            self.amount, self.signature, self.public_key, self.openfield
        )

def load_mempool():
    logging.info('Creating mempool database engine...')
    try:
        engine = create_engine('sqlite:///mempool.db?check_same_thread=False', echo=False)
        logging.info('Loaded `mempool.db`')
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        return session
    except:
        logging.warning('Failed to load `mempool.db`, exiting...')
        return None
