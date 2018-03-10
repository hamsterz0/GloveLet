__all__ = ['GloveletImuEvent', 'GloveletFlexEvent', 'GloveletSensorListener', 'GloveletSensorEventDispatcher']


import numpy as np
from multiprocessing import Queue

from glovelet.eventapi.event import Event, EventListener, EventDispatcher
from glovelet.sensorapi.sensorstream import SensorStream
from glovelet.sensorapi.glovelet_sensormonitor import GloveletBNO055IMUSensorMonitor, GloveletFlexSensorMonitor


class GloveletImuEvent(Event):
    def __init__(self, accel, vel, orient, accel_elapsed):
        self.acceleration = accel[:]
        self.velocity = vel[:]
        self.orientation = orient[:]
        self.motion_elapsed = accel_elapsed[:]


class GloveletImuEventFlipped(Event):
    def __init__(self, accel, vel, orient, accel_elapsed):
        self.accel_x = np.flip(accel[:, 0], 0)
        self.accel_y = np.flip(accel[:, 1], 0)
        self.accel_z = np.flip(accel[:, 2], 0)
        self.vel_x = np.flip(vel[:, 0], 0)
        self.vel_y = np.flip(vel[:, 1], 0)
        self.vel_z = np.flip(vel[:, 2], 0)
        self.orient_x = np.flip(orient[:, 0], 0)
        self.orient_y = np.flip(orient[:, 1], 0)
        self.orient_z = np.flip(orient[:, 2], 0)
        self.orient_w = np.flip(orient[:, 3], 0)
        self.t_elapsed = np.flip(accel_elapsed[:], 0)
        self.vel_max = max([max(vel[:, i]) for i in range(3)])
        self.vel_min = min([min(vel[:, i]) for i in range(3)])
        self.accel_max = max([max(accel[:, i]) for i in range(3)])
        self.accel_min = min([min(accel[:, i]) for i in range(3)])


class GloveletFlexEvent(Event):
    def __init__(self, data, tstamps, time_elapsed):
        self.data = data
        self.tstamps = tstamps
        self.time_elapsed = time_elapsed


class GloveletImuEventDispatcher(EventDispatcher):
    def __init__(self, port, baud, acc_series_sz=50, rot_series_sz=5):
        super().__init__(GloveletImuEvent)
        self.__stream = None
        self._port = port
        self._baud = baud
        self.__acc_series_sz = acc_series_sz
        self.__rot_series_sz = rot_series_sz

    def init(self):
        self.__stream = SensorStream(self._port, self._baud)
        imu_monitor = GloveletBNO055IMUSensorMonitor(acc_series_sz=self.__acc_series_sz,
                                                     rot_series_sz=self.__rot_series_sz)
        self.__stream.register_monitor(imu_monitor)
        self.__stream.open()
        while not self.__stream.is_open():
            continue
        return (imu_monitor,), {}

    def update(self, imu_monitor):
        if self.__stream.is_open():
            self.__stream.update()
            imu_event = GloveletImuEvent(imu_monitor.acceleration_timeseries,
                                         imu_monitor.velocity_timeseries,
                                         imu_monitor.orientation_timeseries,
                                         imu_monitor.time_elapsed)
            return imu_event

    def finish(self, *args, **kwargs):
        self.__stream.close()


class GloveletImuPlotEventDispatcher(EventDispatcher):
    def __init__(self, sensor_stream, acc_series_sz=50, rot_series_sz=5):
        super().__init__(GloveletImuEventFlipped)
        self.__stream = sensor_stream
        self.__acc_series_sz = acc_series_sz
        self.__rot_series_sz = rot_series_sz

    def init(self):
        imu_monitor = GloveletBNO055IMUSensorMonitor(acc_series_sz=self.__acc_series_sz,
                                                     rot_series_sz=self.__rot_series_sz)
        self.__stream.register_monitor(imu_monitor)
        self.__stream.open()
        while not self.__stream.is_open():
            continue
        return (imu_monitor,), {}

    def update(self, imu_monitor):
        if self.__stream.is_open():
            self.__stream.update()
            imu_event = GloveletImuEventFlipped(imu_monitor.acceleration_timeseries,
                                         imu_monitor.velocity_timeseries,
                                         imu_monitor.orientation_timeseries,
                                         imu_monitor.time_elapsed)
            return imu_event

    def finish(self, *args, **kwargs):
        self.__stream.close()


class GloveletSensorEventDispatcher(EventDispatcher):
    def __init__(self, port, baud):
        super().__init__(GloveletImuEvent, GloveletFlexEvent)
        self.port = port
        self.baud = baud

    def init(self):
        stream = SensorStream(self.port, self.baud)
        imu_monitor = GloveletBNO055IMUSensorMonitor()
        flex_monitor = GloveletFlexSensorMonitor()
        stream.register_monitor(imu_monitor)
        stream.register_monitor(flex_monitor)
        stream.open()
        while not stream.is_open():
            continue
        return (stream, imu_monitor, flex_monitor), {}

    def update(self, stream, imu_monitor, flex_monitor):
        if stream.is_open():
            stream.update()
            imu_event = GloveletImuEvent(imu_monitor.acceleration_timeseries[:],
                                         imu_monitor.velocity_timeseries[:],
                                         imu_monitor.orientation_timeseries[:],
                                         imu_monitor.acceleration_timeseries.timestamp[:],
                                         imu_monitor.acceleration_timeseries.time_elapsed[:],
                                         imu_monitor.orientation_timeseries.timestamp[:],
                                         imu_monitor.orientation_timeseries.time_elapsed[:])
            flex_event = GloveletFlexEvent(flex_monitor.data_sequence[:],
                                           flex_monitor.timestamps[:],
                                           flex_monitor.time_elapsed[:])
            return imu_event, flex_event

    def finish(self, stream, *args, **kwargs):
        stream.close()


class GloveletImuListener(EventListener):
    def __init__(self):
        callbacks = {GloveletImuEvent: self.on_imu_event}
        super().__init__(callbacks)
        self.acceleration = None
        self.velocity = None
        self.orientation = None

    def on_imu_event(self, event):
        self.acceleration = event.acceleration
        self.velocity = event.velocity
        self.orientation = event.orientation


class GloveletImuPlotListener(EventListener):
    def __init__(self):
        callbacks = {GloveletImuEventFlipped: self.on_imu_event}
        super().__init__(callbacks)
        self.event = None

    def on_imu_event(self, event):
        self.event = event


# TODO: Finish implementation!
class GloveletSensorListener(EventListener):
    def __init__(self):
        callbacks = {GloveletImuEvent: self.on_imu_event, GloveletFlexEvent: self.on_flex_event}
        super().__init__(callbacks)
        self.accel = None
        self.velocity = None

    def on_imu_event(self, event):
        raise NotImplementedError

    def on_flex_event(self, event):
        raise NotImplementedError
