import time


get_timestamp(ttime=None):
    """Get a new timestamp, or convert a time integer to timestamp
    
    Args:
        ttime: takes a time.time()
        
    returns: int
    """
    if ttime is not None and isinstance(ttime, int):
        return int(ttime * 10000000) 
      
