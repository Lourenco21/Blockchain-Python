import json
from .utils import  keccak256_hash, sign_hash, hash_file
from dotenv import load_dotenv
import os
from web3 import Web3

def diploma_verification(file, cc):
    load_dotenv()

    provider_url = os.getenv("PROVIDER_URL")
    contract_address = os.getenv("CONTRACT_ADDRESS")
    university_account = "0x2146a22603c9a64BEC258De6b59D293C4f662fA9"
    private_key = os.getenv("PRIVATE_KEY")
    w3 = Web3(Web3.HTTPProvider(provider_url))
    abi_path = os.path.join(os.path.dirname(__file__), "..", "contract_abi.json")
    with open(abi_path, "r") as abi_file:
        abi = json.load(abi_file)

    contract = w3.eth.contract(address=contract_address, abi=abi)

    cc_hash = keccak256_hash(cc.encode('utf-8'))
    diploma_hash = hash_file(file)
    cc_signature = sign_hash(cc_hash, private_key)
    diploma_signature = sign_hash(diploma_hash, private_key)
    print(cc_hash)
    print(diploma_hash)
    print(cc_signature)
    print(diploma_signature)


    return contract.functions.verifyDiploma(diploma_signature, cc_signature).call({'from': university_account})