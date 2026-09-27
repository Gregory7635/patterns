from fuel_price_adapter import IFuelPriceProvider, FuelPriceAdapter


class CachingFuelPriceProxy(IFuelPriceProvider):
    """
    Заместитель (Proxy) — кэширующий.

    Стоит «вместо» настоящего поставщика цен и реализует тот же интерфейс
    IFuelPriceProvider, поэтому клиент (фасад) не отличает прокси от
    настоящего объекта. Но перед тем как обратиться к реальному поставщику
    (адаптеру внешнего сервиса), прокси проверяет свой кэш:

        * цена этого топлива уже запрашивалась -> вернуть из кэша,
          к внешнему сервису не обращаться (быстро и бесплатно);
        * цены в кэше нет -> обратиться к реальному поставщику,
          запомнить ответ и вернуть его.

    Так мы контролируем доступ к «дорогому» объекту (обращение к внешнему
    сервису — это сетевой запрос), не меняя ни сам адаптер, ни клиентский код.
    """

    def __init__(self, real_provider: IFuelPriceProvider = None, verbose: bool = True):
        # Реальный объект, которого замещает прокси. По умолчанию — адаптер.
        self._real_provider = real_provider or FuelPriceAdapter()
        self._cache = {}
        self._verbose = verbose

    def get_price_per_liter(self, fuel_type: str) -> float:
        # Ключ кэша приводим к единому виду, чтобы «ай-92» и «АИ-92» были одной записью.
        key = fuel_type.strip().upper()

        if key in self._cache:
            self._log(f"[Прокси] {key}: цена взята из кэша, внешний сервис не вызывался")
            return self._cache[key]

        # Если реальный поставщик выбросит ошибку (неизвестное топливо),
        # она просто пройдёт наружу, а в кэш ничего не попадёт.
        price = self._real_provider.get_price_per_liter(key)
        self._cache[key] = price
        self._log(f"[Прокси] {key}: запрос к внешнему сервису, цена сохранена в кэш")
        return price

    def clear_cache(self):
        """Сбросить кэш (например, если цены на АЗС обновились)."""
        self._cache.clear()

    def _log(self, message: str):
        if self._verbose:
            print(message)
