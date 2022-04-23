""""ChickenTicket client node
"""
import json
from pathlib import Path

from config import Config
from network.http import FlaskAppWrapper
from wallet import Wallet

SRC_PATH = Path(__file__).parent
print(SRC_PATH)


# API Endpoints

def index():
    return json.dumps({"config": {"MAGIC": Config.MAGIC}})


class HTTPNode:
    def __init__(self, host="0.0.0.0", port=42169, peers_list=None, wallet=None):
        self.host = host
        self.port = port
        self.peers_list = peers_list

        self.chain = []

        self.app = FlaskAppWrapper(self.host, self.port)

        self.wallet = Wallet()

    def setup(self):
        # setup node endpoints
        self.app.add_endpoint(endpoint="/", endpoint_name="index", handler=index)
        self.app.add_endpoint(
            endpoint="/api/getheight", endpoint_name="get_height", handler=self.get_height
        )

        # Load chain
        chain_fp = SRC_PATH.parent / "chain/blockchain.json"
        print("Loading blockchain.json")
        if not chain_fp.exists():
            # generate from genesis
            hardcoded.generate_genesis()
    
    def get_height(self):
        return json.dumps({"height": self.chain[-1]["idx"]})  # last block from in-memory chain

    def run(self):
        self.app.run()


if __name__ == "__main__":
    node = HTTPNode()
    node.setup()
    # node.run()
