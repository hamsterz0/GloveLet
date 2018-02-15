import serial
from enum import Enum
import numpy as np
import threading
import time
import logging
import sys
from ctypes import c_float


__all__ = [
    'SensorStreamDataChannel', 'SensorStreamConnectionStatus', 'SensorDataMonitor', 'SensorStream',
    'CH_ACCELEROMETER', 'CH_GYROSCOPE', 'CH_MAGNETOMETER', 'CH_FLEX_SENSOR01', 'CH_FLEX_SENSOR02',
    'CH_FLEX_SENSOR03', 'CH_FLEX_SENSOR04', 'CH_FLEX_SENSOR05', 'CH_IMU_6DOF', 'CH_IMU_9DOF', 'CH_ALL',
    'DEFAULT_CHANNELS'
]


class SensorStreamDataChannel:
    def __init__(self, name, ch_range):
        if not isinstance(ch_range, tuple) or len(ch_range) != 2:
            raise TypeError('Expected tuple of length 2 for argument \'ch_range\'.')
        self.__name = name
        self.__ch_range = range(*ch_range)

    def get_name(self):
        """
        Get channel name.\n
        This is the channel name.
        """
        return self.__name

    def get_range(self):
        return self.__ch_range

    def get_start(self):
        return self.__ch_range.start

    def get_stop(self):
        return self.__ch_range.stop

    def get_width(self):
        """
        Get channel width.\n
        This is the number of data features this channel monitors.\t
        :returns: `int`
        """
        return len(self.__ch_range)


# DEFAULT_CHANNELS keys
_CH_ACCELEROMETER = 'accelerometer'
_CH_GYROSCOPE = 'gyroscope'
_CH_MAGNETOMETER = 'magnetometer'
_CH_FLEX_SENSOR01 = 'flexsensor01'
_CH_FLEX_SENSOR02 = 'flexsensor02'
_CH_FLEX_SENSOR03 = 'flexsensor03'
_CH_FLEX_SENSOR04 = 'flexsensor04'
_CH_FLEX_SENSOR05 = 'flexsensor05'
_CH_IMU_6DOF = 'imu6dof'
_CH_IMU_9DOF = 'imu9dof'
_CH_ALL = 'all'
# DEFAULT_CHANNELS dict initialization
DEFAULT_CHANNELS = {
    _CH_ACCELEROMETER: SensorStreamDataChannel(_CH_ACCELEROMETER, (0, 3)),
    _CH_GYROSCOPE: SensorStreamDataChannel(_CH_GYROSCOPE, (3, 6)),
    _CH_MAGNETOMETER: SensorStreamDataChannel(_CH_MAGNETOMETER, (6, 9)),
    _CH_FLEX_SENSOR01: SensorStreamDataChannel(_CH_FLEX_SENSOR01, (9, 10)),
    _CH_FLEX_SENSOR02: SensorStreamDataChannel(_CH_FLEX_SENSOR02, (10, 11)),
    _CH_FLEX_SENSOR03: SensorStreamDataChannel(_CH_FLEX_SENSOR03, (11, 12)),
    _CH_FLEX_SENSOR04: SensorStreamDataChannel(_CH_FLEX_SENSOR04, (12, 13)),
    _CH_FLEX_SENSOR05: SensorStreamDataChannel(_CH_FLEX_SENSOR05, (13, 14)),
    _CH_IMU_6DOF: SensorStreamDataChannel(_CH_IMU_6DOF, (0, 6)),
    _CH_IMU_9DOF: SensorStreamDataChannel(_CH_IMU_9DOF, (0, 9)),
    _CH_ALL: SensorStreamDataChannel(_CH_ALL, (0, 14))
}
CH_ACCELEROMETER = DEFAULT_CHANNELS[_CH_ACCELEROMETER]
CH_GYROSCOPE = DEFAULT_CHANNELS[_CH_GYROSCOPE]
CH_MAGNETOMETER = DEFAULT_CHANNELS[_CH_MAGNETOMETER]
CH_FLEX_SENSOR01 = DEFAULT_CHANNELS[_CH_FLEX_SENSOR01]
CH_FLEX_SENSOR02 = DEFAULT_CHANNELS[_CH_FLEX_SENSOR02]
CH_FLEX_SENSOR03 = DEFAULT_CHANNELS[_CH_FLEX_SENSOR03]
CH_FLEX_SENSOR04 = DEFAULT_CHANNELS[_CH_FLEX_SENSOR04]
CH_FLEX_SENSOR05 = DEFAULT_CHANNELS[_CH_FLEX_SENSOR05]
CH_IMU_6DOF = DEFAULT_CHANNELS[_CH_IMU_6DOF]
CH_IMU_9DOF = DEFAULT_CHANNELS[_CH_IMU_9DOF]
CH_ALL = DEFAULT_CHANNELS[_CH_ALL]


