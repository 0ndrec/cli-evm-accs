import os
import json
import typing
from cryptography.fernet import Fernet, InvalidToken
from eth_account import Account


def new_encrypt_token():
    return Fernet.generate_key()


class KeyManager:
    def __init__(self, file_path, encryption_key):

        Account.enable_unaudited_hdwallet_features()

        if not os.path.exists(file_path):
            open(file_path, 'w').close()

        self.file_path = file_path

        if encryption_key is None or len(encryption_key) == 0:
            print("Encryption key not provided")

        self.cipher_suite = Fernet(encryption_key)
        self.keys = self.load_keys()


    def load_keys(self) -> typing.Dict[str, str]:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file, object_pairs_hook=dict)
        except json.JSONDecodeError:
            return {}
        return data

    def save_keys(self):
        data = {
            name: value
            for name, value in self.keys.items()
        }
        try:
            with open(self.file_path, 'w') as file:
                json.dump(data, file)
        except FileNotFoundError as e:
            print(f"Error saving keys: {e}")


    def add_key(self, name, private_key):
        encrypted_key = self.cipher_suite.encrypt(private_key.encode())
        self.keys[name] = encrypted_key.decode()
        self.save_keys()
        print(f"Key added: {name}")

    def get_key(self, name):
        key = self.keys.get(name)
        if key is None:
            print(f"No key found with name: {name}")
        return key
    
    def get_decrypted_key(self, name):
        key = self.get_key(name)
        if key is None:
            return None
        try:
            __pkey = self.cipher_suite.decrypt(key.encode())
            return __pkey.decode()
        except InvalidToken as e:
            print(f"Error decrypting key")

    def delete_key(self, name):
        if name in self.keys:
            del self.keys[name]
            self.save_keys()
            print(f"Key deleted: {name}")
        else:
            print(f"No key found with name: {name}")

    def to_private_key(self, seed_phrase):
        try:
            account = Account.from_mnemonic(seed_phrase)
            return account._private_key.hex()
        except ValueError as e:
            print(f"Error converting seed to private key: {e}")

    def create(self, name) -> str:
        new = Account.create()
        private_key = new._private_key.hex()
        if name is None or len(name) == 0:
            name = f"{new.address[2:5]}_{new.address[-3:]}"
        self.add_key(name, private_key)
        return name
    
    def get_available_batches(self) -> typing.List[str]:
        full_list = list(self.keys)
        names = [name.split("_")[0] for name in full_list]
        batches = list(set(names))
        return batches


