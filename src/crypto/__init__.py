def hexdigest(data):
    return "".join(["%02x" % ord(x) for x in data.digest()])