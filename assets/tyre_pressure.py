def calculate_heat_generated(friction_force, distance, weight, acceleration):
    friction_force = eval(friction_force)[0]
    weight_newton = weight * 9.81  

    force_for_acceleration = weight_newton * acceleration

    force_for_heat = force_for_acceleration - friction_force 

    heat_generated = force_for_heat * distance

    return heat_generated

def calculate_delta_temperature(heat_generated, tire_mass, specific_heat_capacity):
    delta_temperature = heat_generated / (tire_mass * specific_heat_capacity)
    return delta_temperature

def calculate_pressure_change(initial_pressure, initial_temperature, final_temperature):
    initial_temperature_kelvin = initial_temperature + 273.15
    final_temperature_kelvin = final_temperature + 273.15

    R = 8.314  # J/(mol*K)

    delta_temperature = final_temperature_kelvin - initial_temperature_kelvin

    # ideal gas law, 12th la padichome
    delta_pressure = (initial_pressure * delta_temperature) / initial_temperature_kelvin

    return delta_pressure

def pascals_to_psi(pascals):
    psi = pascals / 6895
    return psi

def calculate_new_pressure(friction_force, distance, weight, acceleration, initial_pressure, initial_temperature, tire_mass, specific_heat_capacity):
    heat_generated = calculate_heat_generated(friction_force, distance, weight, acceleration)
    delta_temperature = calculate_delta_temperature(heat_generated, tire_mass, specific_heat_capacity)
    delta_pressure = calculate_pressure_change(initial_pressure, initial_temperature, initial_temperature + delta_temperature)
    delta_psi = pascals_to_psi(delta_pressure)
    # converting back initial_pressure inplace
    final_psi = min(initial_pressure/10000 + delta_psi, initial_pressure/10000 + 2)
    return final_psi