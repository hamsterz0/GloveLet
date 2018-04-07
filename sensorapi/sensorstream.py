__all__ = ['SensorStreamConnectionStatus', 'SensorDataMonitor', 'SensorStream']


import serial
from enum import Enum
import numpy as np
from multiprocessing import Lock
import time
import logging
import sys
from glovelet.sensorapi.sensorstreamchannel import SensorStreamDataChannel
from glovelet.sensorapi.sensor import Sensor
from ctypes import c_float


class SensorStreamConnectionStatus(int, Enum):
    OPEN = 0
    CONNECTING = 1
    CLOSING = 2
    CLOSED = 3
    PAUSED = 4


class SensorStreamReadException(Exception):
    pass


class SensorDataMonitor:
    """
    *Abstract interface class. Must define `update(self, data)` where argument `data` is a numpy array.*\n
    Optionally define `on_register` to perform subroutine on registration with a `SensorStream` object.
    """

    def __init__(self, sensor):
        if not isinstance(sensor, Sensor):
            raise TypeError('Expected `Sensor` object for argument `sensor`.')
        self.__sensor = sensor

    @property
    def sensor(self):
        return self.__sensor

    def set_sensor(self, sensor):
        """
        Set the sensor to monitor.\n
        WARNING:\t
        \tUnder normal circumstances, do not call this method.\t
        \tThe `SensorStream` class uses this method to set the\t
        \tsensor when registering a `SensorDataMonitor`. If it\t
        \tis necessary to monitor another
        :param `sensor`: `Sensor`
        """
        if not isinstance(sensor, Sensor):
            raise TypeError('Expected `SensorStreamDataChannel` object for `channel` argument.')
        self.__sensor = sensor

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

    def __init__(self, port, baud,
                 do_success_check=True,
                 conn_success_str='successful@',
                 conn_delay=0,
                 conn_timeout=10.0):
        """
        Construct a SensorStream object.\n
        :param `port`: `str` path to port\t
        :param `baud`: `int` baudrate of port\t
        :param `do_success_check`: `bool` will skip process of matching the success string when `False`
        :param `conn_success_str`: `str` The string sent by the serial device to indicate successful connection established.\t
        :param `conn_delay`: `int` The number of milliseconds to delay connection (gives device a chance to run setup protocol).\t
        :param `conn_timeout`: `float` seconds before connection attempt times out
        """
        self.__serial = serial.Serial(timeout=conn_timeout)
        self.__serial.port = port
        self.__serial.baudrate = baud
        self.__do_success_check = do_success_check
        self.__conn_delay = conn_delay
        self.__ndatapoints = 0
        self.__success_str = conn_success_str
        self.__timeout = conn_timeout
        self.__conn_status = SensorStreamConnectionStatus.CLOSED
        self.__registered_monitors = set()
        self.__registered_sensors = dict()
        self.__read_offset = None
        # TODO: Remove logging module and statements once project-wide logging is implemented
        self.__logger = logging.Logger(name='SensorStream', level=logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(levelname)s][%(name)s]: %(message)s')
        handler.setFormatter(fmt)
        self.__logger.addHandler(handler)

    def get_connection_status(self):
        """
        Current connection status.\n
        :returns: `SensorStreamConnectionStatus` enum value corresponding to the
        current connection status of this `SensorStream` object.
        """
        return self.__conn_status

    def update(self):
        """Issues an update to all of the registered sensors."""
        data = self.read_data()
        if data is None:
            return
        for monitor in self.__registered_monitors:
            start, stop = monitor.sensor.channel.get_start(), monitor.sensor.channel.get_stop()
            monitor.update(data[start:stop])

    def read_data(self):
        """Read from stream."""
        if self.is_open():
            line = self.__readline()
            line = line.strip().split(" ")
            data = None
            try:
                if len(line) < self.__ndatapoints:
                    raise SensorStreamReadException('Incorrect number of data dimensions read from serial device.')
                data = np.array(line, c_float)
            except UnicodeDecodeError as e:
                self.__logger.error(str(e))
                self.__logger.warning('Unable to parse data as float.')
            except ValueError as e:
                self.__logger.warning(str(e))
            except SensorStreamReadException as e:
                self.__logger.warning(str(e))
            return data
        else:
            self.__logger.warning('Attempt to invoke `read_data` while connection is closed.')
            return None

    def register_monitor(self, monitor):
        """
        Register a `SensorDataMonitor` object.\n
        Registered monitors recieve updates on the channel they specify.\t
        On registering a new monitor, the channel offset will be set such that the new monitor's
        channel offset starts where the previously registered monitor's channel ends. This means that
        monitors should be registered in the order that their data values are read from each
        line of serial output.\t
        I.E:\t
        \t
        \tserial output:  0 0 0 0 0 0 0 0 0\t
        \t                ^         ^ ^ ^ ^\t
        \t                imu       f f f f\t
        \t                          l l l l\t
        \t                          e e e e\t
        \t                          x x x x\t
        \t                          0 1 2 3\t
        \t
        \tadd in order: imu, flex0, flex1, flex2, flex3
        :param monitor: `SensorDataMonitor` object to register for updates\t
        """
        if not isinstance(monitor, SensorDataMonitor):
            raise TypeError('Expected SensorDataMonitor object, received ' + type(monitor) + ' instead.')
        # TODO: Consider making a 'proxy' SensorStream class and passing that instead
        self.__register_sensor(monitor.sensor)
        monitor.on_register(self)
        self.__registered_monitors.add(monitor)

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
            while self.__do_success_check:
                line = self.__readline()
                data = line.strip().split(" ")
                # check for the success string
                if self.__success_str in data:
                    break
                if time.time() - t1 > self.__timeout:
                    self.close()
                    raise TimeoutError('SensorStream connection timeout.')
            time.sleep(self.__conn_delay / 1000)
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

    def __register_sensor(self, sensor):
        """Registers a `Sensor` object with the stream."""
        for name, s in self.__registered_sensors.items():
            if s.channel.get_stop() > sensor.channel.offset:
                ch_offset = s.channel.get_stop()
                sensor.set_channel_offset(ch_offset)
        self.__registered_sensors[sensor.name] = sensor
        if self.__read_offset is None or self.__read_offset > sensor.channel_offset:
            self.__read_offset = sensor.channel_offset
        self.__ndatapoints += sensor.ndatapoints

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

    def __del__(self):
        self.close()
