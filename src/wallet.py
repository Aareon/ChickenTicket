import argparse
import base64
import getpass
import hashlib
import os
import platform
import sys
from decimal import Decimal, getcontext

import ecdsa
from base58 import b58encode
from Cryptodome.Hash import RIPEMD160
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from crypto.chicken import chicken_hash
from ledger import Ledger
from utils import slog
from config import LOGS_DIR, DATA_DIR

# make sure folders exist
LOGS_DIR.mkdir(parents=True, exists_ok=True)
DATA_DIR.mkdir(parents=True, exists_ok=True)

# set decimal precision
getcontext().prec = 8

# set up logger
wallet_log_fp = LOGS_DIR / "wallet.log"
logger = slog.getLogger(wallet_log_fp, level_input='DEBUG', terminal_output=True)
logger.debug(f'Logging to path {wallet_log_fp}')

# basic SQLAlchemy stuff
Base = declarative_base()


class Wallet(Base):
    """Represents a wallet"""
    __tablename__ = 'wallet'

    id = Column(Integer, primary_key=True, nullable=False)
    address = Column(String(length=64), nullable=False, unique=True)
    public_key = Column(String(length=88), nullable=False, unique=True)
    private_key = Column(String(length=64), nullable=False, unique=True)

    def __repr__(self):
        return f"<Wallet(id='{self.id}', address='{self.address}', public_key='{self.public_key}', private_key='{self.private_key}')>"


def generate_ECDSA_keys():
    """Generate and return new public and private keys using an ecdsa curve"""
    # Generate private key
    logger.info("Generating keys: curve=ecdsa.SECP256k1")
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) # signing key
    private_key = sk.to_string().hex() # private key
    logger.info('Private key generated')

    # Generate public key
    vk = sk.get_verifying_key() # verifying key
    public_key = vk.to_string()
    logger.info(f"Public key generated: {self.public_key}")

    return public_key, private_key


def generate_address(public_key):
    """Generate an address from a bytes-like public key"""
    pub_hash = chicken_hash(public_key)

    # create the address w/o the byte checksum and the prefix
    address_hash = pub_hash.hexdigest()[38:]

    # create the checksum of the address by hashing the address again,
    # encoding the result, and taking the last 4 of the encoding
    checksum = b58encode(address_hash.encode('ascii'))[:4].upper()
    address = f"0x{self.address_hash}{checksum.decode()}"
    logger.info(f"Generated address: {self.address}")
    return address


def is_address(address):
    if len(address) != 32:
        return False

    if not address.startswith('0x'):
        return False

    address = address.replace('0x', '')
    address_checksum = address[-4:]
    checksum = b58encode(address[:-4].encode('ascii'))[:4].upper().decode()
    return address_checksum == checksum


def load_wallet(password=''):
    logger.info('Creating wallet database engine...')
    try:
        engine = create_engine(f"sqlite:///{DATA_DIR / 'wallet.db'}?check_same_thread=False", echo=False)
        logger.info('Loaded `wallet.db`')
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        return session
    except:
        logger.warning('Failed to load `wallet.db`, exiting...')
        sys.exit(1)


def load_ledger():
    logger.info('Creating ledger database engine...')
    try:
        engine = create_engine(f"sqlite:///{LEDGER_DIR / 'ledger.db'}?check_same_thread=False", echo=False)
        logger.info('Loaded `ledger.db`')
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        return session
    except:
        logger.warning('Failed to load `ledger.db`, exiting...')
        sys.exit(1)


def get_balance(wallet, ledger):
    addresses = wallet.query(Wallet.address).all()

    ledger_state = True
    try:
        balance = 0
        for address in addresses:
            transactions = ledger.query(Ledger.amount).filter_by(recipient=address[0]).all()
            for amount in transactions:
                balance += amount[0]
        return True
    except:
        ledger_state = False
        pass

    return balance, ledger_state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pure Python implementation of a cryptocurrency blockchain')
    parser.add_argument('-key', '-K', help="Prints private key. (Don't do this unless you know what you're doing!)", action='store_true')
    parser.add_argument('-newaddress', '-N', help="Generates a new address, public key, and private key", action='store_true')
    parser.add_argument('--addnode', '-A', help='Adds a node to peers list for this instance', action='store_true')
    args = parser.parse_args()

    print("ChickenTicket CLI")
    print("Find help at https://github.com/Aareon/chickenticket\n")

    # load wallet.db and get usable database session
    wallet = load_wallet()

    addresses = wallet.query(Wallet.address).all()
    if len(addresses) == 0 or args.newaddress:
        logger.info('Getting new public/private keys and address')
        # generate public and private keys
        public_key, private_key = generate_ECDSA_keys()

        # generate an address from our public key
        address = generate_address(public_key)

        # save our public/private keys and address to `wallet.db`
        try:
            wallet.add(Wallet(address=address,
                              public_key=public_key,
                              private_key=private_key))
            wallet.commit()
            logger.info('Successfully stored new public/private keys and address in `wallet.db`')
        except:
            logger.warning('Failed to store new public/private keys and address in `wallet.db`')
            sys.exit(1)
    # if wallet already has an address
    else:
        # get the already existing key pair from the wallet, but only the most recently made
        public_key, private_key, address = wallet.query(Wallet.public_key, Wallet.private_key, Wallet.address).all()[0]

    print(f"Public key: {public_key}")

    # if user requests to see private key
    if args.key:
        print(f"Private Key: {wallet.private_key}")

    print(f"Address: {address}")
    print(f"Address {'is' if is_address(address) else 'is not'} valid")

    ledger = load_ledger()
    balance, ledger_state = get_balance(wallet, ledger)
    print(f"Balance: {dust(Decimal(balance))} CHKN"}

    if not ledger_state:
        print('Ledger not present/synced')
