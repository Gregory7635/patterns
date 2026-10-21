import math
from abc import ABC, abstractmethod


class PricingStrategy(ABC):
    """
    Интерфейс стратегии (Strategy).

    Стратегия отвечает за один вопрос: как из стоимости топлива и
    дополнительных расходов получить итоговую сумму поездки. Калькулятор
    вызывает calculate() и не знает, какой именно тариф за ним стоит.
    """

    name = ""

    @abstractmethod
    def calculate(self, fuel_cost: float, extra_costs: float, decimal_places: int) -> float:
        ...


class LinearTariffStrategy(PricingStrategy):
    """Линейный тариф: топливо + доп. расходы, округление по настройкам."""

    name = "Линейный тариф"

    def calculate(self, fuel_cost: float, extra_costs: float, decimal_places: int) -> float:
        return round(fuel_cost + extra_costs, decimal_places)


class SurchargeTariffStrategy(PricingStrategy):
    """Тариф с наценкой: к сумме добавляется процент, результат округляется вверх до рубля."""

    name = "Тариф с наценкой"

    def __init__(self, markup_percent: float = 20.0):
        if markup_percent < 0:
            raise ValueError("Наценка не может быть отрицательной")
        self.markup_percent = markup_percent

    def calculate(self, fuel_cost: float, extra_costs: float, decimal_places: int) -> float:
        total = (fuel_cost + extra_costs) * (1 + self.markup_percent / 100)
        return float(math.ceil(total))
