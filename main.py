import os
from datetime import datetime
from utils.account import new_encrypt_token, KeyManager
from dotenv import load_dotenv, dotenv_values, set_key
from colorama import Fore, Back, Style
from web3 import Web3
import inquirer

load_dotenv()
config = dotenv_values(".env")



#____________________________DEFAULTS_ENV_VALUES_SECTION____________________________
if config.get("ENDPOINT") == "" or config.get("ENDPOINT") is None:
    set_key(".env", "ENDPOINT", "")
if config.get("KEYS_PATH") == "" or config.get("KEYS_PATH") is None:
    set_key(".env", "KEYS_PATH", "keys.json")

if config.get("ENCRYPTION_TOKEN") == "" or config.get("ENCRYPTION_TOKEN") is None:
    print("Generating a new encryption token for safely storing private keys...")
    # Generate a new encryption token for storing private keys
    __token = new_encrypt_token().decode()
    set_key(".env", "ENCRYPTION_TOKEN", __token)
# ____________________________________________________________________________________



#______________________________INITIALIZE_KEY_MANAGER_SECTION________________________
km = KeyManager(config["KEYS_PATH"], config["ENCRYPTION_TOKEN"])
# __________________________________________________________________________________


# ______________________________INITIALIZE_WEB3_SECTION________________________
def w3_init(endpoint) -> Web3:
    w3 = Web3(Web3.HTTPProvider(endpoint))
    if w3.is_connected():
        print(
            f"{Back.GREEN}\nConnected to the endpoint, current chain ID: {w3.eth.chain_id}{Style.RESET_ALL}"
        )
    else:
        print(f"{Back.RED}\nFailed to connect to the Ethereum endpoint.{Style.RESET_ALL}")
    return w3
# _____________________________________________________________________________


# _________________________________UNSAFE_EXPORT_TO_TXT_SECTION____________________________
def export_private_keys_to_txt(keys: dict, file_path: str):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{timestamp}_export.txt"
    file_path = os.path.join(file_path, file_name)
    with open(file_path, 'w') as file:
        for address, private_key in keys.items():
            file.write(f"{private_key} {address}\n")
#_________________________________________________________________________________________


