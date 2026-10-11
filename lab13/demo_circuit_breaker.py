from external_fuel_price_api import ExternalFuelPriceAPI, ServiceUnavailableError
from fuel_price_adapter import FuelPriceAdapter
from fuel_price_proxy import CachingFuelPriceProxy
from circuit_breaker import CircuitBreaker, GuardedFuelPriceProvider
from trip_cost_facade import TripCostFacade


class FakeClock:
    """Управляемое время, чтобы не ждать 30 секунд в демонстрации."""
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def ask(facade, fuel_type, api):
    before = api.calls
    try:
        price = facade.get_fuel_price(fuel_type)
        print(f"  {fuel_type}: {price:.2f} руб/л")
    except ServiceUnavailableError as e:
        print(f"  {fuel_type}: ОШИБКА — {e}")
    print(f"  (обращений к внешнему сервису: {api.calls - before})")


def main():
    clock = FakeClock()
    api = ExternalFuelPriceAPI()
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30, clock=clock)
    # Цепочка: Фасад -> Прокси (кэш) -> Предохранитель -> Адаптер -> внешний сервис
    facade = TripCostFacade(price_provider=CachingFuelPriceProxy(
        GuardedFuelPriceProvider(FuelPriceAdapter(api), breaker)))

    print("=== Сервис работает ===")
    ask(facade, "АИ-92", api)

    print("\n=== Сервис упал: три сбоя подряд размыкают цепь ===")
    api.available = False
    for _ in range(3):
        ask(facade, "АИ-95", api)

    print("\n=== Цепь разомкнута: отказ сразу, сервис не нагружается ===")
    ask(facade, "АИ-95", api)

    print("\n=== Кэш прокси работает и при разомкнутой цепи ===")
    ask(facade, "АИ-92", api)

    print("\n=== Прошло 30 с, сервис восстановился: пробный запрос ===")
    clock.now = 30
    api.available = True
    ask(facade, "АИ-95", api)
    print(f"  Состояние предохранителя: {breaker.state.value}")


if __name__ == "__main__":
    main()
