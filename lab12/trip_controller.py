class TripController:
    """
    Контроллер (Controller) в паттерне MVC.

    Связывает модель и представление: просит View спросить пользователя,
    передаёт ответы в Model, а результат отдаёт обратно во View для показа.
    Сам ничего не считает, не читает ввод и не печатает — только решает,
    что и в каком порядке делать.
    """

    _TARIFF_CHOICES = {"1": "linear", "2": "surcharge"}

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def run(self) -> None:
        self.view.show_title()
        while True:
            self.manage_settings()
            self.choose_tariff()
            self.run_trip()
            if not self.view.ask_another_trip():
                break
        self.view.show_totals(self.model.totals_summary())

    def manage_settings(self) -> None:
        choice = self.view.ask_settings_action(self.model.get_settings())
        if choice == "1":
            currency, places = self.view.ask_new_settings(
                self.model.get_currency(), self.model.get_decimal_places())
            self.model.change_settings(currency, places)
            self.view.show_settings_saved(self.model.get_settings())
        elif choice == "2":
            done = self.model.undo_settings()
            self.view.show_undo_result(done, self.model.get_settings())

    def choose_tariff(self) -> None:
        choice = self.view.ask_tariff(self.model.get_tariff())
        tariff = self._TARIFF_CHOICES.get(choice)
        if tariff:
            self.model.set_tariff(tariff)
            self.view.show_tariff_changed(self.model.get_tariff())

    def run_trip(self) -> None:
        try:
            vehicle_type = self.view.ask_vehicle_type()
            fuel_consumption = self.view.ask_fuel_consumption()
            fuel_price = self._ask_fuel_price()
            distance = self.view.ask_distance()
            passengers = self.view.ask_passengers()
            extra_costs = self.view.ask_extra_costs()
            surcharges = self.view.ask_surcharges()

            result = self.model.calculate(vehicle_type, fuel_consumption, distance,
                                          passengers, fuel_price, extra_costs, surcharges)
            self.view.show_result(result)

            if self.view.ask_similar_trip():
                new_passengers = self.view.ask_passengers("Новое количество пассажиров: ")
                self.view.show_result(
                    self.model.calculate_similar(result, passengers=new_passengers))

            if self.view.ask_show_history():
                newest_first = self.view.ask_history_newest_first()
                self.view.show_history(self.model.get_history(newest_first))
        except ValueError as e:
            self.view.show_error(e)

    def _ask_fuel_price(self) -> float:
        if self.view.ask_fuel_source() != "e":
            return self.view.ask_fuel_price()
        price = self.model.get_fuel_price(self.view.ask_fuel_type())
        self.view.show_fuel_price(price)
        return price
