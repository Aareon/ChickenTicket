import time


def get_timestamp(ttime=None):
    """Get a new timestamp, or convert a time integer to timestamp

    Args:
        ttime: takes a time.time()

    returns: int
    """
    if isinstance(ttime, float):
        return int(ttime * 10000000)
    return int(time.time() * 10000000)
