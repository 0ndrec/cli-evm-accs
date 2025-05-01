import csv
import os
from datetime import datetime
import re

TEMPLATES = {
    "PRIVATEKEY_ADDRESS": "Private Key +[space]+ Address",
    "ADDRESS_PRIVATEKEY": "Address +[space]+ Private Key",
    "0XPRIVATEKEY_ADDRESS": "0x + Private Key +[space]+ Address",
    "ADDRESS_SEEDPHRASE": "Address +[space]+ Mnemonic",
    "SEEDPHRASE_ADDRESS": "Mnemonic +[space]+ Address"
}
class Export:
    def __init__(self, file_path: str, keys: dict, template: str):
        self.file_path = file_path
        self.keys = keys
        self.template = template


    def to_txt(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{timestamp}_export.txt"
        with open(file_name, 'w') as file:
            for key, value in self.keys.items():
                match self.template:
                    case "PRIVATEKEY_ADDRESS":
                        file.write(f"{value} {key}\n")
                    case "ADDRESS_PRIVATEKEY":
                        file.write(f"{key} {value}\n")
                    case "0XPRIVATEKEY_ADDRESS":
                        file.write(f"0x{value} {key}\n")

                    case "ADDRESS_SEEDPHRASE":
                        #todo
                        file.write(f"{key} {value}\n")
                    case "SEEDPHRASE_ADDRESS":
                        #todo
                        file.write(f"{value} {key}\n")
                    case _:
                        print(f"Unknown template: {self.template}")

    def to_csv(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{timestamp}_export.csv"
        with open(file_name, 'w') as file:
            writer = csv.writer(file)
            match self.template:
                case "PRIVATEKEY_ADDRESS":
                    writer.writerow(['Private Key', 'Address'])
                    for key, value in self.keys.items():
                        writer.writerow([value, key])
                case "ADDRESS_PRIVATEKEY":
                    writer.writerow(['Address', 'Private Key'])
                    for key, value in self.keys.items():
                        writer.writerow([key, value])
                case "0XPRIVATEKEY_ADDRESS":
                    writer.writerow(['0xPrivate Key', 'Address'])
                    for key, value in self.keys.items():
                        writer.writerow([f"0x{value}", key])
                case "ADDRESS_SEEDPHRASE":
                    #todo
                    pass
                case "SEEDPHRASE_ADDRESS":
                    #todo
                    pass
                case _:
                    print(f"Unknown template: {self.template}")

class Reader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def from_txt(self) -> list[list[str, str]]:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
            address_regex = re.compile(r'0x[a-fA-F0-9]{40}')
            private_key_regex = re.compile(r'0x[a-fA-F0-9]{64}')
            keys = []
            for line in lines:
                address = address_regex.search(line)
                private_key = private_key_regex.search(line)
                if address and private_key:
                    keys.append([address.group(), private_key.group()])
            return keys