from dotenv import set_key, dotenv_values, load_dotenv
from os.path import exists
import json
from pathlib import Path
import requests

MAINNET_JSON_URL = "https://raw.githubusercontent.com/0ndrec/cli-evm-accs/refs/heads/main/chains/mainnet.json"
TESTNET_JSON_URL = "https://raw.githubusercontent.com/0ndrec/cli-evm-accs/refs/heads/main/chains/testnet.json"
DATA_PATH = "data"

class Defaults:
    KEYS_PATH = "keys.json"
    ENDPOINT = "https://optimism-rpc.publicnode.com"

def configure(path, encryption_token):
    if not exists(path):
        open(path, 'w').close()
        try:
            set_key(path, "KEYS_PATH", Defaults.KEYS_PATH)
            set_key(path, "ENCRYPTION_TOKEN", encryption_token)
            set_key(path, "ENDPOINT", Defaults.ENDPOINT)
        except Exception as e:
            print(f"Error configuring .env file: {e}")
            return {}

        load_dotenv(path)
        return dotenv_values(path)
    else:
        load_dotenv(path)
        if not dotenv_values(path).get("ENCRYPTION_TOKEN"):
            set_key(path, "ENCRYPTION_TOKEN", encryption_token)
            print("NEW encryption token set.")
        for key in ["KEYS_PATH","ENDPOINT"]:
            value = dotenv_values(path).get(key)
            if value is None or len(value) == 0:
                set_key(path, key, Defaults.__dict__.get(key))
        return dotenv_values(path)

def load_chains(chains_path: str):
    # Check both testnet and mainnet files
    testnet_path = Path(chains_path) / "testnet.json"
    mainnet_path = Path(chains_path) / "mainnet.json"

    if not testnet_path.exists() or not mainnet_path.exists():
        testnet_path.parent.mkdir(parents=True, exist_ok=True)
        mainnet_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = requests.get(TESTNET_JSON_URL)
            if response.status_code == 200:
                with open(testnet_path, 'w') as f:
                    json.dump(response.json(), f)
            response = requests.get(MAINNET_JSON_URL)
            if response.status_code == 200:
                with open(mainnet_path, 'w') as f:
                    json.dump(response.json(), f)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading network configurations: {e}")
            return False

    with open(testnet_path, 'r') as f:
        testnets=json.load(f)
    with open(mainnet_path, 'r') as f:
        mainnets=json.load(f)

    for chain in testnets + mainnets:
        chain_id = chain["chainId"]
        Path(f"{DATA_PATH}/{chain_id}").mkdir(parents=True, exist_ok=True)

    return True

def load_contracts(chain_id)-> list:
    contracts = []
    for file in Path(f"{DATA_PATH}/{chain_id}").iterdir():
        if file.suffix == ".json":
            contracts.append(file.name)
    return contracts
