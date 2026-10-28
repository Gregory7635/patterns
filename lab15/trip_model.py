from config import AppSettings
from settings_history import SettingsCaretaker
from trip_cost_facade import TripCostFacade, TripCostResult
from observers import ITripObserver, RunningTotalObserver
from trip_repository import ITripRepository, InMemoryTripRepository
from thread_pool import ThreadPool


class TripModel:
    """
    Модель (Model) в паттерне MVC.

    Хранит данные и бизнес-логику приложения: считает поездки (через фасад),
    помнит последний результат и историю, управляет тарифом и настройками.
    Модель ничего не знает ни о консоли, ни о том, кто её вызывает:
    в ней нет ни одного input() или print().
    """

    FUEL_TYPES = ("АИ-92", "АИ-95", "ДТ")

    def __init__(self, facade: TripCostFacade = None, repository: ITripRepository = None,
                 pool: ThreadPool = None):
        AppSettings(currency="руб", decimal_places=2)
        self._facade = facade or TripCostFacade()
        self._caretaker = SettingsCaretaker(AppSettings())
        # Репозиторий: хранилище посчитанных поездок (в памяти или в файле).
        # (is None, а не «or»: пустой репозиторий имеет len() == 0 и считался бы ложным)
        self._repository = repository if repository is not None else InMemoryTripRepository()
        # Пул потоков: один на всю модель, его потоки переиспользуются между запросами.
        self._pool = pool if pool is not None else ThreadPool(workers=3)
        self._totals = RunningTotalObserver()
        self._facade.subscribe(self._totals)
        self.last_result: TripCostResult = None

    # --- расчёт поездок ---
    def calculate(self, vehicle_type, fuel_consumption, distance_km, passengers,
                  fuel_price, extra_costs, surcharges) -> TripCostResult:
        self.last_result = self._facade.calculate(
            vehicle_type, fuel_consumption, distance_km, passengers,
            fuel_price=fuel_price, extra_costs=extra_costs, surcharges=surcharges)
        self._repository.add(self.last_result)
        return self.last_result

    def calculate_similar(self, previous: TripCostResult, **overrides) -> TripCostResult:
        self.last_result = self._facade.calculate_similar(previous, **overrides)
        self._repository.add(self.last_result)
        return self.last_result

    def get_fuel_price(self, fuel_type: str) -> float:
        return self._facade.get_fuel_price(fuel_type)

    def get_fuel_prices(self, fuel_types=FUEL_TYPES) -> dict:
        """Цены сразу на несколько видов топлива: запросы к сервису идут параллельно в пуле."""
        prices = self._pool.map(self._facade.get_fuel_price, fuel_types)
        return dict(zip(fuel_types, prices))

    # --- тариф (Стратегия) ---
    def set_tariff(self, tariff: str) -> None:
        self._facade.set_tariff(tariff)

    def get_tariff(self) -> str:
        return self._facade.get_tariff()

    # --- история (Репозиторий) ---
    def get_history(self, newest_first: bool = True) -> list:
        items = self._repository.get_all()
        return items[::-1] if newest_first else items

    def get_trips_by_tariff(self, tariff: str) -> list:
        return self._repository.find_by_tariff(tariff)

    # --- настройки (Одиночка + Снимок) ---
    def get_settings(self) -> str:
        return repr(AppSettings())

    def get_currency(self) -> str:
        return AppSettings().currency

    def get_decimal_places(self) -> int:
        return AppSettings().decimal_places

    def change_settings(self, currency: str = None, decimal_places: int = None) -> None:
        self._caretaker.save(label=repr(AppSettings()))
        AppSettings().update(currency=currency, decimal_places=decimal_places)

    def undo_settings(self) -> bool:
        return self._caretaker.undo()

    # --- наблюдатели и итоги ---
    def subscribe(self, observer: ITripObserver) -> None:
        self._facade.subscribe(observer)

    def totals_summary(self) -> str:
        return self._totals.summary()
