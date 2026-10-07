from abc import ABC, abstractmethod


class ValidationHandler(ABC):
    """
    Обработчик в цепочке обязанностей (Chain of Responsibility).

    Каждый конкретный обработчик отвечает только за одну свою проверку
    (например, «расстояние положительное») и ничего не знает про соседей
    в цепочке. Если проверка не пройдена — обработчик выбрасывает
    ValueError и обработка запроса останавливается. Если проверка
    пройдена — обработчик передаёт запрос дальше по цепочке (следующему
    обработчику), пока не будет проверено всё или цепочка не закончится.
    """

    def __init__(self):
        self._next: "ValidationHandler" = None

    def set_next(self, handler: "ValidationHandler") -> "ValidationHandler":
        """Подключить следующий обработчик. Возвращает его же — удобно
        строить цепочку одной строкой: a.set_next(b).set_next(c)."""
        self._next = handler
        return handler

    def handle(self, request: dict) -> None:
        self._check(request)
        if self._next is not None:
            self._next.handle(request)

    @abstractmethod
    def _check(self, request: dict) -> None:
        """Проверить своё условие в request; при нарушении поднять ValueError."""


class VehicleTypeHandler(ValidationHandler):
    """Тип ТС должен быть одним из известных фабрике VehicleFactory."""

    def __init__(self, known_types):
        super().__init__()
        self._known_types = known_types

    def _check(self, request: dict) -> None:
        vehicle_type = str(request.get("vehicle_type", "")).strip().lower()
        if vehicle_type not in self._known_types:
            raise ValueError(
                f"Неизвестный тип ТС: {vehicle_type!r}. Доступные: {', '.join(self._known_types)}"
            )


class FuelConsumptionHandler(ValidationHandler):
    """Расход топлива должен быть положительным числом."""

    def _check(self, request: dict) -> None:
        if request.get("fuel_consumption", 0) <= 0:
            raise ValueError("Расход топлива должен быть положительным числом")


class DistanceHandler(ValidationHandler):
    """Расстояние поездки должно быть положительным числом."""

    def _check(self, request: dict) -> None:
        if request.get("distance_km", 0) <= 0:
            raise ValueError("Расстояние должно быть положительным числом")


class PassengersHandler(ValidationHandler):
    """Количество пассажиров должно быть положительным целым числом."""

    def _check(self, request: dict) -> None:
        if request.get("passengers", 0) <= 0:
            raise ValueError("Количество пассажиров должно быть положительным числом")


class FuelSourceHandler(ValidationHandler):
    """Должна быть указана хотя бы одна из цен: вручную или по типу топлива."""

    def _check(self, request: dict) -> None:
        if request.get("fuel_price") is None and request.get("fuel_type") is None:
            raise ValueError("Укажите цену топлива (fuel_price) или тип топлива (fuel_type)")


class FuelPriceValueHandler(ValidationHandler):
    """Если цена топлива указана вручную — она должна быть положительной."""

    def _check(self, request: dict) -> None:
        fuel_price = request.get("fuel_price")
        if fuel_price is not None and fuel_price <= 0:
            raise ValueError("Цена топлива должна быть положительным числом")


class ExtraCostsHandler(ValidationHandler):
    """Дополнительные расходы (платная дорога, парковка) не могут быть отрицательными."""

    def _check(self, request: dict) -> None:
        for amount in request.get("extra_costs") or []:
            if amount < 0:
                raise ValueError(f"Доп. расход не может быть отрицательным: {amount}")


class SurchargesHandler(ValidationHandler):
    """Наценки должны быть известного вида и иметь положительную сумму."""

    def __init__(self, known_kinds):
        super().__init__()
        self._known_kinds = known_kinds

    def _check(self, request: dict) -> None:
        for kind, amount in request.get("surcharges") or []:
            if kind not in self._known_kinds:
                raise ValueError(
                    f"Неизвестная наценка: {kind!r}. Доступные: {', '.join(self._known_kinds)}"
                )
            if amount <= 0:
                raise ValueError(f"Сумма наценки {kind!r} должна быть положительным числом")


def build_validation_chain(known_vehicle_types, known_surcharge_kinds) -> ValidationHandler:
    """
    Собирает цепочку в фиксированном порядке и возвращает её первое звено —
    только с ним и должен работать клиент (например, фасад), не заботясь
    о том, сколько всего обработчиков и в каком они порядке.
    """
    handlers = [
        VehicleTypeHandler(known_vehicle_types),
        FuelConsumptionHandler(),
        DistanceHandler(),
        PassengersHandler(),
        FuelSourceHandler(),
        FuelPriceValueHandler(),
        ExtraCostsHandler(),
        SurchargesHandler(known_surcharge_kinds),
    ]
    for current, following in zip(handlers, handlers[1:]):
        current.set_next(following)
    return handlers[0]
