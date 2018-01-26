import base64
import os
import requests
import time

import ecdsa

def generate_ECDSA_keys():
    # Generate private key
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) # signing key
    priv_key = sk.to_string().hex() # private key
    
    # Generate public key
    vk = sk.get_verifying_key() # verifying key
    pk = vk.to_string().hex() # unencoded public key
    pub_key = base64.b64encode(bytes.fromhex(pk)) # encode `pk` to make it shorter
    
    return priv_key, pub_key
    

if __name__ == "__main__":
    print("Chicken Ticket CLI")
    print("Find help at https://github.com/Aareon/chickenticket")
    
    
