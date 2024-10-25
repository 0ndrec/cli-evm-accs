import csv
from datetime import datetime

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
                        pass
                    case "SEEDPHRASE_ADDRESS":
                        #todo
                        pass
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
