from generator import GenerateTraffic
import sys, os, glob

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

if __name__ == '__main__':

    try:
        traffic1 = GenerateTraffic(number_of_vehicles=2, host='10.5.27.231', safe=True, respawn=False)
        traffic1.start_traffic()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
