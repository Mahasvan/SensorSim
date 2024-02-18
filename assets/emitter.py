from typing import List
from datetime import datetime
from config_loader import load_config, Vehicle
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

def convert_vehicle_config_to_car(carla_id: int, vehicle: Vehicle) -> 'Car':
    car = Car(
        carla_id,
        vehicle.vehicle_id,
        vehicle.type,
        make_data_dict(
            vehicle.data_points.odometer.interval if vehicle.data_points.odometer else 9999999,
            vehicle.data_points.speed.interval if vehicle.data_points.speed else 9999999,
            vehicle.data_points.fuel_level.interval if vehicle.data_points.fuel_level else 9999999,
            vehicle.data_points.acceleration.interval if vehicle.data_points.acceleration else 9999999,
            vehicle.data_points.engine_RPM.interval if vehicle.data_points.engine_RPM else 9999999,
            vehicle.data_points.seatbelt_status.interval if vehicle.data_points.seatbelt_status else 9999999,
            vehicle.data_points.ignition.interval if vehicle.data_points.ignition else 9999999,
            vehicle.data_points.EV_charging_status.interval if vehicle.data_points.EV_charging_status else 9999999,
            vehicle.data_points.EV_battery_level.interval if vehicle.data_points.EV_battery_level else 9999999,
            vehicle.data_points.oil_level.interval if vehicle.data_points.oil_level else 9999999,
            vehicle.data_points.tire_pressure.interval if vehicle.data_points.tire_pressure else 9999999,
        )
    )
    
    return car


class Car:
    def __init__(self, id, friendly_id, type, frequency_config)) -> None:
        self.id = id
        self.type = type
        self.type_speific_fields = ['ev_charging', 'ev_battery', 'oil_life', 'fuel_level']
        self.self_fields = ['ev_charging', 'ev_battery'] if type == "electric" else ['oil_life', 'fuel_level']
        self.friendly_id = friendly_id
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
                if (timme.time() - car.last_emmited[key]).microseconds >= car.frequencies[key] :
                    if key in car.type_speific_fields and (not key in car.self_fields):
                        print("Type mismatch. Vehicle of type", car.type, "tried emmitting", key)
                    else:
                        self.emitter.emit(car.id, car.return_emitable(key, value))
                        car.last_emmited[key] = time.time()


def emitter_tester():
    feet_config = load_config()
    cars = [convert_vehicle_config_to_car(index, vehicle) for index, vehicle in enumerate(feet_config.vehicles)]
    emitter = ConsoleEmitter()
    data_emitter = DataEmitter(cars, emitter)
    i = 1
    while True:
        print(f"Tick {i}")
        data_emitter.push(0, {"odometer": 100+i})
        data_emitter.push(0, {"ev_battery": 100+i})
        data_emitter.push(1, {"ev_battery": 100+i})
        data_emitter.push(1, {"odometer": 100+i})
        data_emitter.iter()
        i+=1
        time.sleep(1)


if __name__ == "__main__":
    emitter_tester()