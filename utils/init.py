from dotenv import set_key, dotenv_values, load_dotenv
from os.path import exists
import json
from pathlib import Path
import requests

MAINNET_JSON_URL = "https://raw.githubusercontent.com/0ndrec/cli-evm-accs/refs/heads/main/chains/mainnet.json"
TESTNET_JSON_URL = "https://raw.githubusercontent.com/0ndrec/cli-evm-accs/refs/heads/main/chains/testnet.json"

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
        json.load(f)
    with open(mainnet_path, 'r') as f:
        json.load(f)

    return True