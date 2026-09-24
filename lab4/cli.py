from vehicle import VehicleFactory
from trip import Trip
from calculator import TripCostCalculator
from config import AppSettings
from fuel_price_adapter import FuelPriceAdapter
from decorators import TollRoadDecorator, ParkingDecorator, PenaltyDecorator


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


def get_fuel_price() -> float:
    """
    Цену топлива можно ввести вручную или получить из внешнего сервиса
    через FuelPriceAdapter — калькулятору неважно, откуда взялось число.
    """
    source = input(
        "Откуда взять цену топлива — ввести вручную (m) "
        "или получить из внешнего сервиса (e)? [m]: "
    ).strip().lower() or "m"

    if source != "e":
        return get_float("Цена топлива (руб/л): ")

    fuel_type = input("Тип топлива (АИ-92 / АИ-95 / ДТ): ").strip().upper()
    adapter = FuelPriceAdapter()
    price = adapter.get_price_per_liter(fuel_type)
    print(f"Цена топлива из внешнего сервиса: {price:.2f} руб/л")
    return price


def apply_decorators(calculator):
    """
    Декоратор (Decorator): пользователь может наложить сверху расчёта
    любое количество наценок в любом порядке — каждая следующая оборачивает
    предыдущий результат, не меняя код TripCostCalculator.
    """
    menu = {
        "1": ("Платная дорога", TollRoadDecorator),
        "2": ("Парковка", ParkingDecorator),
        "3": ("Штраф", PenaltyDecorator),
    }
    while True:
        print("\nДобавить наценку сверху? 1 — платная дорога, 2 — парковка, "
              "3 — штраф, Enter — пропустить")
        choice = input("Выбор: ").strip()
        if choice not in menu:
            break
        label, decorator_cls = menu[choice]
        amount = get_float(f"Сумма ({label.lower()}), руб: ")
        calculator = decorator_cls(calculator, amount)
        print(f"Добавлено: {label} = {amount:.2f} руб")
    return calculator


def main():
    print("=== Расчёт стоимости поездки ===\n")

    # AppSettings() — обращение к Одиночке. Это тот же самый объект,
    # который позже создаст (точнее, переиспользует) TripCostCalculator.
    settings = AppSettings(currency="руб", decimal_places=2)

    try:
        vehicle_type = input("Тип ТС (car / taxi / carsharing) [car]: ").strip().lower() or "car"
        fuel_consumption = get_float("Расход топлива (л/100км): ")
        fuel_price = get_fuel_price()
        distance = get_float("Расстояние поездки (км): ")
        passengers = get_int("Количество пассажиров: ")

        extra_costs = []
        while True:
            answer = input("Добавить доп. расход (платная дорога, парковка)? (y/n): ").strip().lower()
            if answer != "y":
                break
            cost = get_float("Сумма доп. расхода (руб): ")
            extra_costs.append(cost)

        # Фабричный метод: сами не решаем, какой класс вызывать (Car/Taxi/
        # CarSharing) — просто просим фабрику создать нужное ТС по строке.
        vehicle = VehicleFactory.create_vehicle(vehicle_type, fuel_consumption, fuel_price)
        trip = Trip(distance, passengers, extra_costs)
        calculator = TripCostCalculator(vehicle, trip)

        # Декоратор: наценки накладываются поверх готового расчёта.
        calculator = apply_decorators(calculator)

        print_result(calculator, trip, settings)

        # Прототип: считаем «похожую» поездку, не вводя всё заново.
        answer = input("\nПосчитать похожую поездку с другим числом пассажиров? (y/n): ").strip().lower()
        if answer == "y":
            new_passengers = get_int("Новое количество пассажиров: ")
            similar_trip = trip.clone(passengers=new_passengers)
            similar_calculator = TripCostCalculator(vehicle, similar_trip)
            print_result(similar_calculator, similar_trip, settings)

    except ValueError as e:
        print(f"\nОшибка ввода: {e}")


def print_result(calculator, trip, settings):
    cur = settings.currency
    print(f"\n--- Результат ({calculator.vehicle!r}) ---")
    print(f"Израсходовано топлива: {calculator.fuel_liters_used():.2f} л")
    print(f"Стоимость топлива: {calculator.fuel_cost():.2f} {cur}")
    print(f"Доп. расходы (заданы при создании поездки): {trip.total_extra_costs():.2f} {cur}")
    print(f"Итоговая стоимость (с учётом наценок-декораторов): {calculator.total_cost():.2f} {cur}")
    print(f"Стоимость на одного пассажира: {calculator.cost_per_passenger():.2f} {cur}")


if __name__ == "__main__":
    main()
