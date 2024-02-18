import io
import carla

# Read the .osm data
f = io.open(r"./maps/annanagarfr.osm", mode="r", encoding="utf-8")
osm_data = f.read()
f.close()

settings = carla.Osm2OdrSettings()
settings.set_osm_way_types(["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential"])
settings.generate_traffic_lights = True
xodr_data = carla.Osm2Odr.convert(osm_data, settings)
# save opendrive file
f = open(r"./maps/annanagarxodr.xodr", 'w')
f.write(xodr_data)
f.close()
client = carla.Client('10.5.27.231', 2000)
client.set_timeout(10.0)
world = client.get_world()

vertex_distance = 20.0   # in meters
max_road_length = 1000.0 # in meters
wall_height = 3     # in meters
extra_width = 30 # in meters
world = client.generate_opendrive_world(
    xodr_data, carla.OpendriveGenerationParameters(
        vertex_distance=vertex_distance,
        max_road_length=max_road_length,
        wall_height=wall_height,
        additional_width=extra_width,
        smooth_junctions=True,
        enable_mesh_visibility=True))