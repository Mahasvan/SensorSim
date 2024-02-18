import carla
import math

# create a tesla ev
def create_ev(world):
    ev_bp = world.get_blueprint_library().find('vehicle.tesla.model3')
    ev_bp.set_attribute('color', '255, 0, 0')
    spawn_point = world.get_map().get_spawn_points()[0]
    ev = world.spawn_actor(ev_bp, spawn_point)
    return ev

# create a charging station
def create_charging_station(world, spawn_point_index):
    charging_station_bp = world.get_blueprint_library().find('static.prop.charging_station.tesla')
    charging_station_bp.set_attribute('color', '255, 255, 255')
    spawn_point = world.get_map().get_spawn_points()
    charging_station = world.spawn_actor(charging_station_bp, spawn_point[spawn_point_index])
    return charging_station, spawn_point[spawn_point_index].location



def calculate_distance(location1, location2):
    return math.sqrt((location1.x - location2.x)**2 + (location1.y - location2.y)**2)

# Example function to find the nearest charging station
def find_nearest_charging_station(ev_location, charging_stations):
    nearest_station = None
    min_distance = float('inf')
    for station in charging_stations:
        distance = calculate_distance(ev_location, station['location'])
        if distance < min_distance:
            min_distance = distance
            nearest_station = station
    return nearest_station, min_distance


def evaluate_charging_probability(ev_location, charging_stations, current_battery_level):
    nearest_station, distance = find_nearest_charging_station(ev_location, charging_stations)
    """Return categorical probability of charging at the nearest station."""
    if distance < 100 and current_battery_level < 25:
        return 'high'
    elif distance < 200 and current_battery_level < 30:
        return 'medium'
    elif distance < 300 and current_battery_level < 40:
        return 'low'
    else:
        return 'none'
    
def main(current_battery_level=50):
    client = carla.Client('10.5.27.231', 2000)
    client.set_timeout(10.0) # seconds
    world = client.get_world()

    ev = create_ev(world)
    charging_stations = []
    for i in range(10):
        charging_station, location = create_charging_station(world, i)
        charging_stations.append({'station': charging_station, 'location': location})
    
    # Find the nearest charging station
    ev_location = ev.get_location()

    p = evaluate_charging_probability(ev_location, charging_stations, current_battery_level)

    print(f"The probability of charging at the nearest station is {p}.")

    
if __name__ == '__main__':
    main()
