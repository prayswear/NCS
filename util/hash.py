import hashlib

def generate_eid(hrn):
    return hashlib.sha1(hrn.encode("utf-8")).hexdigest()[0:32]
