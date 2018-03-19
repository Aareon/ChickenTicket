import base64
import hashlib
import logging
import sys
import time

from Cryptodome.Hash import SHA256
import ecdsa

from wallet import Wallet, load_wallet
from ledger import Ledger, load_ledger

logging.basicConfig(level=logging.INFO, filename="wallet.log", format='%(asctime)s %(message)s') # include timestamp

def create_genesis_transaction(recipient, private_key):
    timestamp = int(time.time() * 10000000)

    # timestamp, address, recipient, amount, openfield
    transaction = {'timestamp': timestamp,
                   'address': 'genesis',
                   'recipient': recipient,
                   'amount': 100000000,
                   'openfield': 'genesis'}

    

    # signing key, will be used to sign the transaction and generate a signature
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)

    # hash the transaction and generate a signature from the hash
    hashed_transaction = SHA256.new(str(transaction).encode('utf-8')).hexdigest()
    signature = sk.sign(hashed_transaction.encode('utf-8'))
    encoded_signature = base64.b64encode(signature)

    block_hash = hashlib.sha256(str((timestamp, transaction)).encode('utf-8')).hexdigest()

    return transaction, encoded_signature, block_hash

if __name__ == '__main__':
    # load the wallet and ledger databases
    wallet = load_wallet()
    ledger = load_ledger()

    # check that no genesis block has already been generated
    last_block_height = ledger.query(Ledger.height).order_by(-Ledger.id).first()
    if last_block_height is not None:
        logging.info('Couldn\'t create genesis block, chain already exists!')
        sys.exit(1)

    # get the most recently geneated address and private key from the wallet
    address, public_key, private_key = wallet.query(Wallet.address, Wallet.public_key, Wallet.private_key).first()

    print('Sending genesis reward to address:', address)

    transaction, signature, block_hash = create_genesis_transaction(address, private_key)

    # store the genesis block in the ledger!
    print(transaction['recipient'])
    ledger.add(Ledger(height=1,
                      timestamp=transaction['timestamp'],
                      address=transaction['address'],
                      recipient=transaction['recipient'],
                      amount=transaction['amount'],
                      signature=signature,
                      public_key=public_key,
                      block_hash=block_hash,
                      fee=0,
                      reward=1,
                      openfield='genesis'))
    ledger.commit()
    logging.info('Genesis block created!')
