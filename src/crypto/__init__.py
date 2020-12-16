def hexdigest(data: bytes) -> str:
    return "".join(["%02x" % x for x in data])
