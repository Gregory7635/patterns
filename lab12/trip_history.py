from abc import ABC, abstractmethod


class IIterator(ABC):
    """
    Интерфейс итератора (Iterator).

    Умеет только две вещи: проверить, есть ли следующий элемент, и
    вернуть его. Больше клиенту знать не нужно — ни про индексы, ни про
    то, как элементы хранятся внутри коллекции.
    """

    @abstractmethod
    def has_next(self) -> bool:
        ...

    @abstractmethod
    def next(self):
        ...


class IIterableCollection(ABC):
    """Интерфейс коллекции, умеющей создавать итератор для собственного обхода."""

    @abstractmethod
    def create_iterator(self, reverse: bool = False) -> IIterator:
        ...


class TripHistoryIterator(IIterator):
    """
    Конкретный итератор.

    Хранит собственную позицию обхода и «снимок» элементов на момент
    создания — поэтому новые поездки, добавленные в историю после
    создания итератора, на уже идущий обход не повлияют, а начатый
    и незаконченный обход не мешает начать новый (create_iterator()
    у TripHistory каждый раз возвращает независимый объект).
    """

    def __init__(self, items: list, reverse: bool = False):
        self._items = list(reversed(items)) if reverse else list(items)
        self._position = 0

    def has_next(self) -> bool:
        return self._position < len(self._items)

    def next(self):
        if not self.has_next():
            raise StopIteration("История поездок закончилась")
        item = self._items[self._position]
        self._position += 1
        return item

    # Дополнительно даёт использовать тот же итератор в обычном for-цикле
    # Python (for trip in history.create_iterator(): ...), не ломая при
    # этом интерфейс IIterator с явными has_next()/next().
    def __iter__(self):
        return self

    def __next__(self):
        if not self.has_next():
            raise StopIteration
        return self.next()


class TripHistory(IIterableCollection):
    """
    Коллекция — история рассчитанных поездок.

    Результаты (TripCostResult) лежат в приватном списке _items, и клиент
    (cli.py) к нему напрямую не обращается. Единственный способ обойти
    историю — попросить у неё итератор через create_iterator(). Сегодня
    внутри список, но с точки зрения клиента это могла бы быть и база
    данных: интерфейс обхода не изменится.
    """

    def __init__(self):
        self._items = []

    def add(self, result) -> None:
        self._items.append(result)

    def __len__(self) -> int:
        return len(self._items)

    def create_iterator(self, reverse: bool = False) -> TripHistoryIterator:
        return TripHistoryIterator(self._items, reverse=reverse)
