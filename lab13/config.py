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

    def update(self, currency: str = None, decimal_places: int = None) -> None:
        """
        Изменить настройки уже существующего экземпляра. В отличие от
        AppSettings(...), которую после первого создания объект игнорирует
        (см. защиту _initialized выше), update() — единственный способ
        поменять currency/decimal_places в уже работающем приложении.
        """
        if currency is not None:
            self.currency = currency
        if decimal_places is not None:
            self.decimal_places = decimal_places

    def create_memento(self, label: str = "") -> "AppSettingsMemento":
        """
        Снимок (Memento): запоминает текущее состояние (currency,
        decimal_places), не раскрывая его наружу — снимок умеет отдать
        своё содержимое обратно только самому AppSettings.
        """
        return AppSettingsMemento({"currency": self.currency, "decimal_places": self.decimal_places}, label)

    def restore(self, memento: "AppSettingsMemento") -> None:
        """Восстановить состояние по ранее сделанному снимку."""
        state = memento._state_for(self)
        self.currency = state["currency"]
        self.decimal_places = state["decimal_places"]


class AppSettingsMemento:
    """
    Снимок (Memento) состояния AppSettings.

    Хранит состояние в приватном атрибуте и не даёт прочитать его никому,
    кроме самого AppSettings (через _state_for — своего рода «пароль
    доступа»: метод просит показать state, передавая в себя self, и
    снимок отдаёт данные только тому, кто его и создал). Хранитель
    (SettingsCaretaker, settings_history.py) работает со снимком как с
    «чёрным ящиком»: может его сохранить и вернуть обратно, но не может
    заглянуть внутрь или изменить.
    """

    def __init__(self, state: dict, label: str = ""):
        self._state = dict(state)
        self._owner_cls = AppSettings
        self.label = label  # подпись для человека — не часть состояния

    def _state_for(self, requester) -> dict:
        if not isinstance(requester, self._owner_cls):
            raise PermissionError("Только AppSettings может прочитать содержимое снимка")
        return dict(self._state)

    def __repr__(self):
        return f"AppSettingsMemento({self.label!r})"


if __name__ == "__main__":
    # Демонстрация: оба обращения возвращают один и тот же объект.
    a = AppSettings()
    b = AppSettings(currency="USD")  # эти аргументы будут проигнорированы
    print(a is b)          # True — один и тот же экземпляр
    print(a, b)             # одинаковые значения currency/decimal_places
