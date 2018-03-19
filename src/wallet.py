import base64
import hashlib
import logging
import os
import sys

import ecdsa
from Cryptodome.PublicKey import RSA
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, filename="wallet.log", format='%(asctime)s %(message)s') # include timestamp

Base = declarative_base()

class Wallet(Base):
    """Represents a wallet"""
    __tablename__ = 'wallet'

    id = Column(Integer, primary_key=True, nullable=False)
    address = Column(String(length=64), nullable=False, unique=True)
    public_key = Column(String(length=88), nullable=False, unique=True)
    private_key = Column(String(length=64), nullable=False, unique=True)

    def __repr__(self):
        return '<Wallet(id=\'{}\', address=\'{}\', public_key=\'{}\', private_key=\'{}\')>'.format(
            self.id, self.address, self.public_key, self.private_key
        )


def generate_ECDSA_keys():
    """Generate and return new public and private keys using an ecdsa curve"""
    # Generate private key
    logging.info('Generating keys: curve=ecdsa.SECP256k1')
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) # signing key
    priv_key = sk.to_string().hex() # private key
    logging.info('Private key generated')
    
    # Generate public key
    vk = sk.get_verifying_key() # verifying key
    pk = vk.to_string().hex() # unencoded public key
    pub_key = base64.b64encode(bytes.fromhex(pk)) # encode `pk` to make it shorter
    logging.info('Public key generated, here it is; {}'.format(pub_key))
    
    return pub_key, priv_key


def generate_address(pub_key):
    """Generate an address from a bytes-like public key"""
    address = hashlib.sha256(pub_key).hexdigest()
    logging.info('Generated address. Here it is; {}'.format(address))
    return address


def load_wallet(password=''):
    logging.info('Creating wallet database engine...')
    try:
        engine = create_engine('sqlite:///wallet.db?check_same_thread=False', echo=False)
        logging.info('Loaded `wallet.db`')
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        return session
    except:
        logging.warning('Failed to load `wallet.db`, exiting...')
        sys.exit(1)
    

if __name__ == "__main__":
    print("ChickenTicket CLI")
    print("Find help at https://github.com/Aareon/chickenticket\n")

    # load wallet.db and get usable database session
    wallet = load_wallet()

    addresses = wallet.query(Wallet.address).all()
    if len(addresses) == 0:
        logging.info('Getting new public/private keys and address')
        # get public and private keys
        public_key, private_key = generate_ECDSA_keys()

        # generate an address from our public key
        address = generate_address(public_key)

        print('Public Key:', public_key)
        print('Private Key:', private_key)
        print('Address:', address, '\n')

        # save our public/private keys and address to `wallet.db`
        try:
            wallet.add(Wallet(address=address,
                              public_key=public_key,
                              private_key=private_key))
            wallet.commit()
            logging.info('Successfully stored new public/private keys and address in `wallet.db`')
        except:
            logging.warning('Failed to store "new" public/private keys and address in `wallet.db`')
            sys.exit(1)
