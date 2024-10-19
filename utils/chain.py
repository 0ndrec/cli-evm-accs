from typing import List

class Network:
    def __init__(self, chain_id: int, endpoints: List[str], symbol: str, decimals: int, gas_price: int):
        self.chain_id = chain_id
        self.endpoints = endpoints
        self.symbol = symbol
        self.decimals = decimals
        self.gas_price = gas_price

    def __repr__(self):
        return f"Network (chain_id={self.chain_id}, endpoints={self.endpoints}, symbol={self.symbol}, decimals={self.decimals}, gas_price={self.gas_price})"
    