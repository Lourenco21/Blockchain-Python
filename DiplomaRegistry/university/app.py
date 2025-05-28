import os
from dotenv import load_dotenv
from web3 import Web3
from university_handler import DiplomaRegistryHandler

if __name__ == "__main__":
    load_dotenv()

    provider_url = os.getenv("PROVIDER_URL")
    contract_address = os.getenv("CONTRACT_ADDRESS")
    abi_path = "../contract_abi.json"
    university_account = Web3(Web3.HTTPProvider(provider_url)).eth.accounts[0]
    private_key = os.getenv("PRIVATE_KEY")

    if not private_key:
        raise ValueError("PRIVATE_KEY not found in environment")
    if not contract_address:
        raise ValueError("CONTRACT_ADDRESS not found in environment")
    if not provider_url:
        raise ValueError("PROVIDER_URL not found in environment")
<<<<<<< Updated upstream
=======

    if not private_key:
        raise ValueError("PRIVATE_KEY not found in environment")
>>>>>>> Stashed changes

    handler = DiplomaRegistryHandler(provider_url, contract_address, abi_path, university_account, private_key)
    handler.listen_to_events()
