from vehicle import Vehicle
from trip import Trip
from calculator import TripCostCalculator
from config import AppSettings


def get_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите число")


def get_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число")


def main():
    print("=== Расчёт стоимости поездки ===\n")

    # AppSettings() — обращение к Одиночке. Это тот же самый объект,
    # который позже создаст (точнее, переиспользует) TripCostCalculator.
    settings = AppSettings(currency="руб", decimal_places=2)

    try:
        fuel_consumption = get_float("Расход топлива (л/100км): ")
        fuel_price = get_float("Цена топлива (руб/л): ")
        distance = get_float("Расстояние поездки (км): ")
        passengers = get_int("Количество пассажиров: ")

        extra_costs = []
        while True:
            answer = input("Добавить доп. расход (платная дорога, парковка)? (y/n): ").strip().lower()
            if answer != "y":
                break
            cost = get_float("Сумма доп. расхода (руб): ")
            extra_costs.append(cost)

        vehicle = Vehicle(fuel_consumption, fuel_price)
        trip = Trip(distance, passengers, extra_costs)
        calculator = TripCostCalculator(vehicle, trip)

        cur = settings.currency
        print("\n--- Результат ---")
        print(f"Израсходовано топлива: {calculator.fuel_liters_used():.2f} л")
        print(f"Стоимость топлива: {calculator.fuel_cost():.2f} {cur}")
        print(f"Доп. расходы: {trip.total_extra_costs():.2f} {cur}")
        print(f"Общая стоимость поездки: {calculator.total_cost():.2f} {cur}")
        print(f"Стоимость на одного пассажира: {calculator.cost_per_passenger():.2f} {cur}")

    except ValueError as e:
        print(f"\nОшибка ввода: {e}")


if __name__ == "__main__":
    main()
