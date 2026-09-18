class AppSettings:
    """
    Настройки приложения: валюта и точность округления.

    Паттерн «Одиночка» (Singleton).
    Гарантирует, что во всём приложении существует только один экземпляр
    настроек, и даёт к нему единую глобальную точку доступа — независимо
    от того, из какого модуля (calculator.py, cli.py и т.д.) обратились
    к AppSettings().
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        # Если экземпляр ещё не создан — создаём и запоминаем его в
        # атрибуте класса. При всех последующих вызовах AppSettings()
        # возвращается один и тот же объект.
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, currency: str = "руб", decimal_places: int = 2):
        # __init__ вызывается при каждом AppSettings(), даже если объект
        # уже существует, поэтому защищаемся флагом _initialized, чтобы
        # повторные вызовы не затирали уже установленные настройки.
        if self._initialized:
            return
        self.currency = currency
        self.decimal_places = decimal_places
        self._initialized = True

    def __repr__(self):
        return f"AppSettings(currency={self.currency!r}, decimal_places={self.decimal_places})"


if __name__ == "__main__":
    # Демонстрация: оба обращения возвращают один и тот же объект.
    a = AppSettings()
    b = AppSettings(currency="USD")  # эти аргументы будут проигнорированы
    print(a is b)          # True — один и тот же экземпляр
    print(a, b)             # одинаковые значения currency/decimal_places
