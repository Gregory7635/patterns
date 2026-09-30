class CostDecorator:
    """
    Базовый декоратор (Decorator).

    Оборачивает объект с итоговой стоимостью (TripCostCalculator или уже
    другой декоратор) и добавляет свою наценку поверх total_cost(), не
    меняя код обёрнутого объекта. Декораторы можно накладывать один на
    другой в любом количестве и порядке — каждый добавляет свою
    «обязанность» (платная дорога, парковка, штраф...) поверх предыдущих.
    """

    def __init__(self, wrapped):
        self._wrapped = wrapped

    def total_cost(self) -> float:
        return round(self._wrapped.total_cost() + self.extra_amount(), 2)

    def cost_per_passenger(self) -> float:
        return round(self.total_cost() / self._wrapped.trip.passengers, 2)

    def extra_amount(self) -> float:
        raise NotImplementedError

    def label(self) -> str:
        raise NotImplementedError

    def __getattr__(self, name):
        # Всё, что декоратор не переопределяет сам (fuel_cost, trip,
        # vehicle...), прозрачно передаётся обёрнутому объекту.
        return getattr(self._wrapped, name)

    def __repr__(self):
        return f"{self.label()} -> {self._wrapped!r}"


class TollRoadDecorator(CostDecorator):
    """Добавляет стоимость проезда по платной дороге."""

    def __init__(self, wrapped, amount: float):
        super().__init__(wrapped)
        self.amount = amount

    def extra_amount(self) -> float:
        return self.amount

    def label(self) -> str:
        return f"Платная дорога: {self.amount:.2f} руб"


class ParkingDecorator(CostDecorator):
    """Добавляет стоимость парковки."""

    def __init__(self, wrapped, amount: float):
        super().__init__(wrapped)
        self.amount = amount

    def extra_amount(self) -> float:
        return self.amount

    def label(self) -> str:
        return f"Парковка: {self.amount:.2f} руб"


class PenaltyDecorator(CostDecorator):
    """Добавляет сумму штрафа (например, за превышение скорости)."""

    def __init__(self, wrapped, amount: float):
        super().__init__(wrapped)
        self.amount = amount

    def extra_amount(self) -> float:
        return self.amount

    def label(self) -> str:
        return f"Штраф: {self.amount:.2f} руб"
