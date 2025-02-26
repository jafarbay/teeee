from web3 import Web3
from eth_account import Account
import random
import string

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_email():
    return f"{random_string(8)}@example.com"

def send_mail_transaction(private_keys, rpc_url="https://soneium.drpc.org", chain_id=1868, contract_address="0x1922Fc53604ED1dC495f15C585acE17fb0e47e48"):
    # ABI с нужными функциями
    abi = [
        {
            "inputs": [],
            "name": "feeAmount",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "string", "name": "to", "type": "string"},
                {"internalType": "string", "name": "path", "type": "string"}
            ],
            "name": "send_mail",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        }
    ]
    
    # Подключение к сети
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    assert w3.is_connected(), "Ошибка подключения к RPC"
    
    contract = w3.eth.contract(address=contract_address, abi=abi)
    fee_amount = contract.functions.feeAmount().call()
    
    transactions = []
    
    for private_key in private_keys:
        account = Account.from_key(private_key)
        recipient_email = random_email()
        file_path = random_string(12)

        estimated_gas = contract.functions.send_mail(recipient_email, file_path).estimate_gas({
            'from': account.address,
            'value': fee_amount
        })

        tx = contract.functions.send_mail(recipient_email, file_path).build_transaction({
            'from': account.address,
            'value': fee_amount,
            'gas': estimated_gas,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': chain_id
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction sent! Hash: {w3.to_hex(tx_hash)}")
        transactions.append(w3.to_hex(tx_hash))
    
    return transactions
