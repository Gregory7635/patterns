import threading
import time

from external_fuel_price_api import ExternalFuelPriceAPI
from fuel_price_adapter import FuelPriceAdapter
from thread_pool import ThreadPool

FUEL_TYPES = ["АИ-92", "АИ-95", "ДТ"]


def main():
    api = ExternalFuelPriceAPI()
    api.delay = 0.5                       # каждый запрос к сервису «идёт по сети» 0.5 с
    adapter = FuelPriceAdapter(api)

    def fetch(fuel_type):
        price = adapter.get_price_per_liter(fuel_type)
        return fuel_type, price, threading.current_thread().name

    print("=== Без пула: запросы по очереди ===")
    start = time.perf_counter()
    for fuel_type in FUEL_TYPES:
        fuel, price, thread = fetch(fuel_type)
        print(f"  {fuel}: {price:.2f} руб/л  (поток {thread})")
    print(f"  Время: {time.perf_counter() - start:.2f} с")

    with ThreadPool(workers=3) as pool:
        print(f"\n=== Пул из {pool.size} потоков: запросы параллельно ===")
        start = time.perf_counter()
        for fuel, price, thread in pool.map(fetch, FUEL_TYPES):
            print(f"  {fuel}: {price:.2f} руб/л  (поток {thread})")
        print(f"  Время: {time.perf_counter() - start:.2f} с")

        print("\n=== 6 запросов на 3 потока: потоки берут задачи из очереди ===")
        threads_before = threading.active_count()
        start = time.perf_counter()
        for fuel, price, thread in pool.map(fetch, FUEL_TYPES * 2):
            print(f"  {fuel}: {price:.2f} руб/л  (поток {thread})")
        print(f"  Время: {time.perf_counter() - start:.2f} с")
        print(f"  Потоков в программе до и после: {threads_before} и {threading.active_count()}"
              f" — новые потоки не создавались")

    print(f"\nПул остановлен, живых потоков: {threading.active_count()} (только главный)")


if __name__ == "__main__":
    main()
