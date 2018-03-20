import base64
from decimal import Decimal, getcontext
import hashlib
import logging
import sys
import time

from Cryptodome.Hash import SHA256
import ecdsa

from wallet import Wallet, load_wallet
from ledger import Ledger, load_ledger

# set up decimal precision
getcontext().prec = 8

# set up logger
logging.basicConfig(level=logging.DEBUG, filename="wallet.log", format='%(asctime)s %(message)s') # include timestamp

def create_genesis_transaction(recipient, private_key):
    timestamp = int(time.time() * 10000000)

    # timestamp, address, recipient, amount, openfield
    transaction = {'timestamp': timestamp,
                   'address': 'genesis',
                   'recipient': recipient,
                   'amount': 150000000,
                   'openfield': 'genesis'}

    

    # signing key, will be used to sign the transaction and generate a signature
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)

    # hash the transaction and generate a signature from the hash
    hashed_transaction = SHA256.new(str(transaction).encode('utf-8')).hexdigest()
    signature = sk.sign(hashed_transaction.encode('utf-8'))

    # encode the signature to shorten the length
    encoded_signature = base64.b64encode(signature)

    # hash a string-tuple containing the timestamp and the raw transaction to create the block hash
    block_hash = hashlib.sha256(str((timestamp, transaction)).encode('utf-8')).hexdigest()

    return transaction, encoded_signature, block_hash

if __name__ == '__main__':
    # load the wallet and ledger databases
    wallet = load_wallet()
    ledger = load_ledger()

    # check that no genesis block has already been generated
    last_block_height = ledger.query(Ledger.height).order_by(-Ledger.id).first()
        
    if last_block_height is not None:
        logging.debug('Couldn\'t create genesis block, chain already exists!')
        sys.exit(1)
    else:
        logging.debug('No previous blocks found, creating genesis block.')

    # get the most recently geneated address and private key from the wallet
    address, public_key, private_key = wallet.query(Wallet.address, Wallet.public_key, Wallet.private_key).first()
    
    transaction, signature, block_hash = create_genesis_transaction(address, private_key)

    # this contains an example of safely performing math that will return a decimal
    print('Sending genesis reward of {} CHKN to address: {}'.format(Decimal(transaction['amount'])/100000000, transaction['recipient']))

    # store the genesis block in the ledger!
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
