from abc import ABC, abstractmethod
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import typing
import json
import os
from mnemonic import Mnemonic

class AccountManager(ABC):
    def __init__(self, storage_path="accounts.json", password="qwerty"):

        if not os.path.exists(storage_path):
            open(storage_path, 'w').close()

        if password is None or len(password) == 0:
            print("Key not provided")

        self.storage_path = storage_path
        self.password = password
        self.accounts = self._load_accounts()
    
    def _load_accounts(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return json.load(f, object_pairs_hook=dict)
        return {}

    def _save_accounts(self):
        """Сохранение аккаунтов в файл."""
        with open(self.storage_path, "w") as f:
            json.dump(self.accounts, f)

    @abstractmethod
    def create_account(self):
        """Создание нового аккаунта."""
        pass

    @abstractmethod
    def import_account(self, private_key):
        """Импорт существующего аккаунта."""
        pass

    @abstractmethod
    def import_from_seed(self, seed_phrase):
        """Импорт аккаунта из сид-фразы."""
        pass

    @abstractmethod
    def export_account(self, address):
        """Экспорт приватного ключа аккаунта."""
        pass

    def list_accounts(self):
        """Список всех сохраненных аккаунтов."""
        return list(self.accounts.keys())


class Web3AccountManager(AccountManager):
    def __init__(self, web3, storage_path="accounts.json", password="default_password"):
        """
        Реализация управления аккаунтами для Web3.
        :param web3: Экземпляр Web3.
        :param storage_path: Путь для хранения зашифрованных аккаунтов.
        :param password: Пароль для шифрования аккаунтов.
        """
        super().__init__(storage_path, password)
        self.web3 = web3

    def create_account(self):
        """Создание нового аккаунта."""
        account = self.web3.eth.account.create()
        encrypted = self.web3.eth.account.encrypt(account.key, self.password)
        self.accounts[account.address] = encrypted
        self._save_accounts()
        return account.address

    def import_account(self, private_key):
        """Импорт существующего аккаунта."""
        account = self.web3.eth.account.from_key(private_key)
        encrypted = self.web3.eth.account.encrypt(account.key, self.password)
        self.accounts[account.address] = encrypted
        self._save_accounts()
        return account.address

    def import_from_seed(self, seed_phrase):
        """Импорт аккаунта из сид-фразы."""
        mnemo = Mnemonic("english")
        private_key = mnemo.to_entropy(seed_phrase)
        return self.import_account(private_key.hex())

    def export_account(self, address):
        """Экспорт приватного ключа аккаунта."""
        if address not in self.accounts:
            raise ValueError("Аккаунт не найден")
        encrypted = self.accounts[address]
        return self.web3.eth.account.decrypt(encrypted, self.password).hex()

    def get_account_balance(self, address):
        """Получение баланса аккаунта."""
        return self.web3.eth.get_balance(address)

    def sign_transaction(self, address, transaction):
        """Подписывание транзакции аккаунтом."""
        if address not in self.accounts:
            raise ValueError("Аккаунт не найден")
        private_key = self.export_account(address)
        signed_tx = self.web3.eth.account.sign_transaction(transaction, private_key)
        return signed_tx


# Использование класса
if __name__ == "__main__":
    # Подключение к сети Ethereum
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Инициализация менеджера аккаунтов
    manager = Web3AccountManager(w3, storage_path="my_accounts.json", password="strong_password")

    # Создание нового аккаунта
    address = manager.create_account()
    print(f"Создан аккаунт: {address}")

    # Импорт аккаунта из приватного ключа
    imported_address = manager.import_account("0xYOUR_PRIVATE_KEY")
    print(f"Импортирован аккаунт: {imported_address}")

    # Импорт аккаунта из сид-фразы
    seed_phrase = "example seed phrase goes here"
    address_from_seed = manager.import_from_seed(seed_phrase)
    print(f"Аккаунт из сид-фразы: {address_from_seed}")

    # Экспорт приватного ключа
    private_key = manager.export_account(address)
    print(f"Приватный ключ аккаунта {address}: {private_key}")
