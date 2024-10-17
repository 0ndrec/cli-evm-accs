import os
from utils.tx import SendTransaction
from utils.xprt import Export, TEMPLATES
from utils.init import configure
from utils.account import new_encrypt_token, KeyManager
from colorama import Fore, Back, Style
from web3 import Web3
import re
import inquirer



# Check validity of .env file
config = configure(".env", new_encrypt_token().decode())
for key in ["ENDPOINT", "KEYS_PATH", "ENCRYPTION_TOKEN"]:
    if config.get(key) is None or len(config.get(key)) == 0:
        print(f"{Back.RED}Error: {key} is missing or empty.{Style.RESET_ALL}")
        exit()


#______________________________INITIALIZE_KEY_MANAGER_SECTION________________________
km = KeyManager(config["KEYS_PATH"], config["ENCRYPTION_TOKEN"])
# __________________________________________________________________________________


# ______________________________INITIALIZE_WEB3_SECTION________________________
def w3_init(endpoint) -> Web3:
    w3 = Web3(Web3.HTTPProvider(endpoint))
    if w3.is_connected():  
        print(
            f"{Back.BLUE}\nConnected to the endpoint, current chain ID: {w3.eth.chain_id}{Style.RESET_ALL}"
        )
    else:
        print(f"{Back.RED}\nFailed to connect to the Ethereum endpoint.{Style.RESET_ALL}")
    return w3
# _____________________________________________________________________________




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
                    "Add manually an account by private key",
                    "Delete an account",
                    "Get private key from an account",
                    "Generate new account(s)",
                    "Connect to endpoint",
                    "Show my accounts",
                    "Unsafe export keys to file",
                    "Get balance of each account",
                    "Transfer native token",
                    "Exit",
                ],
            )
        ]
        answer = inquirer.prompt(questions)
        choice = answer["choice"]

        match choice:
            case "Add manually an account by private key":
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal before action
                questions = [
                    inquirer.Text("name", message="Enter account name"),
                    inquirer.Password("private_key", message="Enter private key"),
                ]
                answers = inquirer.prompt(questions)
                name = answers["name"]
                private_key = answers["private_key"]
                if private_key.startswith("0x"):
                    private_key = private_key[2:]
                if len(private_key) != 64:
                    print(f"{Fore.RED}\nInvalid private key. Length should be 64.{Style.RESET_ALL}\n")
                    input("Press Enter to continue...")
                    continue

                print("\n")
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
                        message="Enter Ethereum endpoint (default from .env file)",
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

            case "Unsafe export keys to file":
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
                        ),
                        inquirer.List(
                            "template",
                            message="Select the template for export",
                            choices=TEMPLATES,
                            default="PRIVATEKEY_ADDRESS"
                        ),
                        inquirer.List(
                            "file_format",
                            message="Select the file format for export",
                            choices=["txt", "csv"],
                            default="txt"
                        )
                    ]
                    answers = inquirer.prompt(questions)
                    export_path = answers["export_path"] or DEFAULT_EXPORT_PATH
                    template = answers["template"]
                    file_format = answers["file_format"]
                    _export = Export(export_path, export_data, template)
                    if file_format == "txt":
                        _export.to_txt()
                    elif file_format == "csv":
                        _export.to_csv()
                    else:
                        print(f"{Fore.RED}\nUnrecognized file format{Style.RESET_ALL}\n")
                    
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
                            # Convert the balance from wei to ether.
                            print(f"{acc}: {balance / 10**18} ETH (or native token) ")
                        print("\n")
                    except Exception as e:
                        print(f"{Fore.RED}\nError fetching balances: {e}{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}\n")
                input("Press Enter to continue...")
                continue

            case "Transfer native token [TODO]":
                os.system('cls' if os.name == 'nt' else 'clear')
                accounts = km.load_keys()
                if accounts:
                    if w3 is None:
                        print(f"{Fore.RED}\nPlease connect to the endpoint first.{Style.RESET_ALL}\n")
                        input("Press Enter to continue...")
                        continue
                    tx_question = [
                        inquirer.List( 
                            "accounts",
                            message="Select accounts to transfer",
                            choices=accounts,
                            carousel=True,
                        ),
                        inquirer.Text(
                            "amount",
                            message="Enter the amount to transfer",
                        ),
                        inquirer.Text(
                            "to_address",
                            message="Enter the recipient's address",
                            validate = lambda _, x: re.match("^0x[a-fA-F0-9]{40}$", x)
                        ),
                        inquirer.Text(
                            "gas_limit",
                            message="Enter the gas limit",
                        ),
                        inquirer.Text(
                            "gas_price",
                            message="Enter the gas price",
                        )
                    ]

                    answers = inquirer.prompt(tx_question)

                    for acc in answers["accounts"]:
                        key = km.get_decrypted_key(acc)
                        address = w3.eth.account.from_key(key).address
                        w3.eth.default_account = address
                        to_address = answers["to_address"]


                        # Convert all strings to floats
                        amount = int(answers["amount"])
                        gas_limit = int(answers["gas_limit"])
                        gas_price = int(answers["gas_price"])

                        amount = int(amount * 10**18)
                        gas_limit = int(gas_limit * 10**9)
                        gas_price = int(gas_price * 10**9)

                        tx = SendTransaction(w3, address, to_address, amount, gas_limit, gas_price)
                        tx.build()
                        tx.sign()
                        result = tx.send()

                        if result:
                            print(f"{Fore.GREEN}\nTransaction sent successfully: {result.hex()}{Style.RESET_ALL}\n")
                        else:
                            print(f"{Fore.RED}\nTransaction failed to send for wallet: {address} {Style.RESET_ALL}\n")
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
