class ConsoleTripView:
    """
    Представление (View) в паттерне MVC.

    Отвечает только за общение с пользователем: показывает данные и читает
    ввод. Здесь все input() и print() приложения. Никаких расчётов и решений
    «что делать дальше» — их делают модель и контроллер. Консольное
    представление можно заменить другим (например, графическим), не меняя
    ни модель, ни контроллер.
    """

    # --- низкоуровневый ввод ---
    @staticmethod
    def _get_float(prompt: str) -> float:
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Ошибка: введите число")

    @staticmethod
    def _get_int(prompt: str) -> int:
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Ошибка: введите целое число")

    @staticmethod
    def ask_yes_no(prompt: str) -> bool:
        return input(prompt).strip().lower() == "y"

    # --- заголовок и настройки ---
    def show_title(self) -> None:
        print("=== Расчёт стоимости поездки ===\n")

    def ask_settings_action(self, settings_text: str) -> str:
        print(f"\nТекущие настройки: {settings_text}")
        return input(
            "Настройки: 1 — изменить, 2 — отменить последнее изменение, "
            "Enter — пропустить\nВыбор: "
        ).strip()

    def ask_new_settings(self, currency: str, decimal_places: int):
        new_currency = input(f"Новая валюта (Enter — оставить {currency!r}): ").strip()
        places_raw = input(
            f"Новая точность округления, знаков (Enter — оставить {decimal_places}): "
        ).strip()
        places = int(places_raw) if places_raw else None
        return new_currency or None, places

    def show_settings_saved(self, settings_text: str) -> None:
        print(f"Сохранено: {settings_text}")

    def show_undo_result(self, done: bool, settings_text: str) -> None:
        if done:
            print(f"Откат выполнен: {settings_text}")
        else:
            print("Нет сохранённых снимков — отменять нечего.")

    # --- тариф ---
    def ask_tariff(self, current: str) -> str:
        print(f"\nТекущий тариф: {current}")
        return input("Тариф: 1 — линейный, 2 — с наценкой 20%, Enter — оставить\nВыбор: ").strip()

    def show_tariff_changed(self, tariff: str) -> None:
        print(f"Тариф переключён: {tariff}")

    # --- ввод данных поездки ---
    def ask_vehicle_type(self) -> str:
        return input("Тип ТС (car / taxi / carsharing) [car]: ").strip().lower() or "car"

    def ask_fuel_consumption(self) -> float:
        return self._get_float("Расход топлива (л/100км): ")

    def ask_fuel_source(self) -> str:
        return input(
            "Откуда взять цену топлива — ввести вручную (m) "
            "или получить из внешнего сервиса (e)? [m]: "
        ).strip().lower() or "m"

    def ask_fuel_price(self) -> float:
        return self._get_float("Цена топлива (руб/л): ")

    def ask_fuel_type(self) -> str:
        return input("Тип топлива (АИ-92 / АИ-95 / ДТ): ").strip().upper()

    def show_fuel_price(self, price: float) -> None:
        print(f"Цена топлива из внешнего сервиса: {price:.2f} руб/л")

    def ask_distance(self) -> float:
        return self._get_float("Расстояние поездки (км): ")

    def ask_passengers(self, prompt: str = "Количество пассажиров: ") -> int:
        return self._get_int(prompt)

    def ask_extra_costs(self) -> list:
        extra_costs = []
        while self.ask_yes_no("Добавить доп. расход (платная дорога, парковка)? (y/n): "):
            extra_costs.append(self._get_float("Сумма доп. расхода (руб): "))
        return extra_costs

    def ask_surcharges(self) -> list:
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
            amount = self._get_float(f"Сумма ({label.lower()}), руб: ")
            surcharges.append((kind, amount))
            print(f"Добавлено: {label} = {amount:.2f} руб")
        return surcharges

    # --- вывод результатов ---
    def show_result(self, result) -> None:
        cur = result.currency
        print(f"\n--- Результат ({result.vehicle!r}) ---")
        print(f"Тариф: {result.tariff}")
        print(f"Израсходовано топлива: {result.fuel_liters:.2f} л")
        print(f"Стоимость топлива: {result.fuel_cost:.2f} {cur}")
        print(f"Доп. расходы (заданы при создании поездки): {result.extra_costs:.2f} {cur}")
        print(f"Итоговая стоимость (с учётом наценок): {result.total_cost:.2f} {cur}")
        print(f"Стоимость на одного пассажира: {result.cost_per_passenger:.2f} {cur}")

    def ask_similar_trip(self) -> bool:
        return self.ask_yes_no("\nПосчитать похожую поездку с другим числом пассажиров? (y/n): ")

    def ask_show_history(self) -> bool:
        return self.ask_yes_no("\nПоказать историю всех посчитанных поездок? (y/n): ")

    def ask_history_newest_first(self) -> bool:
        order = input("Порядок: сначала новые (n) или сначала старые (o)? [n]: ").strip().lower() or "n"
        return order != "o"

    def show_history(self, results: list) -> None:
        if not results:
            print("История пуста.")
            return
        print(f"\n--- История поездок ({len(results)}) ---")
        for n, result in enumerate(results, start=1):
            print(f"{n}. {result.vehicle!r}: {result.total_cost:.2f} {result.currency} "
                  f"({result.cost_per_passenger:.2f} {result.currency}/чел.)")

    def show_error(self, error) -> None:
        print(f"\nОшибка ввода: {error}")

    def ask_another_trip(self) -> bool:
        again = self.ask_yes_no("\nРассчитать другую поездку? (y/n): ")
        if again:
            print()
        return again

    def show_totals(self, summary: str) -> None:
        print(f"\n{summary}")
