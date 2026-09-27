from config import AppSettings
from trip_cost_facade import TripCostFacade, TripCostResult


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


def ask_fuel_price(facade: TripCostFacade) -> float:
    """
    Цену топлива можно ввести вручную или получить из внешнего сервиса.
    Во втором случае обращаемся не к адаптеру напрямую, а через фасад.
    """
    source = input(
        "Откуда взять цену топлива — ввести вручную (m) "
        "или получить из внешнего сервиса (e)? [m]: "
    ).strip().lower() or "m"

    if source != "e":
        return get_float("Цена топлива (руб/л): ")

    fuel_type = input("Тип топлива (АИ-92 / АИ-95 / ДТ): ").strip().upper()
    price = facade.get_fuel_price(fuel_type)
    print(f"Цена топлива из внешнего сервиса: {price:.2f} руб/л")
    return price


def ask_surcharges() -> list:
    """
    Собирает наценки в виде простого списка [("toll", 500.0), ...].
    Как именно они накладываются на расчёт (декораторы) — забота фасада.
    """
    menu = {
        "1": ("toll", "Платная дорога"),
        "2": ("parking", "Парковка"),
        "3": ("penalty", "Штраф"),
    }
    surcharges = []
    while True:
        print("\nДобавить наценку сверху? 1 — платная дорога, 2 — парковка, "
              "3 — штраф, Enter — пропустить")
        choice = input("Выбор: ").strip()
        if choice not in menu:
            break
        kind, label = menu[choice]
        amount = get_float(f"Сумма ({label.lower()}), руб: ")
        surcharges.append((kind, amount))
        print(f"Добавлено: {label} = {amount:.2f} руб")
    return surcharges


def main():
    print("=== Расчёт стоимости поездки ===\n")

    # Одиночка: единые настройки приложения.
    AppSettings(currency="руб", decimal_places=2)

    # Фасад: единственный объект подсистемы, который знает клиент.
    facade = TripCostFacade()

    try:
        vehicle_type = input("Тип ТС (car / taxi / carsharing) [car]: ").strip().lower() or "car"
        fuel_consumption = get_float("Расход топлива (л/100км): ")
        fuel_price = ask_fuel_price(facade)
        distance = get_float("Расстояние поездки (км): ")
        passengers = get_int("Количество пассажиров: ")

        extra_costs = []
        while True:
            answer = input("Добавить доп. расход (платная дорога, парковка)? (y/n): ").strip().lower()
            if answer != "y":
                break
            extra_costs.append(get_float("Сумма доп. расхода (руб): "))

        surcharges = ask_surcharges()

        # Весь расчёт — ОДИН вызов. Фабрика, адаптер, Trip, калькулятор
        # и декораторы спрятаны внутри фасада.
        result = facade.calculate(
            vehicle_type, fuel_consumption, distance, passengers,
            fuel_price=fuel_price,
            extra_costs=extra_costs, surcharges=surcharges,
        )
        print_result(result)

        # Прототип (внутри фасада): «похожая» поездка одним вызовом.
        answer = input("\nПосчитать похожую поездку с другим числом пассажиров? (y/n): ").strip().lower()
        if answer == "y":
            new_passengers = get_int("Новое количество пассажиров: ")
            print_result(facade.calculate_similar(result, passengers=new_passengers))

    except ValueError as e:
        print(f"\nОшибка ввода: {e}")


def print_result(result: TripCostResult):
    cur = result.currency
    print(f"\n--- Результат ({result.vehicle!r}) ---")
    print(f"Израсходовано топлива: {result.fuel_liters:.2f} л")
    print(f"Стоимость топлива: {result.fuel_cost:.2f} {cur}")
    print(f"Доп. расходы (заданы при создании поездки): {result.extra_costs:.2f} {cur}")
    print(f"Итоговая стоимость (с учётом наценок): {result.total_cost:.2f} {cur}")
    print(f"Стоимость на одного пассажира: {result.cost_per_passenger:.2f} {cur}")


if __name__ == "__main__":
    main()
