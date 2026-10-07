from config import AppSettings
from settings_history import SettingsCaretaker
from trip_cost_facade import TripCostFacade, TripCostResult
from observers import ConsoleLogObserver, RunningTotalObserver


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


def choose_tariff(facade: TripCostFacade):
    """Стратегия: выбор тарифа расчёта. Фасад подставит нужную стратегию в калькулятор."""
    print(f"\nТекущий тариф: {facade.get_tariff()}")
    choice = input("Тариф: 1 — линейный, 2 — с наценкой 20%, Enter — оставить\nВыбор: ").strip()
    if choice in ("1", "2"):
        facade.set_tariff("linear" if choice == "1" else "surcharge")
        print(f"Тариф переключён: {facade.get_tariff()}")


def main():
    print("=== Расчёт стоимости поездки ===\n")

    # Одиночка: единые настройки приложения.
    AppSettings(currency="руб", decimal_places=2)
    # Снимок: хранитель, который умеет откатывать настройки к
    # состоянию до последнего изменения.
    settings_caretaker = SettingsCaretaker(AppSettings())

    # Фасад: единственный объект подсистемы, который знает клиент.
    # Один и тот же фасад (а значит, и один и тот же кэш прокси) живёт
    # всё время работы программы — поэтому можно считать несколько поездок подряд.
    facade = TripCostFacade()

    # Наблюдатель: фасад ничего не знает об этих двух подписчиках заранее —
    # они подписываются снаружи и получают уведомление о каждой новой поездке.
    log_observer = ConsoleLogObserver()
    totals_observer = RunningTotalObserver()
    facade.subscribe(log_observer)
    facade.subscribe(totals_observer)

    while True:
        manage_settings(settings_caretaker)
        choose_tariff(facade)
        run_trip(facade)
        again = input("\nРассчитать другую поездку? (y/n): ").strip().lower()
        if again != "y":
            break
        print()

    print(f"\n{totals_observer.summary()}")


def run_trip(facade: TripCostFacade):
    """Один сеанс расчёта поездки: ввод данных, расчёт, печать результата."""
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

        answer = input("\nПоказать историю всех посчитанных поездок? (y/n): ").strip().lower()
        if answer == "y":
            order = input("Порядок: сначала новые (n) или сначала старые (o)? [n]: ").strip().lower() or "n"
            print_history(facade, reverse=(order != "o"))

    except ValueError as e:
        print(f"\nОшибка ввода: {e}")


def print_result(result: TripCostResult):
    cur = result.currency
    print(f"\n--- Результат ({result.vehicle!r}) ---")
    print(f"Тариф: {result.tariff}")
    print(f"Израсходовано топлива: {result.fuel_liters:.2f} л")
    print(f"Стоимость топлива: {result.fuel_cost:.2f} {cur}")
    print(f"Доп. расходы (заданы при создании поездки): {result.extra_costs:.2f} {cur}")
    print(f"Итоговая стоимость (с учётом наценок): {result.total_cost:.2f} {cur}")
    print(f"Стоимость на одного пассажира: {result.cost_per_passenger:.2f} {cur}")


def manage_settings(caretaker: SettingsCaretaker):
    """
    Снимок: позволяет изменить настройки (валюту, точность округления)
    и при необходимости откатить последнее изменение. Перед каждым
    изменением хранитель сохраняет снимок текущего состояния, поэтому
    откат всегда возвращает ровно то, что было непосредственно перед
    этим изменением (а не какие-то настройки "по умолчанию").
    """
    print(f"\nТекущие настройки: {AppSettings()!r}")
    choice = input(
        "Настройки: 1 — изменить, 2 — отменить последнее изменение, "
        "Enter — пропустить\nВыбор: "
    ).strip()

    if choice == "1":
        caretaker.save(label=repr(AppSettings()))
        currency = input(f"Новая валюта (Enter — оставить {AppSettings().currency!r}): ").strip()
        places_raw = input(
            f"Новая точность округления, знаков (Enter — оставить {AppSettings().decimal_places}): "
        ).strip()
        places = int(places_raw) if places_raw else None
        AppSettings().update(currency=currency or None, decimal_places=places)
        print(f"Сохранено: {AppSettings()!r}")
    elif choice == "2":
        if caretaker.undo():
            print(f"Откат выполнен: {AppSettings()!r}")
        else:
            print("Нет сохранённых снимков — отменять нечего.")


def print_history(facade: TripCostFacade, reverse: bool = True):
    """
    Печатает историю поездок через итератор истории (Iterator), а не
    обычным for по списку: cli.py вообще не знает, что внутри TripHistory
    лежит список — он лишь просит create_iterator() и по одному
    забирает элементы через has_next()/next().
    """
    history = facade.get_history()
    if len(history) == 0:
        print("История пуста.")
        return

    print(f"\n--- История поездок ({len(history)}) ---")
    iterator = history.create_iterator(reverse=reverse)
    n = 1
    while iterator.has_next():
        result = iterator.next()
        print(f"{n}. {result.vehicle!r}: {result.total_cost:.2f} {result.currency} "
              f"({result.cost_per_passenger:.2f} {result.currency}/чел.)")
        n += 1


if __name__ == "__main__":
    main()
