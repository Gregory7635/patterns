import time
from enum import Enum

from external_fuel_price_api import ServiceUnavailableError
from fuel_price_adapter import IFuelPriceProvider, FuelPriceAdapter


class CircuitState(Enum):
    CLOSED = "CLOSED"        # цепь замкнута: запросы проходят как обычно
    OPEN = "OPEN"            # цепь разомкнута: запросы отклоняются сразу
    HALF_OPEN = "HALF_OPEN"  # пробный режим: пропускаем один запрос на проверку


class CircuitOpenError(ServiceUnavailableError):
    """Запрос отклонён предохранителем, к сервису он даже не отправлялся."""


class CircuitBreaker:
    """
    Предохранитель (Circuit Breaker).

    Пока всё в порядке, цепь замкнута (CLOSED) и запросы проходят. После
    failure_threshold сбоев подряд цепь размыкается (OPEN), и запросы
    отклоняются сразу, не нагружая упавший сервис. Через recovery_timeout
    секунд пропускается один пробный запрос (HALF_OPEN): при успехе цепь
    замыкается, при сбое — размыкается ещё на один период.

    Сбоем считается только ServiceUnavailableError: любая другая ошибка
    (например, «неизвестный тип топлива») означает, что сервис ответил.
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0,
                 clock=time.monotonic, verbose: bool = True):
        if failure_threshold < 1:
            raise ValueError("Порог сбоев должен быть не меньше 1")
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._clock = clock          # подменяется в тестах и демо
        self._verbose = verbose
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._opened_at = 0.0

    @property
    def state(self) -> CircuitState:
        return self._state

    def call(self, func, *args):
        if self._state is CircuitState.OPEN:
            if self._clock() - self._opened_at >= self._recovery_timeout:
                self._set_state(CircuitState.HALF_OPEN)
            else:
                self._log("цепь разомкнута, запрос к сервису не отправлялся")
                raise CircuitOpenError("Сервис временно отключён предохранителем, попробуйте позже")
        try:
            result = func(*args)
        except ServiceUnavailableError:
            self._on_failure()
            raise
        except Exception:
            self._on_success()   # сервис ответил (пусть и ошибкой запроса) — он жив
            raise
        self._on_success()
        return result

    def _on_failure(self) -> None:
        self._failures += 1
        self._log(f"сбой сервиса ({self._failures} из {self._failure_threshold})")
        if self._state is CircuitState.HALF_OPEN or self._failures >= self._failure_threshold:
            self._opened_at = self._clock()
            self._set_state(CircuitState.OPEN)

    def _on_success(self) -> None:
        self._failures = 0
        if self._state is CircuitState.HALF_OPEN:
            self._set_state(CircuitState.CLOSED)

    def _set_state(self, new_state: CircuitState) -> None:
        self._log(f"{self._state.value} -> {new_state.value}")
        self._state = new_state

    def _log(self, message: str) -> None:
        if self._verbose:
            print(f"[Предохранитель] {message}")


class GuardedFuelPriceProvider(IFuelPriceProvider):
    """Поставщик цен, все обращения которого к реальному поставщику идут через предохранитель."""

    def __init__(self, real_provider: IFuelPriceProvider = None, breaker: CircuitBreaker = None):
        self._real_provider = real_provider or FuelPriceAdapter()
        self.breaker = breaker or CircuitBreaker()

    def get_price_per_liter(self, fuel_type: str) -> float:
        return self.breaker.call(self._real_provider.get_price_per_liter, fuel_type)
