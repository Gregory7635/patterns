from abc import ABC, abstractmethod


class ITripObserver(ABC):
    """
    Интерфейс наблюдателя (Observer).

    Подписчик умеет только одно — получить готовый результат очередной
    поездки через update(). Что именно он с этим результатом делает
    (печатает лог, копит статистику, отправляет уведомление) — его личное
    дело; издатель (TripCostFacade) об этом ничего не знает.
    """

    @abstractmethod
    def update(self, result) -> None:
        ...


class ITripSubject(ABC):
    """Интерфейс издателя (Subject): умеет подписывать и отписывать наблюдателей."""

    @abstractmethod
    def subscribe(self, observer: ITripObserver) -> None:
        ...

    @abstractmethod
    def unsubscribe(self, observer: ITripObserver) -> None:
        ...


class ConsoleLogObserver(ITripObserver):
    """Конкретный наблюдатель: печатает короткую запись о каждой поездке."""

    def update(self, result) -> None:
        print(f"[Наблюдатель] Новая поездка: {result.vehicle!r} -> "
              f"{result.total_cost:.2f} {result.currency}")


class RunningTotalObserver(ITripObserver):
    """
    Конкретный наблюдатель: молча копит количество поездок и общую сумму
    по ним, ничего не печатая сам по себе — вывести итог можно вызвав
    summary() в любой момент.
    """

    def __init__(self):
        self.count = 0
        self.total = 0.0

    def update(self, result) -> None:
        self.count += 1
        self.total += result.total_cost

    def summary(self) -> str:
        if self.count == 0:
            return "Поездок ещё не было."
        return f"Поездок: {self.count}, общая сумма по всем: {self.total:.2f}"
