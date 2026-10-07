from observers import ConsoleLogObserver
from trip_model import TripModel
from trip_view import ConsoleTripView
from trip_controller import TripController


def main():
    # MVC: собираем три части и отдаём управление контроллеру.
    model = TripModel()
    view = ConsoleTripView()
    controller = TripController(model, view)

    # Наблюдатель: короткая строка о каждой поездке подписывается снаружи.
    model.subscribe(ConsoleLogObserver())

    controller.run()


if __name__ == "__main__":
    main()
