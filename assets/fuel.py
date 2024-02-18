import random


def calculate_fuel_consumption(mass_vehicle, acceleration, speed, rpm, distance, drag_coefficient, moment_of_inertia):
    if rpm == 0:
        return 0
    force_acceleration = mass_vehicle * acceleration
    force_drag = 0.5 * drag_coefficient * speed ** 2
    force_rolling_resistance = 0.01 * mass_vehicle * 9.8
    total_force = force_acceleration + force_drag + force_rolling_resistance
    torque = total_force * (speed / rpm)
    fuel_consumption = (torque * distance / moment_of_inertia) * 0.000009

    return fuel_consumption

def predict_engine_oil_life(changed_odometer, initial_odometer=0, oil_change_interval=4500):
    # Predict the engine oil life percentage after a certain distance
    # We started at 0 km, and the oil change interval is 4500 km
    # The initial oil life percentage is 100%
    # Calculate the distance driven since the last oil change
    distance_driven = changed_odometer - initial_odometer
    # Calculate the remaining oil life percentage
    remaining_oil_life_percent = 100 - (distance_driven / (oil_change_interval * 10))
    return remaining_oil_life_percent


def ignition_probability(speed, idle_ticks):
    """
    Calculate the probability of the car being turned off due to idling.

    Parameters:
    - speed: The current speed of the car.
    - ticks: The number of ticks the car has been idle.

    Returns:
    - A tuple of (ignition_state, probability). ignition_state is a boolean indicating
      whether the ignition is on (True) or off (False), and probability is the probability
      of the car being turned off due to idling.
    """

    # If the car speed is greater than 0, the car is moving, so ignition is on
    if speed > 0:
        return True  # Ignition is on, 0% probability of turning off

    # If the car has been idle for less than 60 ticks, the probability is 0%
    if idle_ticks < 60:
        return True  # Ignition is on, 0% probability of turning off

    # Calculate the probability of turning off after idling for 60 to 180 ticks
    if 60 <= idle_ticks <= 180:
        # Linearly increase the probability from 0% at 60 ticks to 100% at 180 ticks
        probability = (idle_ticks - 60) / (180 - 60)

        return random.randrange(0, 100) < probability

    # If the car has been idle for more than 180 ticks, the probability is 100%
    if idle_ticks > 180:
        return False  # Ignition is off, 100% probability of being turned off
