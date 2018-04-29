from merkletools import MerkleTools

class Merkle(MerkleTools):
    def __init__(self, hash_function):
        super().__init__()
        self.hash_function = hash_function