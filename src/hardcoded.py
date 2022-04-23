from block import Block
from transaction import Input, Output, Transaction, TXVersion
from utils.time_tools import get_timestamp


def generate_genesis_tx(genesis_wallet):
    kp = genesis_wallet.addresses[0][1]

    i = Input("n0hash", 0)  # the block hash from which funds are located, and txid
    o = Output(
        "0x00e9823286bee337a5f3965e3b2uau", 1000000000
    )  # address to send funds and amount

    tx = Transaction(0, TXVersion.ver1, [i], [o])
    tx.timestamp = 16506941462005280
    tx.hash()
    assert (
        tx.proof == "b5551bf9425225fc2858212c3f71c0d085a57b929f376735fd6ce90b1141d850"
    )
    tx.pubkey = "5109f8adff2e06cb4612d9fb337cb8981937f77328f9386ef7f5573d2cc4051ae8f268b7ecd2307f2fccdfa9d55cfc87d0d9aef2a8637effec9fa59da0c76e32"  # key to verify the block signature with
    tx.signature = "f6fa55c140f939c43a84ff871310963dc9b1257fb3aadf1a35e63b360dc16c4e07bd0ca8c8187816e3654f3f43fa530c1c2d55f854e379939d0f6f1b9045912a"
    assert (
        tx.json()
        == '{"fee":"0","hash":"b5551bf9425225fc2858212c3f71c0d085a57b929f376735fd6ce90b1141d850","idx":0,"in":[{"idx":0,"tx":"n0hash"}],"out":[{"amount":"1000000000","recipient":"0x00e9823286bee337a5f3965e3b2uau"}],"pub":"5109f8adff2e06cb4612d9fb337cb8981937f77328f9386ef7f5573d2cc4051ae8f268b7ecd2307f2fccdfa9d55cfc87d0d9aef2a8637effec9fa59da0c76e32","sig":"f6fa55c140f939c43a84ff871310963dc9b1257fb3aadf1a35e63b360dc16c4e07bd0ca8c8187816e3654f3f43fa530c1c2d55f854e379939d0f6f1b9045912a","time":16506941462005280,"ver":1}'
    )
    print(tx)


if __name__ == "__main__":
    from config import Config
    from keys import KeyPair

    kp = KeyPair.new()

    from wallet import Wallet

    genesis_wallet = Wallet().load_from_der(Config.DEFAULT_WALLET_FP)

    generate_genesis_tx(genesis_wallet)
