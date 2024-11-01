from typing import List, Dict, Optional
import json
from pathlib import Path
import requests

MAINNET_JSON_URL = "https://raw.githubusercontent.com/0ndrec/cli-evm-accs/refs/heads/main/chains/mainnet.json"
TESTNET_JSON_URL = "https://raw.githubusercontent.com/0ndrec/cli-evm-accs/refs/heads/main/chains/testnet.json"


class Networks:
    def __init__(self, chains_path: str = "chains"):
        """
        Initialize the Networks class.

        Args:
        chains_path (str): The path to the directory containing the network configuration files.
        """
        self.chains_path = chains_path
        self.networks = self.load(self.chains_path)

    @classmethod
    def load(cls, chains_path: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Load the network configurations from the files in the specified directory.

        Args:
        chains_path (str): The path to the directory containing the network configuration files.

        Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary with 'testnet' and 'mainnet' keys, each containing a list of dictionaries representing the network configurations.
        """
        try:
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
            
            with open(testnet_path, 'r') as f:
                testnet = json.load(f)
            with open(mainnet_path, 'r') as f:
                mainnet = json.load(f)
                
            return {"testnet": testnet, "mainnet": mainnet}
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading network configurations: {e}")
            return {"testnet": [], "mainnet": []}

    def get_rpc_url(self, network_name: str) -> Optional[str]:
        """
        Return the RPC URL for a given network name.

        Args:
        network_name (str): The name of the network.

        Returns:
        Optional[str]: The RPC URL for the network or None if not found.
        """
        try:
            for network in self.networks.get("testnet", []) + self.networks.get("mainnet", []):
                if network.get("name") == network_name:
                    return network.get("rpcUrl")
            raise ValueError(f"Network '{network_name}' not found.")
        except ValueError as e:
            print(e)
            return None
        

    def get_symbol_by_id(self, network_id: str) -> Optional[str]:
        """
        Return the symbol for a given network ID.

        Args:
        network_id (str): The ID of the network.

        Returns:
        Optional[str]: The symbol for the network or None if not found.
        """
        try:
            for network in self.networks.get("testnet", []) + self.networks.get("mainnet", []):
                if network.get("chainId") == network_id:
                    return network.get("symbol")
            raise ValueError(f"Network '{network_id}' not found.")
        except ValueError as e:
            print(e)
            return None
