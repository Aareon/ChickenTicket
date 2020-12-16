import asyncio
from typing import List
from mempool import Mempool
from network import P2PConnector


class Node:
    watching: List[str]
    current_height: int
    mempool: Mempool

    def __init__(self, port=24267, height=0):
        self.connector = P2PConnector("localhost", port, self.callback)
        self.watching = []
        self.current_height = height
        self.mempool = Mempool()

    def callback(self, *args):
        print(args)

    def add_watching(self, address):
        if address not in self.watching:
            self.watching.append(address)

    async def run(self):
        asyncio.create_task(self.connector.setup())
        await asyncio.sleep(5)
        print("Adding peer")
        await self.connector.add_peer("localhost", 8888)
        await asyncio.sleep(3)


if __name__ == "__main__":
    node = Node()
    asyncio.run(node.run())
