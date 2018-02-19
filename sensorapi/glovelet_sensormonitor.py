from glovelet.sensorapi.sensorstream import SensorDataMonitor
from glovelet.utility.timeseries import DataTimeSeries
from glovelet.sensorapi.sensor import Sensor
from multiprocessing import Lock
import glm
import numpy as np


__all__ = ['GloveletBNO055IMUSensorMonitor']


class Bno055Sensor(Sensor):
    def __init__(self, name, ndatapoints=7):
        super().__init__(name, ndatapoints)


class FingerFlexGroup(Sensor):
    def __init__(self, name, size):
        super().__init__(name, size)
        self.__thumb = 0
        self.__index = 1
        self.__middle = 2

    @property
    def thumb(self):
        return self.__thumb

    @property
    def index(self):
        return self.__index

    @property
    def middle(self):
        return self.__middle


def axis_correction(time_series):
    data = time_series[0]
    # swap y and z and invert z
    data[1], data[2] = data[2], -data[1]
    # swap qy and qz
    # data[-2], data[-1] = -data[-1], -data[-2]
    # data[-1], data[4:] = data[3], = data[3:6]
    # data[5], data[6] = data[6], data[5]
    data[4], data[5] = data[5], data[4]
    # data[3] = -data[3]
    return data


MPU6050 = None
BNO055 = Bno055Sensor('bno055', 7)
FLEX_SENSORS = FingerFlexGroup('flexsensors', 3)


class GloveletBNO055IMUSensorMonitor(SensorDataMonitor):
    def __init__(self, imu_series_sz=20):
        super().__init__(BNO055)
        self.__timeseries = DataTimeSeries(imu_series_sz, BNO055.ndatapoints, auto_filter=True, post_filter=axis_correction)
        self.__data_lock = Lock()

    def update(self, data):
        # self.__data_lock.acquire()
        self.__timeseries.add(data)
        # self.__data_lock.release()

    def get_acceleration(self):
        # self.__data_lock.acquire()
        acceleration = np.array(self.__timeseries[0][0:3])
        # self.__data_lock.release()
        return acceleration

    def get_rotation(self):
        # self.__data_lock.acquire()
        data = self.__timeseries[0][3:7]
        rotation = glm.tquat(180, 0, 0, dtype='f') * glm.tquat(*data)
        # self.__data_lock.release()
        return rotation

    def get_time_delta(self):
        # self.__data_lock.acquire()
        dt = self.__timeseries.get_tdelta()
        # self.__data_lock.release()
        return dt

    def get_chg_velocity(self):
        # self.__data_lock.acquire()
        dt = self.__timeseries.get_tdelta()
        acc_norm = self.get_acceleration_norm()
        vel = np.zeros(3, dtype='f')
        if acc_norm > 0.15:
            vel = self.get_acceleration() * dt
        # self.__data_lock.release()
        return vel

    def get_acceleration_norm(self):
        # self.__data_lock.acquire()
        acc = self.get_acceleration()
        acc_norm = np.linalg.norm(acc)
        # self.__data_lock.release()
        return acc_norm

    def is_moving(self, norm_threshold=0.15):
        # self.__data_lock.acquire()
        acc_norm = self.get_acceleration_norm()
        is_moving = (acc_norm > norm_threshold)
        # self.__data_lock.release()
        return is_moving
