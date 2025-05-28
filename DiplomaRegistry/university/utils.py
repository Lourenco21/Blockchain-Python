from web3 import Web3
from eth_account.messages import encode_defunct

w3 = Web3()  # standalone instance for utils

def keccak256_hash(data: bytes) -> bytes:
    return w3.keccak(data)

def sign_hash(hash_bytes: bytes, private_key: str) -> bytes:
    message = encode_defunct(hash_bytes)
    signed = w3.eth.account.sign_message(message, private_key=private_key)
    return signed.signature
