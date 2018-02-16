import numpy as np
from glovelet.utility.map import Map
from glovelet.sensorapi.sensorstream import SensorStream, SensorDataMonitor
import glovelet.sensorapi.sensorstream as sensorstream
from glovelet.sensorapi.sensor import FlexSensor, FlexSensorGroup, ImuSensor, Sensor
import argparse
from random import randrange
from serial.serialutil import SerialException


PORT = '/dev/ttyACM0'
BAUDRATE = 115200
CHANNEL_WIDTH = 6


np.set_printoptions(precision=4)


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


flex_index = FlexSensor('index', 0)


class TestMonitor(SensorDataMonitor):
    def __init__(self):
        pass

    def update(self, data):
        print(data)


if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help='Path to serial port.')
    parser.add_argument('baudrate', type=int, help='Baud rate of serial device.')
    parser.add_argument('channel_width', type=int,
                        help='Channel width. This is the number of data elements expected to be read on each line of serial \
                        device output.')
    args = parser.parse_args()
    print(args)
    # set globals
    PORT = args.port
    BAUDRATE = args.baudrate
    CHANNEL_WIDTH = args.channel_width
    # initialize and open serial data stream
    stream = SensorStream(PORT, BAUDRATE, CHANNEL_WIDTH)
    stream.open()
    while stream.is_open():
        print(stream.get_data())
else:
    stream = SensorStream(PORT, BAUDRATE, CHANNEL_WIDTH)
    try:
        stream.open()
    except SerialException as e:
        print(e)
        stream.close()
    monitor = TestMonitor()
    stream.register_monitor(monitor, sensorstream.CH_ACCELEROMETER)
