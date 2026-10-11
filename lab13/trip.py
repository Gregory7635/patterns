import copy


class Trip:
    """
    Поездка: дистанция, количество пассажиров и дополнительные расходы
    (платные дороги, парковка и т.д.).
    """

    def __init__(self, distance_km: float, passengers: int = 1, extra_costs=None):
        if distance_km <= 0:
            raise ValueError("Расстояние должно быть положительным числом")
        if passengers <= 0:
            raise ValueError("Количество пассажиров должно быть положительным числом")

        self.distance_km = distance_km
        self.passengers = passengers
        self.extra_costs = extra_costs if extra_costs is not None else []

    def total_extra_costs(self) -> float:
        return sum(self.extra_costs)

    def clone(self, **overrides) -> "Trip":
        """
        Прототип (Prototype).

        Создаёт полную копию текущей поездки (глубокое копирование, чтобы
        список extra_costs не был общим с оригиналом), а затем применяет
        переданные изменения. Это дешевле и удобнее, чем заново собирать
        объект Trip через конструктор и переспрашивать все параметры —
        особенно если нужно посчитать «почти такую же» поездку, изменив
        всего одно значение (например, количество пассажиров).
        """
        clone = copy.deepcopy(self)
        for field, value in overrides.items():
            setattr(clone, field, value)
        return clone

    def __repr__(self):
        return (f"Trip(distance_km={self.distance_km}, passengers={self.passengers}, "
                f"extra_costs={self.extra_costs})")
