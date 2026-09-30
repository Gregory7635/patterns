from dataclasses import dataclass

from config import AppSettings
from vehicle import Vehicle, VehicleFactory
from trip import Trip
from calculator import TripCostCalculator
from fuel_price_adapter import IFuelPriceProvider, FuelPriceAdapter
from fuel_price_proxy import CachingFuelPriceProxy
from decorators import TollRoadDecorator, ParkingDecorator, PenaltyDecorator
from trip_history import TripHistory
from validators import build_validation_chain


@dataclass
class TripCostResult:
    """
    Готовый результат расчёта — «плоский» набор чисел, который удобно
    печатать. Клиенту не нужно вызывать методы калькулятора и декораторов:
    всё уже посчитано и лежит в полях.
    """
    vehicle: Vehicle
    trip: Trip
    fuel_price: float
    surcharges: list          # список наценок вида [("toll", 500.0), ...]
    fuel_liters: float
    fuel_cost: float
    extra_costs: float
    total_cost: float
    cost_per_passenger: float
    currency: str


class TripCostFacade:
    """
    Фасад (Facade).

    Даёт клиентскому коду (cli.py) ОДИН простой метод calculate() вместо
    целой цепочки действий над разными классами подсистемы:

        1. получить цену топлива        (FuelPriceAdapter / ручной ввод)
        2. создать транспортное средство (VehicleFactory)
        3. создать поездку               (Trip)
        4. создать калькулятор           (TripCostCalculator)
        5. обернуть его наценками        (TollRoad/Parking/PenaltyDecorator)

    Клиент больше не импортирует эти классы и не знает ни их порядка, ни
    того, что внутри вообще есть адаптер, фабрика или декораторы. Если
    подсистема изменится (например, появится новый вид наценки), правится
    только фасад — код клиента остаётся прежним.
    """

    # Ключи, которыми клиент называет наценки, -> классы-декораторы.
    _SURCHARGE_TYPES = {
        "toll": TollRoadDecorator,
        "parking": ParkingDecorator,
        "penalty": PenaltyDecorator,
    }

    def __init__(self, price_provider: IFuelPriceProvider = None):
        # Заместитель: по умолчанию цены берутся не у адаптера напрямую,
        # а через кэширующий прокси, который стоит перед адаптером.
        self._price_provider = price_provider or CachingFuelPriceProxy(FuelPriceAdapter())
        # Итератор: история всех поездок, посчитанных этим фасадом.
        self._history = TripHistory()
        # Цепочка обязанностей: каждый обработчик проверяет своё условие
        # (тип ТС, расход топлива, расстояние...) и передаёт запрос дальше.
        self._validator = build_validation_chain(VehicleFactory._TYPES, self._SURCHARGE_TYPES)

    def calculate(self, vehicle_type: str, fuel_consumption: float, distance_km: float,
                  passengers: int = 1, fuel_price: float = None, fuel_type: str = None,
                  extra_costs: list = None, surcharges: list = None) -> TripCostResult:
        """
        Единая точка входа: принимает «сырые» данные, возвращает готовый результат.

        fuel_price  — цена топлива, введённая вручную;
        fuel_type   — либо тип топлива («АИ-95»), тогда цена возьмётся из внешнего сервиса;
        surcharges  — наценки поверх расчёта: [("toll", 500), ("parking", 200)].
        """
        self._validator.handle({
            "vehicle_type": vehicle_type,
            "fuel_consumption": fuel_consumption,
            "distance_km": distance_km,
            "passengers": passengers,
            "fuel_price": fuel_price,
            "fuel_type": fuel_type,
            "extra_costs": extra_costs,
            "surcharges": surcharges,
        })
        price = self._resolve_fuel_price(fuel_price, fuel_type)
        vehicle = VehicleFactory.create_vehicle(vehicle_type, fuel_consumption, price)
        trip = Trip(distance_km, passengers, extra_costs)
        return self._build_result(vehicle, trip, price, list(surcharges or []))

    def calculate_similar(self, previous: TripCostResult, **overrides) -> TripCostResult:
        """
        «Похожая» поездка: копия предыдущей (Trip.clone) с изменёнными
        полями, например passengers=3. Наценки сохраняются.
        """
        similar_trip = previous.trip.clone(**overrides)
        return self._build_result(previous.vehicle, similar_trip,
                                  previous.fuel_price, list(previous.surcharges))

    def get_history(self) -> TripHistory:
        """
        Доступ к истории поездок. Возвращает саму коллекцию (Iterable),
        а не список внутри неё — обойти её можно только через итератор:
        history.create_iterator().
        """
        return self._history

    def get_fuel_price(self, fuel_type: str) -> float:
        """
        Цена топлива по его типу из внешнего сервиса. Отдельный метод нужен,
        чтобы клиент мог сразу показать цену (или ошибку про неизвестный тип
        топлива), не дожидаясь конца ввода остальных данных.
        """
        return self._price_provider.get_price_per_liter(fuel_type)

    def _resolve_fuel_price(self, fuel_price, fuel_type) -> float:
        if fuel_price is not None:
            return fuel_price
        if fuel_type is not None:
            return self.get_fuel_price(fuel_type)
        raise ValueError("Укажите цену топлива (fuel_price) или тип топлива (fuel_type)")

    def _build_result(self, vehicle, trip, fuel_price, surcharges) -> TripCostResult:
        calculator = TripCostCalculator(vehicle, trip)
        for kind, amount in surcharges:
            decorator_cls = self._SURCHARGE_TYPES.get(kind)
            if decorator_cls is None:
                raise ValueError(
                    f"Неизвестная наценка: {kind!r}. Доступные: {', '.join(self._SURCHARGE_TYPES)}"
                )
            calculator = decorator_cls(calculator, amount)

        result = TripCostResult(
            vehicle=vehicle,
            trip=trip,
            fuel_price=fuel_price,
            surcharges=surcharges,
            fuel_liters=calculator.fuel_liters_used(),
            fuel_cost=calculator.fuel_cost(),
            extra_costs=trip.total_extra_costs(),
            total_cost=calculator.total_cost(),
            cost_per_passenger=calculator.cost_per_passenger(),
            currency=AppSettings().currency,
        )

        # Каждый успешный расчёт (обычный и "похожий") попадает в историю
        # автоматически — клиенту не нужно вызывать это отдельно.
        self._history.add(result)
        return result
