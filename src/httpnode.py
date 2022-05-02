import json
import random as rand
from dataclasses import dataclass
from pathlib import Path
from typing import List

import requests as r
from flask import Flask, Response, jsonify, make_response, request, session

import hardcoded
from block import Block
from config import Config

SRC_PATH = Path(__file__).parent


class EndpointAction:
    def __init__(self, action, mimetype="application/json"):
        self.action = action
        self.response = Response(status=200, headers={}, mimetype=mimetype)

    def __call__(self, *args):
        action_result = self.action()
        self.response.data = action_result
        return self.response


class StatusError(Exception):
    """Exception for when request returns non-200 status"""


@dataclass
class HTTPPeer:
    def __init___(self, host, port):
        self.host = host
        self.port = port

        self.connected = False

    def send_request(self, endpoint, *args):
        try:
            query = None
            if len(args) > 0:
                query = f"?{a for a in args}"
            resp = r.get(
                f"{self.host}:{self.port}/api/{endpoint}{query if query is not None else ''}"
            )
            if resp.status_code != 200:
                raise StatusError
            else:
                return resp.json()
        except:
            raise

    def connect(self, listen_port: int):
        try:
            resp = send_request("connect", listen_port)
            self.connected = True
        except:
            self.connected = False
        finally:
            return self.connected

    def get_height(self):
        """Get the current height"""
        return send_request("get_height")

    def get_block(self, height):
        return send_request("get_block")


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


def index(node):
    return json.dumps({"config": {"MAGIC": node.config.MAGIC.decode()}})


class HTTPNode:
    def __init__(
        self,
        host="0.0.0.0",
        port=42169,
        peers_list: List = None,
        wallet=None,
        config=Config,
    ):
        self.host = host
        self.port = port
        self.peers_list = peers_list
        self.wallet = wallet
        self.config = config

        self.app = FlaskAppWrapper(self.host, self.port)

        self.chain: List[Block] = []
        self.peers: List[HTTPPeer] = []
        self.is_synced = False  # run `node.sync_chain()`
        self.synced_height = 0  # current height that has been synced

    def setup(self):
        # setup node endpoints
        self.app.add_endpoint(
            endpoint="/", endpoint_name="index", handler=lambda: index(self)
        )
        self.app.add_endpoint(
            endpoint="/api/get_height",
            endpoint_name="get_height",
            handler=self.get_height,
        )
        self.app.add_endpoint(
            endpoint="/api/get_block",
            endpoint_name="get_block",
            handler=self.get_block,
        )

        # Load chain
        chain_fp = SRC_PATH.parent / "chain/blockchain.json"
        print("Loading blockchain.json")
        if not chain_fp.exists():
            # generate from genesis
            tx = hardcoded.generate_genesis_tx(self.wallet)
            block = hardcoded.generate_genesis_block(tx)
            self.chain.append(block)

        return self

    def connect(self):
        listen_port = request.args.get("listen")
        p = HTTPPeer()

    def get_height(self):
        """Endpoint `get_height`"""
        return json.dumps(
            {"height": self.synced_height}
        )  # last block from in-memory chain

    def get_block(self):
        try:
            h = int(request.args.get("h"))
            print(f"Getting block at height {h}")
            print(f"Current height: {len(self.chain) - 1}")
            print(self.chain)
        except:
            return Response(400)
        if h > self.synced_height:
            block = None
        else:
            block = self.chain[h]

        return block.json()

    def sync_chain(self):
        # using peers, update chain
        synced = False

        while True:
            # get current height from random peer (x)
            # get block proof at (x) from chosen peer

            p = rand.choice(self.peers)
            height = p.get_height()  # GET peer `get_height`

            # get block proof at (x) from more peers and compare
            proofs_and_peer = [[p.get_block()["proof"], p] for p in self.peers]

            # itemize count of unique block proofs at height (x)
            proof_count = {}
            for p, c in proofs:
                if proof_count.get(p) is not None:
                    proof_count[p]["peers"].append(c)
                    proof_count[p]["count"] += 1
                else:
                    proof_count[p] = {"count": 1, "peers": [c]}

            # choose chain from peer(s) with most common block proof
            chosen = None
            for p in proof_count:
                if chosen is None:
                    chosen = p
                elif p["count"] > chosen:
                    chosen = p

            # iterate over peers and gather chain
            while not synced:
                p = rand.choice(chosen["peers"])
                block_json = p.get_block(self.synced_height + 1)

                # validate block
                block = Block.from_json()
                break

    def run(self):
        self.app.run(use_reloader=False, threaded=True)
