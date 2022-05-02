from block import Block
from transaction import Input, Output, Transaction, TXVersion
from utils.time_tools import get_timestamp


def generate_genesis_tx(genesis_wallet):
    kp = genesis_wallet.addresses[0][1]

    i = Input("n0hash", 0)  # the block hash from which funds are located, and txid
    o = Output(
        genesis_wallet.addresses[0][0], 1000000000
    )  # address to send funds and amount

    tx = Transaction(
        idx=0,
        ver=TXVersion.ver1,
        inputs=[i],
        outputs=[o],
        pubkey="5109f8adff2e06cb4612d9fb337cb8981937f77328f9386ef7f5573d2cc4051ae8f268b7ecd2307f2fccdfa9d55cfc87d0d9aef2a8637effec9fa59da0c76e32",
        timestamp=16506941462005280,
    )
    tx.hash()
    tx.signature = "f6fa55c140f939c43a84ff871310963dc9b1257fb3aadf1a35e63b360dc16c4e07bd0ca8c8187816e3654f3f43fa530c1c2d55f854e379939d0f6f1b9045912a"
    print(tx)
    return tx


def generate_genesis_block(txs):
    block = Block(idx=0, ver=1, timestamp=get_timestamp())
    if isinstance(txs, Transaction):
        block.add_transaction(txs)
    else:
        for tx in txs:
            block.add_transaction(tx)
    print(block)
    return block


if __name__ == "__main__":
    from config import Config
    from keys import KeyPair

    kp = KeyPair.new()

    from wallet import Wallet, WalletException

    try:
        genesis_wallet = Wallet().load_from_der(Config.DEFAULT_WALLET_FP)
    except WalletException:
        print("exc")
        Wallet.create_new()

    tx = generate_genesis_tx(genesis_wallet)
    block = generate_genesis_block([tx])
