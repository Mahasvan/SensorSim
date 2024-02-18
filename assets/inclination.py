def get_vehicle_inclination(rotation):
    # The pitch component of the rotation is the inclination
    pitch = rotation.pitch
    return pitch