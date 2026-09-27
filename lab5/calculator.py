from vehicle import Vehicle
from trip import Trip
from config import AppSettings


class TripCostCalculator:
    """
    Вычисляет стоимость поездки на основе параметров автомобиля и поездки.

    Точность округления берётся из единственного экземпляра AppSettings
    (Одиночка) — благодаря этому, если где-то в приложении настройки
    поменяют (например, decimal_places=0), калькулятор сразу же
    почувствует это изменение без передачи параметров вручную.
    """

    def __init__(self, vehicle: Vehicle, trip: Trip):
        self.vehicle = vehicle
        self.trip = trip
        self.settings = AppSettings()  # тот же самый объект, что и везде в приложении

    def fuel_liters_used(self) -> float:
        return (self.trip.distance_km / 100) * self.vehicle.fuel_consumption

    def fuel_cost(self) -> float:
        return round(self.fuel_liters_used() * self.vehicle.fuel_price, self.settings.decimal_places)

    def total_cost(self) -> float:
        return round(self.fuel_cost() + self.trip.total_extra_costs(), self.settings.decimal_places)

    def cost_per_passenger(self) -> float:
        return round(self.total_cost() / self.trip.passengers, self.settings.decimal_places)