class SensorStreamConnectionStatus(int, Enum):
    OPEN = 0
    CONNECTING = 1
    CLOSING = 2
    CLOSED = 3
    PAUSED = 4


class DataReadException(Exception):
    pass


class SensorDataMonitor:
    """
    *Abstract interface class. Must define `update(self, data)` where argument `data` is a numpy array.*\n
    Optionally define `on_register` to perform subroutine on registration with a `SensorStream` object.
    """

    def __init__(self):
        self.__channel = None

    def get_data_channel(self):
        """
        Get data channel.\n
        :returns: `SensorStreamDataChannel`
        """
        return self.__channel

    def set_data_channel(self, channel):
        """
        Set the data channel to monitor.\n
        WARNING:\t
        \tUnder normal circumstances, do not call this method.\t
        \tThe `SensorStream` class uses this method to set the\t
        \tdata channel when registering a `SensorDataMonitor`.\t
        :param `channel`: `SensorStreamDataChannel`
        """
        if isinstance(channel, SensorStreamDataChannel):
            self.__channel = channel
        else:
            raise TypeError('sensorapi.SensorStreamDataChannel object expected as argument.')

    def update(self, data):
        """
        *Abstract interface method. Implement subroutine for handling data.*\n
        This is the method `SensorStream` will invoke when updating its\t
        registered `SensorDataMonitor` objects.
        """
        raise NotImplementedError

    def on_register(self, sensor_stream):
        """
        *Abstract interface method. Optional.*\n
        This is the method `SensorStream` will invoke when registering\t
        this `SensorDataMonitor` object. The `SensorStream` will pass\t
        """
        pass


