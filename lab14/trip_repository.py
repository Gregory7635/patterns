import os
import pickle
from abc import ABC, abstractmethod


class ITripRepository(ABC):
    """
    Интерфейс репозитория (Repository).

    Для остального приложения репозиторий — «коллекция поездок в памяти»:
    добавить, найти, получить все, удалить. Где и как поездки хранятся на
    самом деле (список, файл, база данных), клиенту знать не нужно.
    """

    @abstractmethod
    def add(self, result) -> int:
        """Сохранить результат расчёта и вернуть его id."""

    @abstractmethod
    def get(self, trip_id: int):
        """Вернуть результат по id или None, если такого нет."""

    @abstractmethod
    def get_all(self) -> list:
        """Вернуть все результаты от старых к новым."""

    @abstractmethod
    def find_by_tariff(self, tariff: str) -> list:
        """Вернуть все результаты, посчитанные по указанному тарифу."""

    @abstractmethod
    def remove(self, trip_id: int) -> bool:
        """Удалить результат по id; True, если он был."""

    @abstractmethod
    def __len__(self) -> int:
        ...


class InMemoryTripRepository(ITripRepository):
    """Хранит поездки в словаре {id: результат}. После закрытия программы всё теряется."""

    def __init__(self):
        self._items = {}
        self._next_id = 1

    def add(self, result) -> int:
        trip_id = self._next_id
        self._items[trip_id] = result
        self._next_id += 1       # id не переиспользуются, даже после удаления
        return trip_id

    def get(self, trip_id: int):
        return self._items.get(trip_id)

    def get_all(self) -> list:
        return list(self._items.values())

    def find_by_tariff(self, tariff: str) -> list:
        return [r for r in self._items.values() if r.tariff == tariff]

    def remove(self, trip_id: int) -> bool:
        return self._items.pop(trip_id, None) is not None

    def __len__(self) -> int:
        return len(self._items)


class FileTripRepository(InMemoryTripRepository):
    """
    То же самое, но после каждого изменения данные сохраняются в файл, а при
    создании читаются из него — история переживает перезапуск программы.
    Файл создаёт и читает само приложение; чужим файлам такого формата
    (pickle) доверять нельзя.
    """

    def __init__(self, path: str):
        super().__init__()
        self._path = path
        if os.path.exists(path):
            with open(path, "rb") as f:
                self._items, self._next_id = pickle.load(f)

    def add(self, result) -> int:
        trip_id = super().add(result)
        self._save()
        return trip_id

    def remove(self, trip_id: int) -> bool:
        removed = super().remove(trip_id)
        if removed:
            self._save()
        return removed

    def _save(self) -> None:
        with open(self._path, "wb") as f:
            pickle.dump((self._items, self._next_id), f)
