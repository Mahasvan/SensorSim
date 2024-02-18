import csv
import glob
import os
import sys
import time
import pprint

import pandas as pd

from assets.gears import calculate_engine_rpm
from assets.inclination import get_vehicle_inclination
from assets.airbag import airbag_deployed
from assets.seatbelt import is_seatbelt_on
from assets.fuel import calculate_fuel_consumption, predict_engine_oil_life, ignition_probability
from assets.battery import get_new_battery_capacity, convert_capacity_to_battery_percent

import carla

from carla import VehicleLightState as vls

import argparse
import logging
from numpy import random

from assets.emitter import DataEmitter, ConsoleEmitter, make_data_dict, Car

car1 = Car(0, make_data_dict(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))
car2 = Car(1, make_data_dict(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

data_emitter = DataEmitter([car1, car2], ConsoleEmitter())


def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []


class GenerateTraffic():
    def __init__(self, host='127.0.0.1', port=2000, number_of_vehicles=30, number_of_walkers=10,
                 safe=False, filterv='vehicle.audi.*', generationv='All', filterw='walker.pedestrian.*',
                 generationw='2', tm_port=8000, asynch=False, hybrid=False, seed=None, seedw=0,
                 car_lights_on=False, hero=False, respawn=True, no_rendering=False):
        self.host = host
        self.port = port
        self.number_of_vehicles = number_of_vehicles
        self.number_of_walkers = number_of_walkers
        self.safe = safe
        self.filterv = filterv
        self.generationv = generationv
        self.filterw = filterw
        self.generationw = generationw
        self.tm_port = tm_port
        self.asynch = asynch
        self.hybrid = hybrid
        self.seed = seed
        self.seedw = seedw
        self.car_lights_on = car_lights_on
        self.hero = hero
        self.respawn = respawn
        self.no_rendering = no_rendering

    def set_synchronous_mode(self, world, fixed_delta_seconds=0.2):
        """Configure the simulation to run in synchronous mode."""
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.substepping = True
        settings.max_substep_delta_time = 0.2
        settings.max_substeps = 10
        settings.fixed_delta_seconds = 0.25  # Set the time step per frame
        world.apply_settings(settings)

    def start_traffic(self):
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

        vehicles_list = []
        walkers_list = []
        all_id = []
        print("Loading Client")
        client = carla.Client(self.host, self.port)
        print("Carla Loaded")
        client.set_timeout(10.0)
        synchronous_master = False
        random.seed(self.seed if self.seed is not None else int(time.time()))

        try:
            world = client.get_world()
            print("World got")
            traffic_manager = client.get_trafficmanager(self.tm_port)
            traffic_manager.set_global_distance_to_leading_vehicle(2.5)
            if self.respawn:
                traffic_manager.set_respawn_dormant_vehicles(True)
            if self.hybrid:
                traffic_manager.set_hybrid_physics_mode(True)
                traffic_manager.set_hybrid_physics_radius(70.0)
            if self.seed is not None:
                traffic_manager.set_random_device_seed(self.seed)

            settings = world.get_settings()
            if not self.asynch:
                traffic_manager.set_synchronous_mode(True)
                if not settings.synchronous_mode:
                    synchronous_master = True
                    settings.synchronous_mode = True
                    settings.fixed_delta_seconds = 0.05
                else:
                    synchronous_master = False
            else:
                print("You are currently in asynchronous mode. If this is a traffic simulation, \
                you could experience some issues. If it's not working correctly, switch to synchronous \
                mode by using traffic_manager.set_synchronous_mode(True)")
            self.set_synchronous_mode(world, fixed_delta_seconds=1)

            if self.no_rendering:
                settings.no_rendering_mode = True
            world.apply_settings(settings)
            blueprints = get_actor_blueprints(world, self.filterv, self.generationv)
            blueprintsWalkers = get_actor_blueprints(world, self.filterw, self.generationw)

            if self.safe:
                blueprints = [x for x in blueprints if x.get_attribute('base_type') == 'car']

            blueprints = sorted(blueprints, key=lambda bp: bp.id)

            spawn_points = world.get_map().get_spawn_points()
            number_of_spawn_points = len(spawn_points)

            if self.number_of_vehicles < number_of_spawn_points:
                random.shuffle(spawn_points)
            elif self.number_of_vehicles > number_of_spawn_points:
                msg = 'requested %d vehicles, but could only find %d spawn points'
                logging.warning(msg, self.number_of_vehicles, number_of_spawn_points)
                self.number_of_vehicles = number_of_spawn_points

            # @todo cannot import these directly.
            SpawnActor = carla.command.SpawnActor
            SetAutopilot = carla.command.SetAutopilot
            FutureActor = carla.command.FutureActor

            # --------------
            # Spawn vehicles
            # --------------
            batch = []
            hero = self.hero
            for n, transform in enumerate(spawn_points):
                if n >= self.number_of_vehicles:
                    break
                blueprint = random.choice(blueprints)
                if blueprint.has_attribute('color'):
                    color = random.choice(blueprint.get_attribute('color').recommended_values)
                    blueprint.set_attribute('color', color)
                if blueprint.has_attribute('driver_id'):
                    driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                    blueprint.set_attribute('driver_id', driver_id)
                if hero:
                    blueprint.set_attribute('role_name', 'hero')
                    hero = False
                else:
                    blueprint.set_attribute('role_name', 'autopilot')

                # spawn the cars and set their autopilot and light state all together
                batch.append(SpawnActor(blueprint, transform)
                             .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))

            for response in client.apply_batch_sync(batch, synchronous_master):
                if response.error:
                    logging.error(response.error)
                else:
                    vehicles_list.append(response.actor_id)

            # Set automatic vehicle lights update if specified
            if self.car_lights_on:
                all_vehicle_actors = world.get_actors(vehicles_list)
                for actor in all_vehicle_actors:
                    traffic_manager.update_vehicle_lights(actor, True)

            # -------------
            # Spawn Walkers
            # -------------
            # some settings
            percentagePedestriansRunning = 15.0  # how many pedestrians will run
            percentagePedestriansCrossing = 30.0  # how many pedestrians will walk through the road

            if self.seedw:
                world.set_pedestrians_seed(self.seedw)
                random.seed(self.seedw)

            # 1. take all the random locations to spawn
            spawn_points = []
            for i in range(self.number_of_walkers):
                spawn_point = carla.Transform()
                loc = world.get_random_location_from_navigation()
                if (loc != None):
                    spawn_point.location = loc
                    spawn_points.append(spawn_point)
            # 2. we spawn the walker object
            batch = []
            walker_speed = []
            for spawn_point in spawn_points:
                walker_bp = random.choice(blueprintsWalkers)
                # set as not invincible
                if walker_bp.has_attribute('is_invincible'):
                    walker_bp.set_attribute('is_invincible', 'false')
                # set the max speed
                if walker_bp.has_attribute('speed'):
                    if (random.random() > percentagePedestriansRunning):
                        # walking
                        walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
                    else:
                        # running
                        walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
                else:
                    print("Walker has no speed")
                    walker_speed.append(0.0)
                batch.append(SpawnActor(walker_bp, spawn_point))
            results = client.apply_batch_sync(batch, True)
            walker_speed2 = []
            for i in range(len(results)):
                if results[i].error:
                    logging.error(results[i].error)
                else:
                    walkers_list.append({"id": results[i].actor_id})
                    walker_speed2.append(walker_speed[i])
            walker_speed = walker_speed2
            # 3. we spawn the walker controller
            batch = []
            walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
            for i in range(len(walkers_list)):
                batch.append(SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[i]["id"]))
            results = client.apply_batch_sync(batch, True)
            for i in range(len(results)):
                if results[i].error:
                    logging.error(results[i].error)
                else:
                    walkers_list[i]["con"] = results[i].actor_id
            # 4. we put together the walkers and controllers id to get the objects from their id
            for i in range(len(walkers_list)):
                all_id.append(walkers_list[i]["con"])
                all_id.append(walkers_list[i]["id"])
            all_actors = world.get_actors(all_id)

            # wait for a tick to ensure client receives the last transform of the walkers we have just created
            if self.asynch or not synchronous_master:
                world.wait_for_tick()
            else:
                world.tick()

            # 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
            # set how many pedestrians can cross the road
            world.set_pedestrians_cross_factor(percentagePedestriansCrossing)
            for i in range(0, len(all_id), 2):
                # start walker
                all_actors[i].start()
                # set walk to random point
                all_actors[i].go_to_location(world.get_random_location_from_navigation())
                # max speed
                all_actors[i].set_max_speed(float(walker_speed[int(i / 2)]))

            print('spawned %d vehicles and %d walkers, press Ctrl+C to exit.' % (len(vehicles_list), len(walkers_list)))

            # Example of how to use Traffic Manager parameters
            traffic_manager.global_percentage_speed_difference(10.0)

            with open('vehicle_data_2.csv', 'w', newline='') as csvfile:
                fieldnames = ["gear", "throttle", "speed", "acceleration", "max_rpm", "gear_ratio", "wheel_radius",
                              "engine_rpm", "inclination"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header row to CSV file
                writer.writeheader()

                # Main loop
                current_time = time.time()
                arr = []
                airbags = [False] * len(vehicles_list)
                prev_accel = [0] * len(vehicles_list)
                prev_locations = [0] * len(vehicles_list)
                odometer_readings = [0] * len(vehicles_list)
                fuel_readings = [0] * len(vehicles_list)
                max_battery_capacities = [random.randint(70, 120) for _ in range(len(vehicles_list))]
                max_battery_capacities = list(
                    map(lambda x: x * 1000, max_battery_capacities))  # convert to watt hours form kilowatt hours
                current_battery_capacities = max_battery_capacities.copy()
                prev_nonzero_speed = time.time()
                prev_zero_speed = time.time()
                # while count < 20:

                while (tick_time := time.time()) < current_time + 60:
                    t1_start = time.perf_counter()
                    if not self.asynch and synchronous_master:
                        world.tick()
                        world.tick()
                        world.tick()
                        world.tick()

                        all_vehicle_actors = world.get_actors(vehicles_list)
                        for id, i in enumerate(all_vehicle_actors):
                            torque_curve_data = []
                            for vector in i.get_physics_control().torque_curve:
                                x_value = vector.x
                                y_value = vector.y
                                torque_curve_data.append((x_value, y_value))

                            physics = i.get_physics_control()
                            control = i.get_control()
                            gear = control.gear
                            mass = physics.mass
                            throttle = control.throttle
                            speed = i.get_velocity().length()
                            if round(speed) > 0.5:
                                prev_nonzero_speed = time.time()
                            if round(speed) < 0.5:
                                prev_zero_speed = time.time()
                            uptime = int(time.time() - prev_zero_speed)
                            stopped_for = int(time.time() - prev_nonzero_speed)
                            wearing_seatbelt = is_seatbelt_on(uptime, stopped_for)
                            acceleration = i.get_acceleration().length()
                            max_rpm = physics.max_rpm
                            final_drive_ratio = physics.final_ratio
                            try:
                                gear_ratio = physics.forward_gears[gear].ratio
                            except IndexError:
                                gear_ratio = physics.forward_gears[0].ratio

                            wheel_radius = physics.wheels[0].radius / 100
                            engine_rpm = calculate_engine_rpm(gear, gear_ratio, final_drive_ratio, speed, wheel_radius)
                            rotation = i.get_transform().rotation
                            inclination = get_vehicle_inclination(rotation)
                            airbags_deployed_bool = airbag_deployed(prev_accel[id], acceleration)
                            if airbags_deployed_bool:
                                airbags[id] = True
                            prev_accel[id] = acceleration

                            if prev_locations[id] == 0:
                                prev_locations[id] = i.get_location()

                            # calculate distances travelled
                            distance_travelled = i.get_location().distance(prev_locations[id])
                            prev_locations[id] = i.get_location()
                            odometer_readings[id] += distance_travelled

                            mass = physics.mass
                            drag_coefficient = physics.drag_coefficient
                            moi = physics.moi
                            fuel_consumed = calculate_fuel_consumption(mass, acceleration, speed, engine_rpm,
                                                                       distance_travelled, drag_coefficient, moi)
                            fuel_readings[id] += fuel_consumed
                            # ignition_status = ignition_probability(speed, stopped_for)
                            ignition_status = True if speed > 0.1 else False
                            engine_oil_life = predict_engine_oil_life(changed_odometer=odometer_readings[id],
                                                                      initial_odometer=0, oil_change_interval=4500)
                            new_battery_capacity = get_new_battery_capacity(max_battery_capacities,
                                                                            current_battery_capacities, id, 1 / 3600)
                            current_battery_capacities[id] = new_battery_capacity
                            new_battery_percent = convert_capacity_to_battery_percent(max_battery_capacities, id,
                                                                                      new_battery_capacity)

                            wheel_friction = [physics.wheels[i].tire_friction for i in range(4)]

                            # print("Timestamp: ", tick_time)
                            # print("Vehicle ID: ", id)
                            # print("Current Time:", time.time())
                            # print("Gear: ", gear)
                            # print("Throttle: ", throttle)
                            # print("Speed: ", speed)
                            # print("Acceleration: ", acceleration)
                            # print("Max RPM: ", max_rpm)
                            # print("Gear Ratio: ", gear_ratio)
                            # print("Wheel Radius: ", wheel_radius)
                            # print("Engine RPM: ", engine_rpm)
                            # print("Inclination: ", inclination)
                            # print("Airbags Deployed: ", airbags_deployed_bool)
                            # print("============")
                            to_add = {
                                "car_weight": mass,
                                "timestamp": tick_time,
                                "vehicle_id": id,
                                "gear": gear,
                                "throttle": throttle,
                                "speed": speed,
                                "acceleration": acceleration,
                                "max_rpm": max_rpm,
                                "gear_ratio": gear_ratio,
                                "wheel_radius": wheel_radius,
                                "engine_rpm": engine_rpm,
                                "inclination": inclination,
                                "tyre_pressure": (0, 0, 0, 0),
                                "tyre_friction": wheel_friction,
                                "odometer": odometer_readings[id],
                                "fuel_consumed": fuel_readings[id],
                                "ignition_status": ignition_status,
                                "engine_oil_life": engine_oil_life,
                                "new_battery_percent": new_battery_percent,
                                "seatbelt_status": wearing_seatbelt,
                            }
                            payload = make_data_dict(
                                odometer_readings[id],
                                speed,
                                fuel_readings[id],
                                acceleration,
                                engine_rpm,
                                wearing_seatbelt,
                                ignition_status,
                                "yes",
                                new_battery_percent,
                                0,
                                (0, 0, 0, 0)
                            )
                            data_emitter.push(id, payload)
                            arr.append(to_add)
                        print("----")
                        data_emitter.iter()
                        t1_stop = time.perf_counter()
                        try:
                            time.sleep(1 - (t1_stop - t1_start))
                        except ValueError:
                            print("Value Error")
                            pass
                    else:
                        world.wait_for_tick()

                df = pd.DataFrame(arr)
                df.to_csv('../vehicle_data.csv', index=False)

        finally:

            if not self.asynch and synchronous_master:
                settings = world.get_settings()
                settings.synchronous_mode = False
                settings.no_rendering_mode = False
                settings.fixed_delta_seconds = None
                world.apply_settings(settings)

            print('\ndestroying %d vehicles' % len(vehicles_list))
            client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

            # stop walker controllers (list is [controller, actor, controller, actor ...])
            for i in range(0, len(all_id), 2):
                all_actors[i].stop()

            print('\ndestroying %d walkers' % len(walkers_list))
            client.apply_batch([carla.command.DestroyActor(x) for x in all_id])
            # return arr
            # time.sleep(1)
