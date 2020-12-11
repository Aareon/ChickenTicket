import argparse
import sys
from decimal import Decimal, getcontext
from config import *

import ecdsa
from base58 import b58encode
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from crypto.chicken import chicken_hash
from ledger import Ledger, load_ledger
from mempool import Mempool, load_mempool

# set decimal precision
getcontext().prec = 8

# basic SQLAlchemy stuff
Base = declarative_base()


class Wallet(Base):
    """Represents a wallet"""

    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True, nullable=False)
    address = Column(String(length=64), nullable=False, unique=True)
    public_key = Column(String(length=88), nullable=False, unique=True)
    private_key = Column(String(length=64), nullable=False, unique=True)

    def __repr__(self):
        return f'<Wallet(id="{self.id}", address="{self.address}", public_key="{self.public_key}", private_key="{self.private_key}")>'


def generate_ECDSA_keys():
    """Generate and return new public and private keys using an ecdsa curve"""
    # Generate private key
    logger.info("Generating keys: curve=ecdsa.SECP256k1")
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)  # signing key
    private_key = sk.to_string().hex()  # private key
    logger.info("Private key generated")

    # Generate public key
    vk = sk.get_verifying_key()  # verifying key
    public_key = vk.to_string()
    logger.info(f"Public key generated: {public_key}")

    return public_key, private_key


def generate_address(public_key):
    """Generate an address from a bytes-like public key"""
    pub_hash = chicken_hash(public_key)

    # create the address w/o the byte checksum and the prefix
    address_hash = pub_hash.hexdigest()[38:]

    # create the checksum of the address by hashing the address again,
    # encoding the result, and taking the last 4 of the encoding
    checksum = b58encode(address_hash.encode("ascii"))[:4]
    print(checksum)
    address = f"0x{address_hash}{checksum.decode().lower()}"
    logger.info(f"Generated address: {address}")
    return address


def is_address(address):
    if len(address) != 32:
        return False

    if not address.startswith("0x"):
        return False

    address = address.replace("0x", "")
    address_checksum = address[-4:]
    checksum = b58encode(address[:-4].encode("ascii"))[:4].decode().lower()
    return address_checksum == checksum


def load_wallet(password=""):
    logger.info(f"Creating wallet database engine... {DATA_DIR / 'wallet.db'}")
    try:
        engine = create_engine(
            f"sqlite:///{DATA_DIR / 'wallet.db'}?check_same_thread=False", echo=False
        )
        logger.info("Loaded `wallet.db`")
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        return session
    except:
        logger.warning(f"Failed to load {DATA_DIR / 'wallet.db'}, exiting...")
        sys.exit(1)


def get_balance(wallet, ledger):
    addresses = wallet.query(Wallet.address).all()

    balance = 0
    ledger_state = True
    try:
        for address in addresses:
            transactions = (
                ledger.query(Ledger.amount).filter_by(recipient=address[0]).all()
            )
            for amount in transactions:
                balance += amount[0]
    except Exception as e:
        logger.warning("Failed to load ledger. Exiting...")
        logger.error(f"{type(e).__name__}: {e}")
        ledger_state = False
        pass

    return balance, ledger_state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pure Python implementation of a cryptocurrency blockchain"
    )
    parser.add_argument(
        "-key",
        "-K",
        help="Prints private key. (Don not do this unless you know what you are doing!)",
        action="store_true",
    )
    parser.add_argument(
        "--newaddress",
        "-N",
        help="Generates a new address, public key, and private key",
        action="store_true",
    )
    parser.add_argument(
        "--addnode",
        "-A",
        help="Adds a node to peers list for this instance",
        action="store_true",
    )
    args = parser.parse_args()

    print("ChickenTicket CLI")
    print("Find help at https://github.com/Aareon/chickenticket\n")

    # load wallet.db and get usable database session
    wallet = load_wallet()

    # load mempool.db (unconfirmed txs) for later
    mempool = load_mempool()

    addresses = wallet.query(Wallet.address).all()
    if len(addresses) == 0 or args.newaddress:
        logger.info("Getting new public/private keys and address")
        # generate public and private keys
        public_key, private_key = generate_ECDSA_keys()

        # generate an address from our public key
        address = generate_address(public_key)

        # save our public/private keys and address to `wallet.db`
        try:
            wallet.add(
                Wallet(address=address, public_key=public_key, private_key=private_key)
            )
            wallet.commit()
            logger.info(
                "Successfully stored new public/private keys and address in `wallet.db`"
            )
        except Exception as e:
            logger.warning(
                "Failed to store new public/private keys and address in `wallet.db`"
            )
            logger.error(f"{type(e).__name__}: {e}")
            sys.exit(1)
    # if wallet already has an address
    else:
        # get the already existing key pair from the wallet, but only the most recently made
        public_key, private_key, address = wallet.query(
            Wallet.public_key, Wallet.private_key, Wallet.address
        ).all()[0]
        print(f"Public Key: {public_key}")

    # if user requests to see private key
    if args.key:
        print(f"Private Key: {wallet.private_key}")

    print(f"Address: {address}")
    print(f"Address is valid: {is_address(address)}\n")

    ledger = load_ledger()
    balance = 0
    ledger_state = False
    try:
        balance, ledger_state = get_balance(wallet, ledger)
    except TypeError as e:
        print(get_balance(wallet, ledger))

    print(f"Balance: {Decimal(balance / 100000000)} CHKN")

    if not ledger_state:
        print("Ledger not present/synced")
    else:
        print("Ledger is present/synced")
