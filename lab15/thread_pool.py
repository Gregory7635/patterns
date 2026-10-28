import queue
import threading


class ThreadPool:
    """
    Пул потоков (Thread Pool).

    При создании запускает фиксированное число рабочих потоков, и дальше
    они живут всё время работы пула. Задачи складываются в общую очередь;
    свободный поток берёт из неё следующую задачу, выполняет и возвращается
    за новой. Новые потоки на каждую задачу не создаются — уже запущенные
    используются повторно.
    """

    def __init__(self, workers: int = 3):
        if workers < 1:
            raise ValueError("В пуле должен быть хотя бы один поток")
        self._tasks = queue.Queue()   # потокобезопасная очередь задач
        self._closed = False
        self._threads = []
        for n in range(workers):
            thread = threading.Thread(target=self._worker_loop, name=f"worker-{n + 1}",
                                      daemon=True)
            thread.start()
            self._threads.append(thread)

    @property
    def size(self) -> int:
        return len(self._threads)

    def submit(self, func, *args) -> None:
        """Поставить задачу в очередь. Результат не возвращается — для этого есть map()."""
        if self._closed:
            raise RuntimeError("Пул потоков остановлен")
        self._tasks.put((func, args))

    def wait(self) -> None:
        """Дождаться, пока все поставленные задачи будут выполнены."""
        self._tasks.join()

    def map(self, func, items) -> list:
        """
        Выполнить func для каждого элемента параллельно и вернуть результаты
        в том же порядке, что и элементы. Если хотя бы одна задача упала,
        после завершения всех задач выбрасывается её исключение.
        """
        items = list(items)
        results = [None] * len(items)
        errors = [None] * len(items)

        def run(index, item):
            try:
                results[index] = func(item)
            except Exception as e:
                errors[index] = e

        for index, item in enumerate(items):
            self.submit(run, index, item)
        self.wait()

        for error in errors:
            if error is not None:
                raise error
        return results

    def shutdown(self) -> None:
        """Остановить пул: каждому потоку отправляется «стоп-сигнал» None."""
        if self._closed:
            return
        self._closed = True
        for _ in self._threads:
            self._tasks.put(None)
        for thread in self._threads:
            thread.join()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.shutdown()

    def _worker_loop(self) -> None:
        """Жизнь рабочего потока: брать задачу из очереди, выполнять, повторять."""
        while True:
            task = self._tasks.get()          # ждёт, пока в очереди что-то появится
            try:
                if task is None:              # стоп-сигнал — поток завершается
                    return
                func, args = task
                try:
                    func(*args)
                except Exception:
                    pass                      # ошибка одной задачи не должна убить поток
            finally:
                self._tasks.task_done()       # отметить задачу выполненной (для wait())
