import os
from dotenv import load_dotenv
from web3 import Web3
from university_handler import DiplomaRegistryHandler

if __name__ == "__main__":
    load_dotenv()

    provider_url = "http://172.20.128.1:7545"
    contract_address = "0xBdcb5aC5De6218B007b8af9Aef67f92F44b27539"
    abi_path = "../contract_abi.json"
    university_account = Web3(Web3.HTTPProvider(provider_url)).eth.accounts[0]
    private_key = os.getenv("PRIVATE_KEY")

    if not private_key:
        raise ValueError("PRIVATE_KEY not found in environment")

    handler = DiplomaRegistryHandler(provider_url, contract_address, abi_path, university_account, private_key)
    handler.listen_to_events()
