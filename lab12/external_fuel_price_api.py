class ExternalFuelPriceAPI:
    """
    Имитация стороннего сервиса цен на топливо (например, агрегатора цен на АЗС).

    У такого сервиса, как правило, свой формат ответа и свои названия методов,
    не совпадающие с тем, что удобно нашему приложению: метод называется
    fetch_price(), а не get_price_per_liter(), и возвращает не просто число,
    а целый словарь с дополнительными полями.
    """

    _PRICES = {
        "АИ-92": 54.10,
        "АИ-95": 58.30,
        "ДТ": 60.90,
    }

    def fetch_price(self, fuel_type: str) -> dict:
        """Возвращает 'сырой' ответ в формате внешнего сервиса."""
        fuel_type = fuel_type.strip().upper()
        if fuel_type not in self._PRICES:
            raise ValueError(
                f"Внешний сервис не знает тип топлива {fuel_type!r}. "
                f"Доступные: {', '.join(self._PRICES)}"
            )
        return {
            "fuel_type": fuel_type,
            "price_rub_per_liter": self._PRICES[fuel_type],
            "updated_at": "2026-09-22",
        }
