import concurrent.futures
import threading

from loguru import logger

from ..chain import Blockchain
from ..crypto.chicken import chicken_hash


class ConcurrentBlockchain(Blockchain):
    def __init__(self, *args, max_workers=4, **kwargs):
        super().__init__(*args, **kwargs)

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.cancel_flag = threading.Event()
    
    def find_valid_nonce(self, block, start_nonce=0, end_nonce=None, workers=4):
        """Finds a valid nonce for the block in parallel using concurrent.futures."""
        self.cancel_flag.clear()
        nonce_ranges = self.divide_nonce_space(start_nonce, end_nonce, workers)
        # Using the existing executor instead of creating a new one
        futures = [self.executor.submit(self.find_nonce_in_range, block, start, end, i+1) 
                   for i, (start, end) in enumerate(nonce_ranges)]

        # Future canceling is not directly supported in ThreadPoolExecutor as it is in ProcessPoolExecutor.
        # However, we can immediately return upon finding a valid nonce to minimize unnecessary computation.
        nonce, hash_value = None, None
        for future in concurrent.futures.as_completed(futures):
            nonce, hash_value = future.result()
            if nonce is not None:
                self.cancel_flag.set()
                break  # exit early

        return nonce, hash_value if nonce is not None else (None, None)
    
    def find_nonce_in_range(self, block, start_nonce, end_nonce, worker_id):
        """Searches for a valid nonce within a given range."""
        prefix = f'{block.previous_proof}{block.state_root}{block.timestamp}'.encode()
        for nonce in range(start_nonce, end_nonce):
            if self.cancel_flag.is_set():  # Check the flag
                return None, None
            guess = prefix + str(nonce).encode()
            guess_hash = chicken_hash(guess).hex()
            if guess_hash.startswith('0' * block.difficulty):
                logger.info(f"Worker {worker_id} found the correct nonce: {nonce} - hash: {guess_hash}")
                return nonce, guess_hash
        return None, None

    def divide_nonce_space(self, start_nonce, end_nonce, workers):
        """Divides the nonce search space among workers."""
        if end_nonce is None:
            end_nonce = 2**32
        step = (end_nonce - start_nonce) // workers + 1
        return [(start_nonce + i * step, min(start_nonce + (i + 1) * step, end_nonce)) for i in range(workers)]
