from pydantic import BaseModel, ValidationError
from typing import List, Union, Optional
import json


class ABIFunctionInput(BaseModel):
    name: str
    type: str

class ABIFunctionOutput(BaseModel):
    name: Optional[str] = None
    type: str

class ABIFunction(BaseModel):
    name: str
    inputs: List[ABIFunctionInput]
    outputs: List[ABIFunctionOutput]
    stateMutability: str
    type: str = "function"


class ABIEvent(BaseModel):
    name: str
    inputs: List[ABIFunctionInput]
    anonymous: bool
    type: str = "event"

class ABIDecoder:
    """
    A class for decoding ABI data.

    Attributes:
        abi (List[dict]): A list of dictionary objects representing the ABI.
        contract_address (str): A string representing the Ethereum contract address.

    Methods:
        __init__(self, abi: List[dict], contract_address: str):
            Initializes the ABIDecoder with an ABI and contract address.

        get_function(self, name: str) -> Union[ABIFunction, None]:
            Returns the ABIFunction object with the specified name, or None if not found.

        get_event(self, name: str) -> Union[ABIEvent, None]:
            Returns the ABIEvent object with the specified name, or None if not found.

        list_functions(self) -> List[str]:
            Returns a list of function names.

        list_events(self) -> List[str]:
            Returns a list of event names.
    """
    def __init__(self, abi: List[dict], contract_address: str):
        """
        Initializes the ABIDecoder with an ABI and contract address.

        :param abi: A list of dictionary objects representing the ABI.
        :param contract_address: A string representing the Ethereum contract address.
        """
        self.abi = abi
        self.contract_address = contract_address
        self.functions = []
        self.events = []
        self._parse_abi()

        if not self.contract_address.startswith("0x") or len(self.contract_address) != 42:
            raise ValueError("Invalid contract address format.")

    def _parse_abi(self):
        for item in self.abi:
            try:
                if item["type"] == "function":
                    func = ABIFunction(**item)
                    self.functions.append(func)
                elif item["type"] == "event":
                    event = ABIEvent(**item)
                    self.events.append(event)
                else:
                    pass
            except ValidationError as e:
                print(f"Error parsing ABI item: {e}")

    def get_function(self, name: str) -> Union[ABIFunction, None]:
        for func in self.functions:
            if func.name == name:
                return func
        print(f"No function found with name: {name}")
        return None

    def get_event(self, name: str) -> Union[ABIEvent, None]:
        for event in self.events:
            if event.name == name:
                return event
        print(f"No event found with name: {name}")
        return None

    def list_functions(self) -> List[str]:
        return [func.name for func in self.functions]

    def list_events(self) -> List[str]:
        return [event.name for event in self.events]

    
def get_abi(contract_address: str, chain_id: int) -> ABIDecoder:
    """
    Get the ABI of a contract by its address.
    Find JSON file in data/chain_id/contract_address.json
    param contract_address: str
    param chain_id: int
    return: ABIDecoder class
    """
    abi_path = f"data/{chain_id}/{contract_address}.json"
    try:
        with open(abi_path, "r") as f:
            abi = json.load(f)
            return ABIDecoder(abi, contract_address)
    except FileNotFoundError:
        return []
