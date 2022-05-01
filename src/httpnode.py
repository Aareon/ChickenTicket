from flask import Flask, Response, session, jsonify, make_response
from pathlib import Path
import json
from config import Config

class EndpointAction:

    def __init__(self, action, mimetype="application/json"):
        self.action = action
        self.response = Response(status=200, headers={}, mimetype=mimetype)

    def __call__(self, *args):
        action_result = self.action()
        self.response.data = action_result
        return self.response


class FlaskAppWrapper:
    def __init__(self, host, port, name=__name__):
        self.host = host
        self.port = port

        self._name = name
        self.app = Flask(self._name)
    
    def run(self, **kwargs):
        self.app.run(host=self.host, port=self.port, **kwargs)
    
    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))


SRC_PATH = Path(__file__).parent
print(SRC_PATH)


# API Endpoints

def index(node):
    return json.dumps({"config": {"MAGIC": node.config.MAGIC}})


class HTTPNode:
    def __init__(self, host="0.0.0.0", port=42169, peers_list=None, wallet=None, config=Config):
        self.host = host
        self.port = port
        self.peers_list = peers_list
        self.wallet = wallet
        self.config = config

        self.chain = []

        self.app = FlaskAppWrapper(self.host, self.port)

        self.wallet = wallet

    def setup(self):
        # setup node endpoints
        self.app.add_endpoint(endpoint="/", endpoint_name="index", handler=index)
        self.app.add_endpoint(
            endpoint="/api/getheight", endpoint_name="get_height", handler=self.get_height
        )

        # Load chain
        chain_fp = SRC_PATH.parent / "chain/blockchain.json"
        print("Loading blockchain.json")
        #if not chain_fp.exists():
            # generate from genesis
            # hardcoded.generate_genesis()
    
    def get_height(self):
        return json.dumps({"height": self.chain[-1]["idx"]})  # last block from in-memory chain

    def run(self):
        self.app.run(use_reloader=False, threaded=True)


if __name__ == "__main__":
    def action():
        # Execute anything
        pass

    a = FlaskAppWrapper("0.0.0.0", 5001)
    a.add_endpoint(endpoint='/ad', endpoint_name='ad', handler=action)
    a.run()
