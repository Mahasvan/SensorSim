
def airbag_deployed(prev_accel: float, current_accel: float):

    if abs(prev_accel - current_accel) > 5:
        return True

    return False
