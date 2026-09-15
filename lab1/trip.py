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

    def __repr__(self):
        return (f"Trip(distance_km={self.distance_km}, passengers={self.passengers}, "
                f"extra_costs={self.extra_costs})")
