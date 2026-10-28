import os

from trip_model import TripModel
from trip_repository import FileTripRepository

PATH = "demo_trips.dat"


def show(repo):
    for trip_id in range(1, 10):
        r = repo.get(trip_id)
        if r:
            print(f"  #{trip_id}: {type(r.vehicle).__name__}, тариф {r.tariff}, "
                  f"итого {r.total_cost:.2f} {r.currency}")


def main():
    if os.path.exists(PATH):
        os.remove(PATH)

    print("=== Сеанс 1: поездки сохраняются в репозиторий ===")
    repo = FileTripRepository(PATH)
    model = TripModel(repository=repo)
    model.calculate("car", 8, 100, 2, 60, [], [])
    model.set_tariff("surcharge")
    model.calculate("taxi", 9, 50, 1, 60, [], [("toll", 100)])
    model.set_tariff("linear")
    model.calculate("carsharing", 7, 200, 3, 60, [], [])
    print(f"Всего в репозитории: {len(repo)}")
    show(repo)

    print("\n=== Поиск по тарифу «surcharge» ===")
    for r in model.get_trips_by_tariff("surcharge"):
        print(f"  {type(r.vehicle).__name__}: {r.total_cost:.2f} {r.currency}")

    print("\n=== Удаление поездки #2 ===")
    print(f"  Удалено: {repo.remove(2)}; повторное удаление: {repo.remove(2)}")
    show(repo)

    print("\n=== Сеанс 2: программа перезапущена, новый репозиторий читает тот же файл ===")
    repo2 = FileTripRepository(PATH)
    model2 = TripModel(repository=repo2)
    print(f"Всего в репозитории: {len(repo2)}")
    show(repo2)
    model2.calculate("car", 8, 10, 1, 60, [], [])
    new_id = max(i for i in range(1, 10) if repo2.get(i))
    print(f"Новая поездка получила id #{new_id}, а не #2 (id не переиспользуются)")
    show(repo2)
    print(f"История (сначала новые): {[round(r.total_cost) for r in model2.get_history()]}")

    os.remove(PATH)


if __name__ == "__main__":
    main()
