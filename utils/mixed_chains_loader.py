import requests
import os
import urllib
from pathlib import Path
import json
import typing
from tempfile import NamedTemporaryFile
import tempfile
import atexit
from concurrent.futures import ThreadPoolExecutor

SOURCE = 'https://chainid.network/chains.json' # Return list of dictionaries


def preload_chains(tempfile= None) -> Path:
    """
    Preload chains from the source URL and save them to a temporary file.
    If a tempfile is provided, it will be used; otherwise, a new one will be created.
    """
    if tempfile is None:
        tempfile = NamedTemporaryFile(delete=False, mode='w+')
        def cleanup():
            try:
                os.unlink(tempfile.name)
                print(f"Temporary file removed: {os.path.abspath(tempfile.name)}")
            except:
                pass
        atexit.register(cleanup)
    
    try:
        response = requests.get(SOURCE)
        response.raise_for_status()
        with open(tempfile.name, 'w') as file:
            json.dump(response.json(), file)
        return Path(tempfile.name)
    except requests.RequestException as e:
        print(f"Error fetching chains: {e}")
        return None


def convert_chain_format(chain: dict) -> dict:
    """
    Convert the chain format to the target format.
    Chech endpoint health before using it. Skip if not reachable.
    """
    def is_url_reachable(url):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.status == 200
        except:
            return False

    # Get basic chain properties
    name = chain.get("name")
    chain_id = str(chain.get("chainId"))
    
    # Get RPC URL (first one from the list if available)
    rpc_urls = chain.get("rpc", [])
    rpc_url = rpc_urls[0] if rpc_urls else None
    if rpc_url and not is_url_reachable(rpc_url):
        print(f"Skipping {name} because RPC endpoint {rpc_url} is not reachable.")
        return None
    
    # Get native currency symbol
    native_currency = chain.get("nativeCurrency", {})
    symbol = native_currency.get("symbol")
    
    # Get explorer URL (first one from the list if available)
    explorers = chain.get("explorers", [])
    if not explorers:
        return None
    
    explorer_url = explorers[0].get("url")

    # Return formatted chain data
    return {
        "name": name,
        "rpcUrl": rpc_url,
        "chainId": chain_id,
        "symbol": symbol,
        "explorer": explorer_url
    }

def write_chains_to_file(chains: typing.List[dict], file_path: Path, max_workers: int = 10) -> None:
    """
    Write the chains to a file in the target format. with threading
    """
    formatted_chains = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks for each chain conversion
        futures = [executor.submit(convert_chain_format, chain) for chain in chains]

        # Collect results as they become available
        for future in futures:
            result = future.result()
            if result:  # Only add if the result is not None
                formatted_chains.append(result)


    # Write the formatted chains to file with pretty printing
    with open(file_path, 'w') as file:
        json.dump(formatted_chains, file, indent=2)

if __name__ == "__main__":
    tempfile = preload_chains()
    if tempfile:
        with open(tempfile, 'r') as file:
            chains = json.load(file)
            print(f"Loaded {len(chains)} chains from {tempfile.name}")
        write_chains_to_file(chains, file_path=Path("chains.json"))
    else:
        print("Failed to preload chains.")