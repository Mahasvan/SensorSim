from pydantic import BaseModel, Field
import yaml
from pprint import pprint 
from typing import List, Dict, Union, Optional
from enum import Enum

class TireConfig(BaseModel):
    position: str
    pressure_value: int

class DataPoint(BaseModel):
    interval: int
    unit: str
    statuses: Optional[List[str]] = None
    tires: Optional[List[TireConfig]] = None

class VehicleType(str, Enum):
    gasoline = 'gasoline'
    electric = 'electric'

class VehicleDataPoints(BaseModel):
    odometer: Optional[DataPoint] = None
    fuel_level: Optional[DataPoint] = None
    speed: Optional[DataPoint] = None
    acceleration: Optional[DataPoint] = None
    seatbelt_status: Optional[DataPoint] = None
    ignition: Optional[DataPoint] = None
    EV_charging_status: Optional[DataPoint] = None
    EV_battery_level: Optional[DataPoint] = None
    engine_RPM: Optional[DataPoint] = None
    tire_pressure: Optional[DataPoint] = None
    oil_level: Optional[DataPoint] = None


class Vehicle(BaseModel):
    vehicle_id: str
    type: VehicleType
    data_points: VehicleDataPoints

class Fleet(BaseModel):
    vehicles: List[Vehicle]

# Load the YAML configuration file into a Pydantic model
def load_config(fname = 'config.yaml'):
    with open(fname, 'r') as f:
        yaml_config = yaml.safe_load(f)
        vehicles = Fleet(**yaml_config)  
        return vehicles
