from web3 import Web3
from solcx import compile_source, install_solc, set_solc_version

def deploy_contract(private_keys, rpc_url="https://soneium.drpc.org", chain_id=1868):
    # Установка и выбор версии Solidity
    install_solc("0.8.0")
    set_solc_version("0.8.0")

    # Подключение к сети
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    assert web3.is_connected(), "Ошибка подключения к RPC"

    # Минимальный смарт-контракт (только конструктор)
    minimal_contract = """
    pragma solidity ^0.8.0;
    contract Minimal {
        constructor() {}
    }
    """

    # Компиляция контракта
    compiled_sol = compile_source(minimal_contract, output_values=["abi", "bin"])
    contract_data = next(iter(compiled_sol.values()))
    MinimalContract = web3.eth.contract(abi=contract_data["abi"], bytecode=contract_data["bin"])

    deployed_addresses = []
    
    for private_key in private_keys:
        # Получение адреса из приватного ключа
        account = web3.eth.account.from_key(private_key)
        owner_address = account.address

        # Определение оптимального газа
        gas_estimate = MinimalContract.constructor().estimate_gas({"from": owner_address})
        gas_price = web3.eth.gas_price

        # Подготовка транзакции
        tx = MinimalContract.constructor().build_transaction({
            "from": owner_address,
            "nonce": web3.eth.get_transaction_count(owner_address),
            "gas": int(gas_estimate * 1.1),  # Запас 10%
            "gasPrice": gas_price,
            "chainId": chain_id
        })

        # Подписание и отправка транзакции
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Транзакция отправлена: {tx_hash.hex()}")

        # Ожидание подтверждения
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Контракт развернут по адресу: {receipt.contractAddress}")
        deployed_addresses.append(receipt.contractAddress)
    
    return deployed_addresses