from merkletools import MerkleTools


class MerkleTree(MerkleTools):
    def __init__(self, hash_function=None):
        super().__init__()
        self.hash_function = hash_function or self.hash_function


if __name__ == "__main__":
    # test automatically setting hash function
    import hashlib
    tree = MerkleTree()
    sha256 = getattr(hashlib, "sha256")
    assert(tree.hash_function == sha256)
