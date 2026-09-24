class Vehicle:
    """
    Транспортное средство: хранит расход топлива и цену топлива.
    """

    def __init__(self, fuel_consumption_l_per_100km: float, fuel_price_per_liter: float):
        if fuel_consumption_l_per_100km <= 0:
            raise ValueError("Расход топлива должен быть положительным числом")
        if fuel_price_per_liter <= 0:
            raise ValueError("Цена топлива должна быть положительным числом")

        self.fuel_consumption = fuel_consumption_l_per_100km
        self.fuel_price = fuel_price_per_liter

    def __repr__(self):
        return (f"Vehicle(fuel_consumption={self.fuel_consumption} л/100км, "
                f"fuel_price={self.fuel_price} руб/л)")


class Car(Vehicle):
    """Личный автомобиль — обычное транспортное средство без наценок."""
    pass


class Taxi(Vehicle):
    """
    Такси: помимо расхода топлива у него есть сервисный сбор за километр
    (используется тарификацией в будущих лабораторных, здесь — для примера
    того, что фабрика может создавать продукты с разными наборами полей).
    """

    def __init__(self, fuel_consumption_l_per_100km, fuel_price_per_liter, service_fee_per_km=5.0):
        super().__init__(fuel_consumption_l_per_100km, fuel_price_per_liter)
        self.service_fee_per_km = service_fee_per_km

    def __repr__(self):
        return super().__repr__().replace("Vehicle(", "Taxi(") \
            .replace(")", f", service_fee_per_km={self.service_fee_per_km})")


class CarSharing(Vehicle):
    """Каршеринг: есть фиксированная плата за старт аренды."""

    def __init__(self, fuel_consumption_l_per_100km, fuel_price_per_liter, unlock_fee=50.0):
        super().__init__(fuel_consumption_l_per_100km, fuel_price_per_liter)
        self.unlock_fee = unlock_fee

    def __repr__(self):
        return super().__repr__().replace("Vehicle(", "CarSharing(") \
            .replace(")", f", unlock_fee={self.unlock_fee})")


class VehicleFactory:
    """
    Фабричный метод (Factory Method).

    Инкапсулирует создание объектов Vehicle: вызывающий код не решает
    сам, какой конструктор (Car, Taxi, CarSharing) вызвать — он просто
    просит фабрику создать транспортное средство нужного типа по строке.
    Это упрощает добавление новых типов ТС в будущем: не придётся менять
    код там, где транспортное средство используется — только саму фабрику.
    """

    _TYPES = {
        "car": Car,
        "taxi": Taxi,
        "carsharing": CarSharing,
    }

    @classmethod
    def create_vehicle(cls, vehicle_type: str, fuel_consumption_l_per_100km: float,
                        fuel_price_per_liter: float) -> Vehicle:
        vehicle_type = vehicle_type.strip().lower()
        vehicle_cls = cls._TYPES.get(vehicle_type)
        if vehicle_cls is None:
            raise ValueError(
                f"Неизвестный тип ТС: {vehicle_type!r}. Доступные: {', '.join(cls._TYPES)}"
            )
        return vehicle_cls(fuel_consumption_l_per_100km, fuel_price_per_liter)
