import numpy as np
import matplotlib.pyplot as plt
import math

BASE_VOLTAGE = 400 # tesla model s
MIN_VOLTAGE = 280 # tesla model s battery backs are 96 cells in series and 3.7 volts per cell ooda min voltage is 280. below this voltage the battery will start doing low voltage protection
INTERNAL_RESISTANCE = 0.038 # ohms in tesla model s
BATTERY_CAPACITY = 85 # kWh in tesla model s
TICK_SIZE = 1/3600

def sigmoid(x, a, b, c):
    return (a / (1 + np.exp(b * (x - c))))

def linear(x, m, b):
    return m * x + b

def parabola(x):
    return -0.0005 * (x - 10) * (x - 20)

def get_dV(x):
    a = 1
    b = 1
    c = 0
    return np.maximum(sigmoid(x, a, b, c) + linear(x, 0.00012, 0), sigmoid(x, a, b, c) + parabola(x))/2

def get_V(x):
    dV = np.cumsum(get_dV(x))

    scaled_dV = (dV - np.min(dV)) / (np.max(dV) - np.min(dV))
    return scaled_dV

def integrate_from_x_to_100(x):
    try:
        return np.trapz(get_V(np.linspace(x, 100, 100 - x)))
    except Exception as e:
        return np.trapz(get_V(np.linspace(x, 100, 100 - x + 1)))


def get_voltage_drop(soc):
    return BASE_VOLTAGE * (integrate_from_x_to_100(soc)/100)

def get_actual_voltage(soc):
    return min(MIN_VOLTAGE, BASE_VOLTAGE - get_voltage_drop(soc))

def get_current_draw(soc): # in watt hours
    return get_actual_voltage(soc) / INTERNAL_RESISTANCE

def power_consumed_in_one_tick(soc, time): # in watt hours
    return get_current_draw(soc) * time

def get_new_battery_capacity(max_capacities, old_battery_capacities, car_id, tick_size):
    """
    max_capacities: Array with max capacities initialized of each vehicle in watt hours
    old_battery_capacities: Array with battery capacity from last tick in watt hours
    car_id: self explanatory
    tick_size: size of tick in seconds
    """
    old_battery_capacity = old_battery_capacities[car_id]
    max_capacity = max_capacities[car_id]
    new_capacity = old_battery_capacity - power_consumed_in_one_tick(math.ceil((old_battery_capacity / max_capacity) * 100), tick_size)
    return new_capacity

def convert_capacity_to_battery_percent(max_capacities, car_id, battery_capacity):
    max_capacity = max_capacities[car_id]
    return (battery_capacity / max_capacity) * 100

if __name__ == "__main__":
    import time

    # simulation
    battery_capacity = BATTERY_CAPACITY * 1000  # in watt hours
    capacities = [battery_capacity / (BATTERY_CAPACITY * 1000) * 100]
    while battery_capacity > 0:
        battery_capacity -= power_consumed_in_one_tick(math.ceil((battery_capacity / (BATTERY_CAPACITY * 1000)) * 100),
                                                       TICK_SIZE)
        print(max(0, (battery_capacity / (BATTERY_CAPACITY * 1000)) * 100))
        capacities.append(max(0, (battery_capacity / (BATTERY_CAPACITY * 1000)) * 100))
        time.sleep(.001)

    plt.plot(np.arange(0, len(capacities), 1), capacities)
    plt.show()