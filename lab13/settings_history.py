from config import AppSettings, AppSettingsMemento


class SettingsCaretaker:
    """
    Хранитель (Caretaker) — стек снимков настроек.

    Складывает снимки (AppSettingsMemento), которые отдаёт AppSettings,
    и возвращает их обратно по одному, в порядке "последний сохранённый
    отменяется первым" (LIFO). Caretaker никогда не заглядывает внутрь
    снимка и не читает его состояние напрямую — только хранит ссылку на
    объект и передаёт его назад тому же AppSettings для восстановления.
    """

    def __init__(self, settings: AppSettings):
        self._settings = settings
        self._stack: list[AppSettingsMemento] = []

    def save(self, label: str = "") -> None:
        """Сделать и сохранить снимок текущего состояния настроек."""
        self._stack.append(self._settings.create_memento(label))

    def undo(self) -> bool:
        """
        Откатить настройки к последнему сохранённому снимку.
        Возвращает False, если сохранять было нечего (стек пуст).
        """
        if not self._stack:
            return False
        memento = self._stack.pop()
        self._settings.restore(memento)
        return True

    def __len__(self) -> int:
        return len(self._stack)