def menu():
    sentinel = "Exit"
    choice = None
    w3 = None  # Initialize w3 variable
    while choice != sentinel:
        # Clear the terminal at the beginning of each loop iteration
        os.system('cls' if os.name == 'nt' else 'clear')

        questions = [
            inquirer.List(
                "choice",
                message="What do you want to do?",
                choices=[
                    "Restore an account from a passphrase",
                    "Delete an account",
                    "Get private key from an account",
                    "Generate new account(s)",
                    "Connect to endpoint",
                    "Show my accounts",
                    "Unsafe export keys to text file",
                    "Get balance of each account",
                    "Exit",
                ],
            )
        ]
        answer = inquirer.prompt(questions)
        choice = answer["choice"]

        match choice:
            case "Restore an account from a passphrase":
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal before action
                questions = [
                    inquirer.Text("name", message="Enter account name"),
                    inquirer.Password("passphrase", message="Enter passphrase"),
                ]
                answers = inquirer.prompt(questions)
                name = answers["name"]
                passphrase = answers["passphrase"]
                if len(passphrase.split(" ")) not in [12, 24]:
                    print("\n")
                    print(
                        f"{Fore.RED}Invalid passphrase. Passphrase should contain 12 or 24 words.{Style.RESET_ALL}"
                    )
                    input("Press Enter to continue...")  # Pause before clearing
                    continue

                print("\n")
                private_key = km.to_private_key(passphrase)
                km.add_key(name, private_key)
                print(f"Account '{name}' restored successfully.\n")
                input("Press Enter to continue...")
                continue

            case "Delete an account":
                os.system('cls' if os.name == 'nt' else 'clear')
                accounts = km.load_keys()
                if accounts:
                    questions = [
                        inquirer.List(
                            "name",
                            message="Select account to delete",
                            choices=accounts,
                        )
                    ]
                    answers = inquirer.prompt(questions)
                    name = answers["name"]
                    km.delete_key(name)
                    print(f"Account '{name}' deleted.\n")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}\n")
                input("Press Enter to continue...")
                continue

            case "Get private key from an account":
                os.system('cls' if os.name == 'nt' else 'clear')
                accounts = km.load_keys()
                if accounts:
                    questions = [
                        inquirer.List(
                            "name",
                            message="Select account to get private key",
                            choices=accounts,
                        )
                    ]
                    answers = inquirer.prompt(questions)
                    name = answers["name"]
                    private_key = km.get_decrypted_key(name)
                    if private_key is not None:
                        print(f"Private key for '{name}': {private_key}\n")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}\n")
                input("Press Enter to continue...")
                continue

            case "Generate new account(s)":
                os.system('cls' if os.name == 'nt' else 'clear')
                questions = [
                    inquirer.Text(
                        "num_accounts",
                        message="Enter the number of account(s) to generate",
                        validate=lambda _, x: x.isdigit() and int(x) > 0,
                    ),
                    inquirer.Text("name_prefix", message="Enter the name prefix for the account(s)"),
                ]
                answers = inquirer.prompt(questions)
                num_accounts = int(answers["num_accounts"])
                name_prefix = answers["name_prefix"]
                print("\n")
                for num in range(num_accounts):
                    km.create(name=f"{name_prefix}_{num + 1}")
                print(f"Successfully generated {num_accounts} account(s).\n")
                input("Press Enter to continue...")
                continue

            case "Connect to endpoint":
                os.system('cls' if os.name == 'nt' else 'clear')

                endpoint_default = config.get("ENDPOINT", "")

                questions = [
                    inquirer.Password(
                        "endpoint",
                        message="Enter Ethereum endpoint (default from .env file):",
                        default=endpoint_default
                    )
                ]

                answers = inquirer.prompt(questions)
                endpoint = answers["endpoint"] or endpoint_default
                if not endpoint:
                    print(f"{Fore.RED}\nNo endpoint provided.{Style.RESET_ALL}\n")
                    input("Press Enter to continue...")
                    continue
                w3 = w3_init(endpoint)
                print("\n")
                input("Press Enter to continue...")
                continue

            
            case "Show my accounts":
                os.system('cls' if os.name == 'nt' else 'clear')
                accounts = km.load_keys()
                if accounts:
                    print("Available accounts:")
                    for idx, acc in enumerate(accounts, start=1):
                        print(f"{idx}. {acc}")
                    print("_________________\n")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}\n")
                input("Press Enter to continue...")
                continue

            case "Unsafe export keys to text file":
                DEFAULT_EXPORT_PATH = os.getcwd()
                os.system('cls' if os.name == 'nt' else 'clear')
                
                export_data = {}
                accounts = km.load_keys()

                if w3 is None:
                    print(f"{Fore.RED}\nPlease connect to the endpoint first.{Style.RESET_ALL}\n")
                    input("Press Enter to continue...")
                    continue

                for acc in accounts:
                    key = km.get_decrypted_key(acc)
                    evm_acc = w3.eth.account.from_key(key)
                    address = evm_acc.address
                    if key:
                        export_data[address] = key

                if accounts:
                    questions = [
                        inquirer.Text(
                            "export_path",
                            message="Enter the path to export the keys to ",
                            default=DEFAULT_EXPORT_PATH
                        )
                    ]
                    answers = inquirer.prompt(questions)
                    export_path = answers["export_path"] or DEFAULT_EXPORT_PATH
                    export_private_keys_to_txt(export_data, export_path)
                    print("\n")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}\n")
                input("Press Enter to continue...")
                continue

            case "Get balance of each account":
                os.system('cls' if os.name == 'nt' else 'clear')
                accounts = km.load_keys()
                if accounts:
                    if w3 is None:
                        print(f"{Fore.RED}\nPlease connect to the endpoint first.{Style.RESET_ALL}\n")
                        input("Press Enter to continue...")
                        continue
                    try:
                        for acc in accounts:
                            key = km.get_decrypted_key(acc)
                            address = w3.eth.account.from_key(key).address
                            balance = w3.eth.get_balance(address)
                            # Convert the balance from wei to ether
                            print(f"{acc}: {balance / 10**18} ETH")
                        print("\n")
                    except Exception as e:
                        print(f"{Fore.RED}\nError fetching balances: {e}{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}\n")
                input("Press Enter to continue...")
                continue

            case "Exit":
                print("Exiting the program...")
                exit(0)

            case _:
                print("Invalid choice. Please try again.\n")
                input("Press Enter to continue...")


if __name__ == "__main__":
    menu()
