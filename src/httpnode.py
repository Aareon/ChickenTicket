import json
import random as rand
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


class HTTPPeer:
    def __init___(self, host, port):
        self.host = host
        self.port = port

        self.connected = False

    def send_request(self, endpoint, **kwargs):
        try:
            query = None
            if len(kwargs) > 0:
                query = "?"
                for k, v in kwargs.items():
                    query += f"{k}={v},"
                query = query[:-1]  # remove trailing comma
            resp = r.get(
                f"http://{self.host}:{self.port}/api/{endpoint}{query if query is not None else ''}"
            )
            if resp.status_code != 200:
                raise StatusError
            else:
                return resp.json()
        except:
            raise

    def connect(self, listen):
        try:
            resp = self.send_request("connect", listen=listen)
            self.connected = True
        except Exception as e:
            self.connected = False
            print("Failed to connect:", type(e), str(e))
        finally:
            return self.connected

    def get_height(self):
        """Get the current height"""
        return self.send_request("get_height")

    def get_block(self, height):
        return self.send_request("get_block", h=height)


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
    return json.dumps(
        {
            "config": {
                "MAGIC": node.config.MAGIC.decode(),
                "TESTNET": bool(node.config.TESTNET),
            }
        }
    )


class HTTPNode:
    def __init__(
        self,
        host="0.0.0.0",
        port=42169,
        peers_list: List = [],
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

        self.connect_cb = None  # callback to call when connections have changed

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
        self.app.add_endpoint(
            endpoint="/api/connect",
            endpoint_name="connect",
            handler=self.connect,
        )

        # prepare peers list and try to connect
        # remove peers that are invalid
        for i, p in enumerate(self.peers_list):
            host, port = p.rstrip().split(":")

            if (host, int(port)) == (self.host, self.port):
                # if this peer is this node
                continue

            print(host, port)
            print(f"Attempting connection to {host}:{port}")
            p = HTTPPeer()
            p.host, p.port = host, int(port)

            try:
                connected = p.connect(self.port)
                if connected:
                    self.peers.append(p)
                    if self.connected_cb is not None:
                        self.connected_cb(len(self.peers))
                    print(f"Connected to {host}:{port}")
            except Exception as e:
                print(type(e), str(e))
                print(f"Failed to connect to peer {host}:{port}")

        # Load chain
        chain_fp = SRC_PATH.parent / "chain/blockchain.json"
        print("Loading blockchain.json")
        if not chain_fp.exists():
            # create chain if it doesn't exist

            # check with peers first to find the most commonly accepted genesis and start from there
            if len(self.peers) > 0:
                self.sync_chain()
            else:
                # generate from genesis
                tx = hardcoded.generate_genesis_tx(self.wallet)
                block = hardcoded.generate_genesis_block(tx)
                self.chain.append(block)

        return self

    def connect(self):
        host, port = request.remote_addr, request.args.get("listen")
        try:
            p = HTTPPeer()
            p.host, p.port = host, int(port)
            if p in self.peers:
                return json.dumps({"connected": "already"})
            connected = True
            self.connect_cb(len(self.peers))
        except Exception as e:
            print(f"{request.remote_addr} failed to connect -", type(e), str(e))
            connected = False
        return json.dumps({"connected": connected})

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
            try:
                return json.dumps(self.chain[h].json())
            except Exception as e:
                print(
                    f"Failed to send `get_block` response for height {h}"
                    + "\n"
                    + f"{type(e)} {str(e)}"
                )
        except Exception as e:
            print("Failed to send get_block", type(e), str(e))
            return Response(status=500)
        if h > self.synced_height:
            return json.dumps({"block": None})

    def choose_peers_at_height(self, height):
        """Choose peers that agree on a block at given height"""
        # get block proof at (h) from peers and compare
        print(f"CHOOSE: {height}")

        proofs = []
        for p in self.peers:
            block = json.loads(p.get_block(height))
            print("GOT", block)
            proofs.append([json.loads(p.get_block(height))["hash"], p])

        # itemize count of unique block proofs at height (x)
        proof_count = {}
        for p, c in proofs:  # proof, client (peer)
            if proof_count.get(p) is not None:
                proof_count[p]["peers"].append(c)
                proof_count[p]["count"] += 1
            else:
                proof_count[p] = {"count": 1, "peers": [c]}

        return proof_count

    def sync_chain(self):
        # using peers, update chain
        synced = False

        while True:
            # get current height from random peer (x)
            # get block proof at (x) from chosen peer

            p = rand.choice(self.peers)
            height = p.get_height()["height"]  # GET peer `get_height`
            print(f"SYNC: getting height {height}")

            # get dict of proofs and peers that agree on proof @ height
            proof_count = self.choose_peers_at_height(height)
            print(f"proof_count: {proof_count}")

            # choose chain from peer(s) with most common block proof
            chosen = None
            for proof in proof_count:
                print(proof)
                if chosen is None:
                    chosen = proof_count[proof]
                elif proof_count[proof]["count"] > chosen:
                    chosen = proof_count[proof]

            print(chosen)

            # iterate over peers and gather chain
            while not synced:
                p = rand.choice(chosen["peers"])
                block_json = p.get_block(self.synced_height + 1)

                # validate block
                block = Block.from_json()
                break

    def run(self):
        self.app.run(use_reloader=False, threaded=True)
