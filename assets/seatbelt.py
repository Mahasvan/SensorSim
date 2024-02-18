import random


def is_seatbelt_on(uptime: int, stopped_for: int):
    # uptime is in seconds
    # seatbelt is on after stopping for random time between 10 and 30 seconds
    # seatbelt is off after stopping for random time between 0 and 10 seconds
    if stopped_for < 10:
        return False
    if uptime > 30:
        return True

    if uptime > random.randint(10, 30) or stopped_for > random.randint(0, 10):
        return True

    return False
