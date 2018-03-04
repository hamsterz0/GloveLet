#!../venv/bin/python
import numpy as np
from glovelet.utility.map import Map
from glovelet.utility.motion_multiplier import motion_multiplier, u, delta_scale
from glovelet.utility.timeseries import DataTimeSeries, DataSequence
from glovelet.sensorapi.sensorstream import SensorStream, SensorDataMonitor
import glovelet.sensorapi.sensorstream as sensorstream
from glovelet.sensorapi.sensor import Sensor
from glovelet.sensorapi.glovelet_sensormonitor import GloveletBNO055IMUSensorMonitor
from multiprocessing import Process
import argparse
import time
from random import randrange
from serial.serialutil import SerialException


PORT = '/dev/ttyACM0'
BAUDRATE = 115200
CHANNEL_WIDTH = 6


np.set_printoptions(precision=4)


def loop(sensor_stream, monitor):
    while sensor_stream.is_open():
        sensor_stream.update()
        # print('acc:' + str(monitor.get_acceleration()) + ' : rot:' + str(monitor.get_rotation().value) )


def get_u_test(sz=20, mx=50):
    return [randrange(0, mx) for i in range(sz)]


def u(dr, n=2, k_max=20, k_min=4, m=-1):
    if dr < k_min:
        return -1
    elif dr >= k_max:
        return n
    return ((n + m) * (dr / k_max)) - 1


def u_test(sz=20, mx=50, n=2, k_max=20, k_min=4):
    vals = get_u_test(sz, mx)
    for v in vals:
        res = u(v)
        print('u({: .4f}) = {: .4f}'.format(v, res))
        assert res >= -1 and res <= n


class MapTest(Map):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

    @property
    def index(self):
        print('okay')


class TestMonitor(SensorDataMonitor):
    def __init__(self):
        pass

    def update(self, data):
        print(data)


def stream_test(port, baud):
    stream = SensorStream(port, baud)
    monitor = GloveletBNO055IMUSensorMonitor()
    stream.register_monitor(monitor)
    try:
        stream.open()
    except SerialException as e:
        print(e)
        stream.close()
    while(stream.is_open()):
        stream.update()
        print('acc:' + str(monitor.get_acceleration()) + ', acc_norm:' + str(monitor.get_acceleration_norm()) + ' : rot:' + str(monitor.get_rotation().value))


def dscale_test(stream, bno055, nsamples=50, args=(), kwargs={}):
    if not stream.is_open():
        stream.open()
        time.sleep(5.0)
    for i in range(nsamples):
        stream.update()
        acc = bno055.get_acceleration()
        acc_scale = delta_scale(acc, *args, **kwargs)
        print(str(acc) + " : " + str(acc_scale))


def print_velocity(stream, bno055, times=50):
    for i in range(times):
        stream.update()
        print(str(bno055.get_velocity()) + ' :: {: .4f}'.format(monitor.get_time_delta()))


if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=str, default=PORT, help='Path to serial port. Default path is /dev/ttyACM0.')
    parser.add_argument('--baudrate', '-b', type=int, default=BAUDRATE, help='Baud rate of serial device. Default is 115200')
    args = parser.parse_args()
    print(args)
    # set globals
    PORT = args.port
    BAUDRATE = args.baudrate
    # Run SesnorStream test
    stream_test(PORT, BAUDRATE)
else:
    stream = SensorStream(PORT, BAUDRATE)
    monitor = GloveletBNO055IMUSensorMonitor()
    stream.register_monitor(monitor)
    stream.open()
    s = stream
    m = monitor
    v = np.array([0.12, -0.07, 0.21], 'f')
    dr = np.array([0.02, -0.05, 0.10], 'f')
    dr_scale = (5.0, 0.15, 0.5)
