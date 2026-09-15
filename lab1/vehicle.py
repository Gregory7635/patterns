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
