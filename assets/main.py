import random


def calculate_pressure(initial_pressure: float, uptime: int, stopped_for: int):
    # pressure is in psi
    # uptime is in seconds
    # tire pressure increases by 1 psi for every 5 minutes, for 20 minutes. then it stays constant
    # tire pressure decreases by 1 psi for every 5 minutes of stopping, for 20 minutes. then it stays constant
    if uptime <= 1200:
        return initial_pressure + uptime / 300 - stopped_for / 300
    else:
        if stopped_for >= 1200:
            return initial_pressure
        return initial_pressure + 4 - stopped_for / 300


def is_seatbelt(uptime: int, stopped_for: int):
    # uptime is in seconds
    # seatbelt is on after stopping for random time between 10 and 30 seconds
    # seatbelt is off after stopping for random time between 0 and 10 seconds
    if stopped_for < 5:
        return False
    if uptime > 10:
        return True

    if uptime > random.randint(0, 10) or stopped_for > random.randint(0, 5):
        return True

    return False


def airbag(prev_accel: float, current_accel: float):

    if abs(prev_accel - current_accel) > 5:
        return True

    return False