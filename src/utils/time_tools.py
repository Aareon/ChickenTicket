import time
from typing import Optional, Union


def get_timestamp(ttime: Optional[Union[float, int]] = None) -> int:
    """Get a new timestamp, or convert a time integer or float to timestamp

    Args:
        ttime: takes a time.time(), an integer or floating point number representing seconds, or None.

    Returns: int
    Raises:
        TypeError: If ttime is not a float, int (excluding boolean), or None.
    """
    # Explicitly check for None first
    if ttime is None:
        return int(time.time() * 10000000)
    # Check for boolean values explicitly because they are subclasses of int
    elif isinstance(ttime, bool):
        raise TypeError("ttime must not be a boolean.")
    elif isinstance(ttime, (float, int)):
        return int(float(ttime) * 10000000)
    else:
        raise TypeError("ttime must be a float, int, or None.")
