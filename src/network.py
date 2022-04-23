# -*- coding: utf-8 -*-

# Copyright © 2019 AnonymousDapper
# If you aren't Aareon, go away

__all__ = (
    "MAGIC_BYTES",
    "MAGIC_BYTES_LEN",
    "Peer",
    "Connection",
    "ConnectionPooler",
    "P2PConnector",
)

import asyncio
from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass
from functools import partial
from random import randrange
from typing import Any, Callable, Mapping, Union

# We intercept the traffic if it starts with these bytes
MAGIC_BYTES = b"\xDapper@\x00"
MAGIC_BYTES_LEN = len(MAGIC_BYTES)


@dataclass
class Peer:
    """
    Represents a network peer.
    """

    addr: str
    port: int

    def __hash__(self):
        return hash((hash(self.addr), hash(self.port)))


@dataclass
class Connection:
    """
    Represents a peer connection with a (reader, writer) pair.
    """

    closed: bool
    reader: StreamReader
    writer: StreamWriter


PeerCallback = Callable[[Peer, bytes], Any]


class ConnectionPooler:
    """
    Stores and manages a pool of network peers.
    """

    def __init__(
        self,
        recv_callback: PeerCallback,
        *,
        max_peers: int = 0,
        use_random_ports: bool = True,
        peer_port: int = 8080,
    ):
        self.recv_callback = recv_callback
        self.max_peers = max(max_peers, 0)

        if use_random_ports:
            self.port_callback = partial(randrange, 2000, 65535)

        else:
            self.port_callback = lambda: peer_port

        self.peers: Mapping[Peer, Connection] = {}

    def check_peers(self) -> bool:
        """
        Checks whether adding another peer will hit the max_peers limit.
        """
        if self.max_peers == 0:
            return True

        return len(self.peers) < self.max_peers

    async def write_peer(self, peer: Peer, data: bytes):
        if peer not in self.peers:
            raise ValueError(f"Failed writing, {peer} not a connected peer")

        conn = self.peers[peer]

        if conn.closed:
            raise RuntimeError(f"Failed writing, {conn} for {peer} is closed")

        conn.writer.write(data)
        await conn.writer.drain()

    async def add_peer(self, peer: Peer):
        """
        Adds a peer and initiates a connection.
        """
        if peer in self.peers:
            return

        if not self.check_peers():
            raise RuntimeError(
                f"Can't add peer, max_peers ({self.max_peers}) already reached"
            )

        print(f"[Add] Connecting to {peer}")
        connection = await self.connect_peer(peer)

        self.peers[peer] = connection

        asyncio.create_task(self.start_poll(peer))

        # await self.write_peer(peer, b"Hello, World!")

    async def connect_peer(self, peer: Peer) -> Connection:
        """
        Initiates a connection to a peer.
        """
        peer_info = await asyncio.open_connection(
            peer.addr, peer.port, local_addr=("127.0.0.1", self.port_callback())
        )

        return Connection(False, *peer_info)

    async def close_peer_connection(self, peer: Peer):
        """
        Closes a peer connection and removes the peer.
        """
        self.peers[peer].closed = True
        self.peers[peer].writer.close()

        try:
            await self.peers[peer].wait_closed()

        except:
            pass

        finally:
            await self.close_peer(peer)

    async def close_peer(self, peer: Peer):
        """
        Removes a peer with a closed connection.
        """
        if self.peers[peer].closed:
            del self.peers[peer]

        else:
            raise ValueError(f"{peer} has an open connection, cannot close")

    async def start_poll(self, peer: Peer):
        """
        Contiously polls a peer connection.
        """
        if peer not in self.peers:
            raise ValueError(f"{peer} is not a recognized peer")

        connection = self.peers[peer]

        while not connection.closed:
            try:
                print(f"[Poll] Polling {peer}")
                data = await connection.reader.read()

            except Exception as e:
                print(f"[Error] ({type(e).__name__}: {e}")
                exit()

            except asyncio.ConnectionError:
                print(f"{peer} errored while reading, closing connection")
                await self.close_peer_connection(peer)
                return

            if not data:
                print(f"{peer} sent empty data while reading, closing connection")
                await self.close_peer_connection(peer)
                return

            if data[:MAGIC_BYTES_LEN] == MAGIC_BYTES:
                await self._dispatch_internal(peer, data[MAGIC_BYTES_LEN:])

            else:
                print(f"[Recvd] {peer} {data!r}")
                await self.recv_callback(peer, data)

    async def recv_connect(self, reader: StreamReader, writer: StreamWriter):
        """
        Recieves an incoming connection and starts a polling task.

        """
        details = writer.get_extra_info("peername")

        peer = Peer(*details)
        print(f"Recieved connection from {peer}")

        if not self.check_peers():
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass

            raise RuntimeError(
                f"Can't add peer, max_peers ({self.max_peers}) already reached"
            )

        self.peers[peer] = Connection(False, reader, writer)

        await self.start_poll(peer)

    async def _dispatch_internal(self, peer: Peer, data: bytes):
        print(f"[Internal] {peer} {data!r}")


class P2PConnector:
    """
    Manages a connection pooler and handles callbacks.
    """

    def __init__(self, host_addr: str, host_port: int, recv_cb: PeerCallback, **kwargs):
        self.addr = host_addr
        self.port = host_port
        self.pooler = ConnectionPooler(recv_cb, **kwargs)

    async def setup(self):
        server = await asyncio.start_server(
            self.pooler.recv_connect, self.addr, self.port
        )

        addr = server.sockets[0].getsockname()
        print(f"Listening on {addr}")

        async with server:
            await server.serve_forever()

    def list_peers(self):
        for peer in self.pooler.peers:
            yield peer

    async def send_to_peer(self, peer: Peer, data: Union[str, bytes]):
        if isinstance(data, str):
            data = bytes(data, encoding="utf-8")

        else:
            raise TypeError(f"data can be bytes or str, not {type(data)}")

        await self.pooler.write_peer(peer, data)

    async def add_peer(self, addr: str, port: int):
        peer = Peer(addr, port)
        await self.pooler.add_peer(peer)


if __name__ == "__main__":
    # Testing shit, thanks @Dap
    # Running this in WSL2 on port 42069, then connecting in VSCode
    # on 42169 works!

    async def main():
        def cb(*args):
            print("called")

        conn = P2PConnector("0.0.0.0", 42169, cb)
        await conn.add_peer("127.0.0.1", 42069)
        await conn.setup()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except:
        pass
    finally:
        loop.close()
