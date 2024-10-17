class SendTransaction:
    def __init__(self, w3, from_address, to_address, amount, gas_limit, gas_price):
        self.w3 = w3
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.gas_limit = gas_limit
        self.gas_price = gas_price
        self.tx = None
        self.tx_hash = None

    def build(self):
        nonce = self.w3.eth.get_transaction_count(self.from_address)
        tx = {
            'nonce': nonce,
            'to': self.to_address,
            'value': self.amount,
            'gas': self.gas_limit,
            'gasPrice': self.gas_price,
        }
        return tx
    
    def sign(self):
        tx = self.build()
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.from_address)
        return signed_tx

    def send(self):
        signed_tx = self.sign()
        self.tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.tx_hash