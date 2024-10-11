from dotenv import set_key, dotenv_values, load_dotenv
from os.path import exists

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
