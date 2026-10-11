from config import AppSettings
from settings_history import SettingsCaretaker
from trip_cost_facade import TripCostFacade, TripCostResult
from observers import ITripObserver, RunningTotalObserver


class TripModel:
    """
    Модель (Model) в паттерне MVC.

    Хранит данные и бизнес-логику приложения: считает поездки (через фасад),
    помнит последний результат и историю, управляет тарифом и настройками.
    Модель ничего не знает ни о консоли, ни о том, кто её вызывает:
    в ней нет ни одного input() или print().
    """

    def __init__(self, facade: TripCostFacade = None):
        AppSettings(currency="руб", decimal_places=2)
        self._facade = facade or TripCostFacade()
        self._caretaker = SettingsCaretaker(AppSettings())
        self._totals = RunningTotalObserver()
        self._facade.subscribe(self._totals)
        self.last_result: TripCostResult = None

    # --- расчёт поездок ---
    def calculate(self, vehicle_type, fuel_consumption, distance_km, passengers,
                  fuel_price, extra_costs, surcharges) -> TripCostResult:
        self.last_result = self._facade.calculate(
            vehicle_type, fuel_consumption, distance_km, passengers,
            fuel_price=fuel_price, extra_costs=extra_costs, surcharges=surcharges)
        return self.last_result

    def calculate_similar(self, previous: TripCostResult, **overrides) -> TripCostResult:
        self.last_result = self._facade.calculate_similar(previous, **overrides)
        return self.last_result

    def get_fuel_price(self, fuel_type: str) -> float:
        return self._facade.get_fuel_price(fuel_type)

    # --- тариф (Стратегия) ---
    def set_tariff(self, tariff: str) -> None:
        self._facade.set_tariff(tariff)

    def get_tariff(self) -> str:
        return self._facade.get_tariff()

    # --- история (Итератор) ---
    def get_history(self, newest_first: bool = True) -> list:
        iterator = self._facade.get_history().create_iterator(reverse=newest_first)
        items = []
        while iterator.has_next():
            items.append(iterator.next())
        return items

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
