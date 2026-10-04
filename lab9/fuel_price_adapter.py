from abc import ABC, abstractmethod
from external_fuel_price_api import ExternalFuelPriceAPI


class IFuelPriceProvider(ABC):
    """
    Интерфейс, которого ожидает наше приложение: один простой метод,
    возвращающий цену топлива числом.
    """

    @abstractmethod
    def get_price_per_liter(self, fuel_type: str) -> float:
        ...


class FuelPriceAdapter(IFuelPriceProvider):
    """
    Адаптер (Adapter).

    Приводит несовместимый интерфейс ExternalFuelPriceAPI (метод fetch_price,
    возвращающий словарь с несколькими полями) к интерфейсу IFuelPriceProvider,
    который ожидает остальная часть приложения (метод get_price_per_liter,
    возвращающий обычное число float).

    Благодаря адаптеру cli.py и калькулятор вообще не знают об устройстве
    внешнего сервиса — они работают только с IFuelPriceProvider. Если завтра
    сменится сторонний сервис (или его формат ответа), достаточно поменять
    один класс-адаптер, не трогая остальной код.
    """

    def __init__(self, external_api: ExternalFuelPriceAPI = None):
        self._external_api = external_api or ExternalFuelPriceAPI()

    def get_price_per_liter(self, fuel_type: str) -> float:
        raw_response = self._external_api.fetch_price(fuel_type)
        return raw_response["price_rub_per_liter"]
