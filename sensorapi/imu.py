from sensorapi import SensorDataMonitor
from glovelet.utility.timeseries import DataTimeSeries
import glm


def convert_raw(time_series):
    # TODO: implement raw data convertion
    pass


class IMU6DofSensorDataFilter(SensorDataMonitor):
    def __init__(self, acc_vref, acc_sensitivity, gyr_vref, gyr_sensitivity, series_size=20):
        # Init all params as private class member variables, except "screen_size".
        # That one can be used as an argument directly to the DataTimeSeries constructor.
        self.__time_series = DataTimeSeries(series_size, 6, auto_filter=True, post_filter=convert_raw)
        # More class variables:
        # private: grav_vector(glm.vec4), grav_magnitude(float), prev_attitude(None),
        # public: velocity(glm.vec3), rotation(glm.tquat)

    def update(self, data):
        # add to time series
        # att = attitude_estimation()
        # rot = complementary_filter(att)
        # convert rot to glm.tquat type
        # self.rotation = rot
        # self.velocity ...
        pass

    def get_rotation(self, data):
        return self.rotation[:]
