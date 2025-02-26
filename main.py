import random
import time
from concurrent.futures import ThreadPoolExecutor
from deploy import deploy_contract
from dmail import send_mail_transaction
from web3 import Web3

# Функция для чтения приватных ключей из текстового файла
def read_private_keys(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]

# Функция для рандомной задержки
def random_delay(min_delay=5, max_delay=10):
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)
    print(f"Задержка {delay:.2f} секунд.")

# Функция для выполнения операций с кошельком
def process_wallet(private_key, rpc_url, chain_id, min_tx=50, max_tx=65):
    # Подключаемся к сети
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # Получаем адрес кошелька
    account = w3.eth.account.from_key(private_key)
    wallet_address = account.address
    
    # Получаем текущий nonce (количество транзакций на кошельке)
    current_nonce = w3.eth.get_transaction_count(wallet_address)
    
    # Случайное количество транзакций для кошелька
    tx_limit = random.randint(min_tx, max_tx)
    
    # Рассчитываем, сколько транзакций нужно выполнить
    transactions_to_make = tx_limit - current_nonce
    if transactions_to_make <= 0:
        print(f"Кошелек {wallet_address}: Уже выполнено достаточно транзакций ({current_nonce}). Пропускаем.")
        return
    
    print(f"\nКошелек {wallet_address}: Ожидается выполнить {transactions_to_make} транзакций. Текущие: {current_nonce}, лимит: {tx_limit}.")
    
    error_count = 0  # Счётчик ошибок для каждого кошелька

    for _ in range(transactions_to_make):
        try:
            # Рандомная вероятность для каждого кошелька
            probability_send_mail = random.random()  # случайная вероятность для отправки письма
            probability_deploy_contract = 1 - probability_send_mail  # оставшаяся вероятность для развертывания контракта

            print(f"Вероятность для отправки письма: {probability_send_mail:.2f}")
            print(f"Вероятность для развертывания контракта: {probability_deploy_contract:.2f}")

            # Случайный выбор функции с учетом вероятностей
            choice = random.random()

            if choice <= probability_send_mail:  # Если случайное число <= вероятности отправки письма
                print(f"Кошелек {wallet_address}: Выбрана функция отправки письма.")
                send_mail_transaction([private_key], rpc_url, chain_id)
            else:  # Иначе выбираем развертывание контракта
                print(f"Кошелек {wallet_address}: Выбрана функция развертывания контракта.")
                deploy_contract([private_key], rpc_url, chain_id)

            # Добавляем случайную задержку между действиями
            random_delay(min_delay=200, max_delay=400)
        
        except Exception as e:
            # В случае ошибки увеличиваем счётчик ошибок
            error_count += 1
            print(f"Ошибка для кошелька {wallet_address}: {e}")
            
            # Если количество ошибок превышает 5, пропускаем этот кошелек
            if error_count >= 5:
                print(f"Кошелек {wallet_address}: Превышен лимит ошибок. Переход к следующему кошельку.")
                return

# Основная функция
def main():
    private_keys = read_private_keys("C:\\soft\\soneium\\private_keys.txt")  # путь к файлу с приватными ключами
    rpc_url = "https://soneium.drpc.org"
    chain_id = 1868
    
    # Запрос количества потоков у пользователя
    num_threads = int(input("Введите количество потоков для запуска: "))

    # Запуск многозадачности с использованием ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for private_key in private_keys:
            # Каждому кошельку выделяется отдельный поток
            executor.submit(process_wallet, private_key, rpc_url, chain_id)

if __name__ == "__main__":
    main()