from typing import List
from datetime import datetime
from abc import ABC
import time


def make_data_dict(odometer, speed, fuel_level, acceleration, engine_rpm, seatbelt_status, ignition, ev_charging,
                   ev_battery, oil_life, tyre_pressure):
    return {
        "odometer": odometer,
        "speed": speed,
        "fuel_level": fuel_level,
        "acceleration": acceleration,
        "engine_rpm": engine_rpm,
        "seatbelt_status": seatbelt_status,
        "ignition": ignition,
        "ev_charging": ev_charging,
        "ev_battery": ev_battery,
        "oil_life": oil_life,
        "tyre_pressure": tyre_pressure,
    }


class Car:
    def __init__(self, id, frequency_config) -> None:
        self.id = id
        self.frequencies = make_data_dict(
            frequency_config["odometer"],
            frequency_config["speed"],
            frequency_config["fuel_level"],
            frequency_config["acceleration"],
            frequency_config["engine_rpm"],
            frequency_config["seatbelt_status"],
            frequency_config["ignition"],
            frequency_config["ev_charging"],
            frequency_config["ev_battery"],
            frequency_config["oil_life"],
            frequency_config["tyre_pressure"],
        )
        # self.data = {
        #     "odometer": None,
        #     "ev_battery": None
        # }
        self.data = make_data_dict(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None
        )

        # self.last_emmited = {
        #     "odometer": datetime.now(),
        #     "ev_battery": datetime.now()
        # }

        self.last_emmited = make_data_dict(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        )

    def update_data(self, update_data: dict):
        for key in update_data.keys():
            self.data[key] = update_data[key]

    def return_emitable(self, key, value):
        return {
            "id": self.id,
            key: value
        }


class Emitter(ABC):
    def __init__(self) -> None:
        pass

    def emit(self, vehicle_id, data):
        pass


class ConsoleEmitter(Emitter):
    def __init__(self) -> None:
        pass

    def emit(self, vehicle_id, data):
        print(f"Vehicle {vehicle_id} emitted {data}")


class DataEmitter:
    def __init__(self, cars: List[Car], emitter: Emitter) -> None:
        self.cars = {
            car.id: car
            for car in cars
        }
        self.emitter = emitter
        self.emitter_tick_size = self._get_all_least_tick_frequencies()

    def push(self, car_id, car_data):
        car = self.cars[car_id]
        car.update_data(car_data)
        self.cars[car_id] = car

    def _get_car_least_tick_frequency(self, car: Car):
        return min(car.frequencies.values())

    def _get_all_least_tick_frequencies(self):
        return min(map(self._get_car_least_tick_frequency, self.cars.values()))

    def iter(self):
        for car in self.cars.values():
            for key, value in car.data.items():
                if (time.time() - car.last_emmited[key]) >= car.frequencies[key]:
                    self.emitter.emit(car.id, car.return_emitable(key, value))
                    car.last_emmited[key] = time.time()


def emitter_tester():
    car1 = Car(1, make_data_dict(5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))
    car2 = Car(2, make_data_dict(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))
    emitter = ConsoleEmitter()
    data_emitter = DataEmitter([car1, car2], emitter)
    i = 1
    while True:
        print(f"Tick {i}")
        data_emitter.push(1, {"odometer": 100 + i})
        data_emitter.push(1, {"ev_battery": 100 + i})
        data_emitter.push(2, {"ev_battery": 100 + i})
        data_emitter.push(2, {"odometer": 100 + i})
        data_emitter.iter()
        i += 1
        time.sleep(1)


if __name__ == "__main__":
    emitter_tester()