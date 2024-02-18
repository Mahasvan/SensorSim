def calculate_engine_rpm(current_gear: int, gear_ratio: float, final_drive_ratio: float,
                         current_speed: float, rolling_radius: float):
    # current speed in m/s
    # rolling radius in meters
    rpm = (current_speed*60) / (2 * 3.14 * rolling_radius)
    if current_gear > 0:
        rpm = rpm * gear_ratio * final_drive_ratio
    return rpm
