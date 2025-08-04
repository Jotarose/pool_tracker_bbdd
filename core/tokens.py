from web3 import Web3

# Sacar nombre, simbolo y decimales del token
def get_token_info(w3, token_address):
    try:
        erc20_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "name",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function",
            }
        ]

        token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)
        name = token_contract.functions.name().call()
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
        
        return {"name": name, "symbol": symbol, "decimals": decimals}

    except Exception as e:
        print(f"❌ Error al obtener información del token {token_address}: {e}")
        return {"name": "N/A", "symbol": "N/A"}