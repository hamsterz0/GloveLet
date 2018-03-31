__all__ = ['GloveletBNO055IMUSensorMonitor', 'GloveletFlexSensorMonitor']


from glovelet.utility.timeseries import DataTimeSeries, DataSequence
from glovelet.utility.motion_multiplier import delta_scale, motion_multiplier
from glovelet.sensorapi.sensorstream import SensorDataMonitor
from glovelet.sensorapi.sensor import Sensor
import glm
import numpy as np
from scipy.integrate import cumtrapz
from scipy.signal import filtfilt, butter


class Bno055Sensor(Sensor):
    def __init__(self, name, ndatapoints=7):
        super().__init__(name, ndatapoints)


class Mpu6050Sensor(Sensor):
    def __init__(self, name, ndatapoints=6):
        super().__init__(name, ndatapoints)
        self.__acc_vzerog = np.array([1.09375, 1.09375, 1.09375], 'f')
        self.__acc_sensitivity = np.array([16384, 8192, 4096, 2048], np.uint8)


class FingerFlexGroup(Sensor):
    def __init__(self, name, size):
        super().__init__(name, size)


def accel_post_filter(time_series):
    data = time_series[0]
    data[1], data[2] = -data[2], -data[1]
    return data


def rot_axis_correction(time_series):
    data = time_series[0]
    data[1], data[2] = data[2], data[1]
    return data


def binary_convert(b):
    return int(bool(b))


MPU6050 = None
BNO055 = Bno055Sensor('bno055', 7)
FLEX_SENSORS = FingerFlexGroup('flexsensors', 4)


class GloveletBNO055IMUSensorMonitor(SensorDataMonitor):
    def __init__(self, acc_series_sz=20, rot_series_sz=5,
                 lowpass_order=2, lowpass_critcal=0.15,
                 highpass_order=2, highpass_critical=0.125):
        super().__init__(BNO055)
        self.__acc_timeseries = DataTimeSeries(acc_series_sz, 3,
                                           auto_filter=True,
                                           post_filter=accel_post_filter)
        self.__acc_lowpassed = DataSequence(acc_series_sz, 3)
        self.__rot_timeseries = DataTimeSeries(rot_series_sz, 4,
                                           auto_filter=True, filter_alg=None,
                                           post_filter=rot_axis_correction)
        self.__velocity = DataSequence(acc_series_sz, 3)
        self.__vel_hipassed = DataSequence(acc_series_sz, 3)
        self.__bttr_numtr_low, self.__bttr_denom_low =\
            butter(lowpass_order, lowpass_critcal, btype='lowpass')
        self.__bttr_numtr_hi, self.__bttr_denom_hi =\
            butter(highpass_order, highpass_critical, btype='highpass')

    @property
    def accel_timestamp(self):
        return self.__acc_timeseries.timestamp

    @property
    def accel_tdelta(self):
        return self.__acc_timeseries.tdelta

    @property
    def accel_time_elapsed(self):
        return self.__acc_timeseries.time_elapsed

    @property
    def orient_timestamp(self):
        return self.__rot_timeseries.timestamp

    @property
    def orient_tdelta(self):
        return self.__rot_timeseries.tdelta

    @property
    def orient_time_elapsed(self):
        return self.__rot_timeseries.time_elapsed

    @property
    def acceleration_sequence(self):
        return self.__acc_lowpassed

    @property
    def velocity_sequence(self):
        return self.__vel_hipassed
        # return self.__velocity

    @property
    def orientation_timeseries(self):
        return self.__rot_timeseries

    def update(self, data):
        b, a = self.__bttr_numtr_low, self.__bttr_denom_low
        self.__acc_timeseries.add(data[:3])
        # self.__acc_timeseries.add(delta_scale(data[:3], k_max=4, k_min=0.17, n=0))
        self.__rot_timeseries.add((data[3:]), self.__acc_timeseries.timestamp[0])
        # if self.__acc_lowpassed.added > 15:
        self.__acc_lowpassed[:, 0] = filtfilt(b, a, self.__acc_timeseries[:, 0])
        self.__acc_lowpassed[:, 1] = filtfilt(b, a, self.__acc_timeseries[:, 1])
        self.__acc_lowpassed[:, 2] = filtfilt(b, a, self.__acc_timeseries[:, 2])
        self.__update_velocity()

    def get_acceleration(self):
        acceleration = np.array(self.__acc_timeseries[0][0:3])
        return acceleration

    def get_rotation(self):
        data = self.__rot_timeseries[0]
        rotation = glm.tquat(*data)
        return rotation

    def get_tdelta(self):
        dt = self.__acc_timeseries.tdelta[0]
        return dt

    def get_timestamp(self):
        dt = self.__acc_timeseries.timestamp[0]
        return dt

    def get_velocity(self):
        return self.__vel_hipassed[0]

    def __update_velocity(self):
        acc = self.__acc_lowpassed
        t_elapsed = self.__acc_timeseries.time_elapsed
        # print(acc[0])
        self.__velocity[:, 0] = cumtrapz(acc[:, 0], t_elapsed[:], initial=0)
        self.__velocity[:, 1] = cumtrapz(acc[:, 1], t_elapsed[:], initial=0)
        self.__velocity[:, 2] = cumtrapz(acc[:, 2], t_elapsed[:], initial=0)
        # self.__velocity[:, 0] = cumtrapz(acc[:, 0], t_elapsed[:], initial=acc[:, 0][0])
        # self.__velocity[:, 1] = cumtrapz(acc[:, 1], t_elapsed[:], initial=acc[:, 1][0])
        # self.__velocity[:, 2] = cumtrapz(acc[:, 2], t_elapsed[:], initial=acc[:, 2][0])
        b, a = self.__bttr_numtr_hi, self.__bttr_denom_hi
        self.__velocity[:, 0] = filtfilt(b, a, self.__velocity[:, 0])
        self.__velocity[:, 1] = filtfilt(b, a, self.__velocity[:, 1])
        self.__velocity[:, 2] = filtfilt(b, a, self.__velocity[:, 2])
        self.__vel_hipassed.add(self.__vel_hipassed[0] + self.__velocity[4])

    def get_acceleration_norm(self):
        acc = self.get_acceleration()
        acc_norm = np.linalg.norm(acc)
        return acc_norm

    def is_moving(self, norm_threshold=0.19):
        acc_norm = self.get_acceleration_norm()
        is_moving = (acc_norm > norm_threshold)
        return is_moving


class GloveletFlexSensorMonitor(SensorDataMonitor):
    def __init__(self, series_sz=10):
        super().__init__(FLEX_SENSORS)
        self.__timeseries = DataTimeSeries(series_sz, FLEX_SENSORS.ndatapoints, auto_filter=False)

    @property
    def data_sequence(self):
        return self.__timeseries[:]

    @property
    def timestamps(self):
        return self.__timeseries.timestamp[:]

    @property
    def time_elapsed(self):
        return self.__timeseries.time_elapsed[:]

    def update(self, data):
        self.__timeseries.add(data)

    def get_flex_data(self):
        return self.__timeseries[0]


class GloveletMPU6050IMUSensorMonitor(SensorDataMonitor):
    def __init__(self, accel_series_sz=20, gyro_series_sz=8):
        super().__init__(MPU6050)
        self.__acc_timeseries = DataTimeSeries(20, 6, auto_filter=True, )
