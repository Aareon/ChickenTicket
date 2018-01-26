class Node:
    """
    Represents a node (not to be confused with a peer)
    A Node is any applicable peer capable of serving the
    entire blockchain"""

    def __init__(self, ip, port):
        # IP and Port of specific Node
        self.ip = ip
        self.port = port

        # Reported block_height of specific node, makes checking `concensus` easier
        self.block_height = None

        # WIP
