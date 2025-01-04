import os
from colorama import Fore, Back, Style
from web3 import Web3
import inquirer
from pathlib import Path

from utils.tx import SendTransaction
from utils.chain import Networks
from utils.abi import ABIDecoder, get_abi
from utils.export import Export, Reader, TEMPLATES
from utils.init import configure, load_chains, load_contracts
from utils.account import new_encrypt_token, KeyManager


# Check validity of .env file or initialize it
config = configure(".env", new_encrypt_token().decode())
for key in ["ENDPOINT", "KEYS_PATH", "ENCRYPTION_TOKEN"]:
    if config.get(key) is None or len(config.get(key)) == 0:
        print(f"{Back.RED}Error: {key} is missing or empty.{Style.RESET_ALL}")
        exit()


#______________________________INITIALIZE_KEY_MANAGER_SECTION________________________
km = KeyManager(config["KEYS_PATH"], config["ENCRYPTION_TOKEN"])
# __________________________________________________________________________________

#______________________________INITIALIZE_CHAINS_SECTION________________________
app_dir = Path(__file__).parent
chains_dir = app_dir / "chains"
if load_chains(chains_path=chains_dir):
    chains = Networks(chains_path=chains_dir)
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
                    "Import batch from file",
                    "Connect to endpoint",
                    "Show my accounts",
                    "Show available batches of accounts",
                    "Unsafe export keys to file",
                    "Get balance of each account",
                    "Transaction(s) [NATIVE TOKEN]",
                    "Contract call(s) [ERC20 TOKEN]",
                    "Exit",
                ],
            )
        ]
        answer = inquirer.prompt(questions)
        choice = answer["choice"]

        match choice:
            case "Show available batches of accounts":
                os.system('cls' if os.name == 'nt' else 'clear')
                batches = km.get_available_batches()
                if batches:
                    print(f"Available batches of accounts: {batches}")
                else:
                    print("Not found any batches of accounts.")
                input("Press Enter to continue...")
                continue


            case "Add manually an account by private key":
                os.system('cls' if os.name == 'nt' else 'clear')
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

            case "Import batch from file":
                os.system('cls' if os.name == 'nt' else 'clear')
                # Ask path to file. or name
                questions = [
                    inquirer.Text("file_path", message="Enter the path to the file"),
                    inquirer.Text("name_prefix", message="Enter the name prefix for the account(s)"),
                ]
                answers = inquirer.prompt(questions)
                file_path = answers["file_path"]
                if not os.path.exists(file_path):
                    print(f"{Fore.RED}\nFile not found.{Style.RESET_ALL}\n")
                    input("Press Enter to continue...")
                    continue
                read = Reader(file_path)
                acc_list = read.from_txt()
                if acc_list:
                    for key in acc_list:
                        key_name = f"{answers['name_prefix']}_{acc_list.index(key) + 1}"
                        km.add_key(key_name, key[1])
                    print(f"Successfully imported {len(acc_list)} account(s).\n")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}\n")
                input("Press Enter to continue...")
                continue

            case "Connect to endpoint":
                os.system('cls' if os.name == 'nt' else 'clear')
                endpoint = None 
                questions = [
                    inquirer.List(
                        "type",
                        message="Select network type",
                        choices=["Mainnet", "Testnet"],
                    )
                ]
                answers = inquirer.prompt(questions)
                if answers["type"] == "Mainnet":
                    _chains = chains.networks["mainnet"]
                elif answers["type"] == "Testnet":
                    _chains = chains.networks["testnet"]

                # Select network by name
                questions = [
                    inquirer.List(
                        "name",
                        message="Select network",
                        choices=[chain["name"] for chain in _chains],
                    )
                ]
                answers = inquirer.prompt(questions)
                endpoint = chains.get_rpc_url(answers["name"])
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
                        current_symbol = chains.get_symbol_by_id(str(w3.eth.chain_id))
                        for acc in accounts:
                            key = km.get_decrypted_key(acc)
                            address = w3.eth.account.from_key(key).address
                            balance = w3.eth.get_balance(address)
                            if balance > 0:
                                print(f"{acc}: {balance / 10**18} {current_symbol}")
                        print("\n")
                    except Exception as e:
                        print(f"{Fore.RED}\nError fetching balances: {e}{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}\n")
                input("Press Enter to continue...")
                continue

            case "Transaction(s) [NATIVE TOKEN]":
                os.system('cls' if os.name == 'nt' else 'clear')
                accounts = km.load_keys()

                # Check if accounts exist
                if accounts:
                    if w3 is None:
                        print(f"{Fore.RED}\nPlease connect to the endpoint first.{Style.RESET_ALL}\n")
                        input("Press Enter to continue...")
                        continue


                    tx_question = [
                        inquirer.Checkbox( 
                            "accounts",
                            message="Select [FROM] account(s) to transfer",
                            choices=accounts,
                        ),
                        inquirer.Text(
                            "amount",
                            message="Enter the amount to transfer (in ether or native token)",

                        ),
                        inquirer.Text(
                            "to_address",
                            message="Enter the recipient's address",
                            default = "0x0000000000000000000000000000000000000000",
                        ),
                        inquirer.Text(
                            "gas_limit",
                            message="Enter the gas limit",
                        ),
                        inquirer.Text(
                            "gas_price",
                            message="Enter the gas price",
                            default = w3.eth.gas_price
                        )
                    ]

                    answers = inquirer.prompt(tx_question)



                    for acc in answers["accounts"]:

                        #________________SEND TRANSACTION__________________________
                        key = km.get_decrypted_key(acc)
                        # add 0x to private key
                        if "0x" not in key:
                            key = "0x" + key
                        address = w3.eth.account.from_key(key).address
                        w3.eth.default_account = address
                        to_address = answers["to_address"]

                        try:
                            amount = answers["amount"]
                            gas_limit = answers["gas_limit"]
                            gas_price = answers["gas_price"]
                        except ValueError as e:
                            print(f"{Fore.RED}\nInvalid input: {e}{Style.RESET_ALL}\n")
                            continue
                        # Converting to correct format (wei)
                        amount = w3.to_wei(float(amount), 'ether')
                        gas_limit = int(gas_limit)  
                        gas_price = int(gas_price)


                        print(f"{Fore.GREEN}\nTransferring from: {acc} to: {answers['to_address']}{Style.RESET_ALL}\n")
                        chain_id = w3.eth.chain_id
                        tx = SendTransaction(w3, chain_id, key, address, to_address, amount, gas_limit, gas_price)
                        tx.build()

                        try:
                            tx.sign()
                            result = tx.send()
                            print(f"{Fore.GREEN}\nTransaction sent successfully: {result.hex()}{Style.RESET_ALL}\n")
                        except Exception as e:
                            print(f"{Fore.RED}\nError sending transaction: {e}{Style.RESET_ALL}\n")
                        # __________________________________________________________________

            case "Contract call(s) [ERC20 TOKEN]":
                os.system('cls' if os.name == 'nt' else 'clear')
                accounts = km.load_keys()

                # Check if accounts exist
                if accounts:
                    if w3 is None:
                        print(f"{Fore.RED}\nPlease connect to the endpoint first.{Style.RESET_ALL}\n")
                        input("Press Enter to continue...")
                        continue

                    chain_id = w3.eth.chain_id
                    available_contracts = load_contracts(chain_id)


                    primary_question = [
                        inquirer.Checkbox( 
                            "accounts",
                            message="Select [FROM] account(s) to execute contract call",
                            choices=accounts,
                        ),
                        inquirer.List(
                            "contract",
                            message="Select a contract",
                            choices=available_contracts

                        )
                    ]

                    primary_answers = inquirer.prompt(primary_question)

                    selected_contract = primary_answers["contract"].split(".")[0]
                    abi = get_abi(selected_contract, chain_id)
                    current_contract = w3.eth.contract(address=selected_contract, abi=abi.abi)
                    decimals = current_contract.functions.decimals().call()
                    print(f"Decimals: {decimals}")

                    questions = [
                        inquirer.List(
                            "function",
                            message="Select a function",
                            choices=abi.list_functions()
                        )
                    ]

                    answers = inquirer.prompt(questions)
                    if answers["function"] == "transfer":
                        transfer_question = [
                            inquirer.Text(
                                "to_address",
                                message="Enter the recipient's address",
                                default = "0x0000000000000000000000000000000000000000",
                            ),
                            inquirer.Text(
                                "amount",
                                message="Enter the amount to transfer",
                            )
                        ]

                        transfer_answers = inquirer.prompt(transfer_question)

                        amount = transfer_answers["amount"]
                        to_address = transfer_answers["to_address"]

                        amount = w3.to_wei(float(amount), 'ether')

                    for acc in primary_answers["accounts"]:
                        key = km.get_decrypted_key(acc)
                        if "0x" not in key:
                            key = "0x" + key
                        address = w3.eth.account.from_key(key).address
                        w3.eth.default_account = address
                        nonce = w3.eth.get_transaction_count(address)
                        tx = current_contract.functions.transfer(to_address, amount).build_transaction({
                            'from': address,
                            'nonce': nonce,
                            'gasPrice': w3.eth.gas_price,
                            'chainId': chain_id
                        })
                        tx['gas'] = w3.eth.estimate_gas(tx)
                        signed_tx = w3.eth.account.sign_transaction(tx, key)
                        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                        print(f"{Fore.GREEN}\nTransaction sent successfully: {tx_hash.hex()}{Style.RESET_ALL}\n")




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
