from utils.account import new_encrypt_token, KeyManager
from dotenv import load_dotenv, dotenv_values, set_key
from getpass import getpass
from colorama import Fore, Back, Style
from web3 import Web3



load_dotenv()
config = dotenv_values(".env")


#____________________________ENCRYPTION_TOKEN_SECTION________________________________
if config["ENCRYPTION_TOKEN"] == "" or config["ENCRYPTION_TOKEN"] is None:
    print("Generating a new encryption token for safety storing private keys...")
    # Generate a new encryption token for storing private keys
    __token = new_encrypt_token().decode()
    # Save the new encryption token in the .env file
    set_key(".env", "ENCRYPTION_TOKEN", __token)
    km = KeyManager(config["KEYS_PATH"], __token)
else:
    km = KeyManager(config["KEYS_PATH"], config["ENCRYPTION_TOKEN"])
#____________________________________________________________________________________



#______________________________INITIALIZE_WEB3_SECTION________________________
def w3_init(endpoint) -> Web3:
    w3 = Web3(Web3.HTTPProvider(endpoint))
    if w3.is_connected():
        print(f"{Back.GREEN}\nConnected to the endpoint, currently chain ID: {w3.eth.chain_id}{Style.RESET_ALL}")
    else:
        print(f"{Back.RED}\n Failed to connect to the Ethereum endpoint.{Style.RESET_ALL}")
    return w3
#_____________________________________________________________________________



def menu():
    sentinel = '9'
    choice = None
    while choice != sentinel:
        print("1. Restore an account from a passphrase")
        print("2. Delete an account")
        print("3. Get private key from an account")
        print("4. Generate new account(s)")
        print("5. Connect to endpoint")
        print("6. Show my accounts")
        print("7. Get balance of each account")
        print("9. Exit")

        choice = input("Enter your choice: ")
        match choice:
            case '1':
                name = input("Enter account name: ")
                passphrase = getpass("Enter passphrase: ")
                if len(passphrase.split(" ")) < 12 or len(passphrase.split(" ")) > 24:
                    print("\n")
                    print(f"{Fore.RED}Invalid passphrase. Passphrase should contain 12 or 24 words.{Style.RESET_ALL}")
                    continue

                print("\n")
                private_key = km.to_private_key(passphrase)
                km.add_key(name, private_key)
                continue
            case '2':
                name = input("Enter account name: ")
                print("\n")
                km.delete_key(name)
                continue
            case '3':
                name = input("Enter account name: ")
                private_key = km.get_decrypted_key(name)
                if private_key is not None:
                    print(f"Private key: {private_key}")
                continue
            case '4':
                num_accounts = int(input("Enter the number of account(s) to generate: "))
                name_prefix = input("Enter the name prefix for the account(s): ")
                print("\n")
                for num in range(num_accounts):
                    name = km.create(name=f"{name_prefix}_{num + 1}")
                print(f"Successfully generated {num_accounts} account(s).")
                print("\n")
                continue
            case '5':
                global w3
                w3 = w3_init(config["ENDPOINT"])
                print("\n")
                continue
            case '6':
                if len(km.load_keys()) != 0:
                    print("Available accounts:")
                    pointer = 1
                    for acc in km.load_keys():
                        print(f"{pointer}. {acc}")
                        pointer += 1
                    print("_________________")
                    print("\n")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}")
                    print("\n")
            case '7': 
                if len(km.load_keys()) != 0:
                    try:
                        for acc in km.load_keys():
                            key = km.get_decrypted_key(acc)
                            address = w3.eth.account.from_key(key).address
                            balance = w3.eth.get_balance(address)
                            # Convert the balance from wei to ether
                            print(f"{acc}: {balance / 10**18} ETH")
                        print("\n")
                    except NameError:
                        print(f"{Fore.RED}\nPlease connect to the endpoint.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}\nNo accounts found.{Style.RESET_ALL}")
                    print("\n")
            
            case '9':
                print("Exiting the program...")
                exit(0)
            case _:
                print("Invalid choice. Please try again.")
                print("\n")

    
if __name__ == "__main__":
    menu()

    
    