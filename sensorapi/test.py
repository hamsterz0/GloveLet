import numpy as np
from glovelet.sensorapi.sensorstream import SensorStream, SensorDataMonitor
import glovelet.sensorapi.sensorstream as sensorstream
import argparse


PORT = '/dev/ttyACM0'
BAUDRATE = 115200
CHANNEL_WIDTH = 6


np.set_printoptions(precision=4)


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
    stream.open()
    monitor = TestMonitor()
    stream.register_monitor(monitor, sensorstream.CH_ACCELEROMETER)