class SensorStream:
    """Streams sensor data to registered `SensorDataMonitor` objects."""
    # Default channels defined as globals here for convenience.
    global CH_ACCELEROMETER, CH_GYROSCOPE, CH_MAGNETOMETER, CH_FLEX_SENSOR01, CH_FLEX_SENSOR02,\
        CH_FLEX_SENSOR03, CH_FLEX_SENSOR04, CH_FLEX_SENSOR05, CH_IMU_6DOF, CH_IMU_9DOF, CH_ALL

    def __init__(self, port, baud, channel_width, conn_success_str='successful@', conn_timeout=10.0):
        """
        Construct a SensorStream object.\n
        :param `port`: `str` path to port\t
        :param `baud`: `int` baudrate of port\t
        :param `channel_width`: `int` number of data features per sample\t
        :param `conn_success_str`: `str` The string sent by the serial device to indicate successful connection established.\t
        :param `conn_timeout`: `float` seconds before connection attempt times out
        """
        self.__serial = serial.Serial(timeout=conn_timeout)
        self.__serial.port = port
        self.__serial.baudrate = baud
        self.__channel_width = channel_width
        self.__success_str = conn_success_str
        self.__timeout = conn_timeout
        self.__conn_status = SensorStreamConnectionStatus.CLOSED
        self.__registered_monitors = set()
        self.__channels = dict()
        self.__init_default_channels()
        # TODO: Remove logging module and statements once project-wide logging is implemented
        self.__logger = logging.Logger(name='SensorStream', level=logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(levelname)s][%(name)s]: %(message)s')
        handler.setFormatter(fmt)
        self.__logger.addHandler(handler)

    def get_channels(self):
        """Get key values of registered channels."""
        return self.__channels.keys()

    def get_connection_status(self):
        """
        Current connection status.\n
        :returns: `SensorStreamConnectionStatus` enum value corresponding to the
        current connection status of this `SensorStream` object.
        """
        return self.__conn_status

    def update(self):
        """Issues an update to all of the registered sensors."""
        data = self.get_data()
        for monitor in self.__registered_monitors:
            ch = monitor.get_data_channel()
            monitor.update(data[ch.get_start():ch.get_stop()])

    def get_data(self):
        """Read from stream."""
        if self.is_open():
            line = self.__readline()
            line = line.strip().split(" ")
            data = np.zeros(self.__channel_width, c_float)
            try:
                n = len(line)
                if n != self.__channel_width:
                    raise DataReadException('get_data:  Incorrect sample width read from serial device.')
                data = np.array(line, c_float)
            except UnicodeDecodeError as e:
                self.__logger.error(str(e))
                self.__logger.warning('get_data:  Unable to parse data as float.')
            except DataReadException as e:
                self.__logger.error(str(e))
            return data
        else:
            self.__logger.error('get_data:  Serial connection is closed.')
            return None

    def register_monitor(self, monitor, channel):
        """
        Register a `SensorDataMonitor` object to recieve data updates on the specified data channel.\n
        :param monitor: `SensorDataMonitor` object to register for updates\t
        :param data_channel: `SensorDataChannel` channel enum value
        """
        if not isinstance(monitor, SensorDataMonitor):
            raise TypeError('Expected SensorDataMonitor object, received ' + type(monitor) + ' instead.')
        if channel.get_name() not in self.__channels:
            raise KeyError('Channel \'' + channel.get_name() + '\' not found in registered channels.')
        monitor.set_data_channel(channel)
        # TODO: Consider making a 'proxy' SensorStream class that only and passing that instead
        monitor.on_register(self)
        self.__registered_monitors.add(monitor)

    def register_channel(self, channel_name, channel_range):
        channel = SensorStreamDataChannel(channel_name, channel_range)
        self.__channels[channel_name] = channel

    def open(self):
        """
        Open serial connection.\n
        :raises: `TimeoutError` if the connection timed out.
        """
        if self.get_connection_status() is SensorStreamConnectionStatus.CLOSED:
            self.__set_conn_status(SensorStreamConnectionStatus.CONNECTING)
            self.__serial.open()
            t1 = time.time()
            # repeats until successful connection has been established or timeout occurs
            while True:
                line = self.__readline()
                data = line.strip().split(" ")
                # check for the success string
                if self.__success_str in data:
                    break
                if time.time() - t1 > self.__timeout:
                    self.close()
                    raise TimeoutError('SensorStream connection timeout.')
            self.__set_conn_status(SensorStreamConnectionStatus.OPEN)

    def is_open(self):
        return self.get_connection_status() is SensorStreamConnectionStatus.OPEN

    def pause(self):
        # TODO: Implement a pause feature for the data stream
        raise NotImplementedError

    def close(self):
        """Close the connection to the serial port."""
        if self.get_connection_status() is not SensorStreamConnectionStatus.CLOSED:
            self.__set_conn_status(SensorStreamConnectionStatus.CLOSING)
            self.__serial.close()
            self.__set_conn_status(SensorStreamConnectionStatus.CLOSED)

    def __set_conn_status(self, status):
        self.__logger.debug(status.name)
        self.__conn_status = status

    def __readline(self):
        success = False
        line = None
        while not success:
            try:
                line = self.__serial.readline().decode('utf-8')
                success = True
            except UnicodeError as e:
                self.__logger.warning(e)
                continue
        return line

    def __init_default_channels(self):
        self.__channels = DEFAULT_CHANNELS

    def __del__(self):
        self.close()
