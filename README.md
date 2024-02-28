# SensorSim
A CARLA-based sensor solution that uses values provided by the simulator to derive values for the following sensors:
- Odometer
- Speedometer
- Fuel Level
- Acceleration
- Engine RPM
- Seatbelt Status
- Ignition
- EV Charging Status
- EV Battery Health
- Engine Oil Life Percentage
- Tire Pressure (for all four wheels)
- Airbag Status

## Usage
- Install CARLA
- Change the values in `app.py` to reflect the CARLA server details
  - host (`0.0.0.0` if local)
  - port (`2000` by default)
  - number_of_cars: The number of cars you want in the simulation
- load the Anna Nagar map by running the `load_map` script
  ```shell
  python3 load_map.py
  ```
- run the simulation by running `app.py`
  ```shell
  python3 app.py
  ```
  
# Credits
- [SNUC Delta](https://github.com/snuc-Delta)
- [Mahasvan Mohan](https://github.com/Mahasvan)
- [Aakhil](https://github.com/AMohamedAakhil)
- [Aditya B](https://github.com/aditya20-b)
- [Joshua](https://github.com/BlitzJB)
