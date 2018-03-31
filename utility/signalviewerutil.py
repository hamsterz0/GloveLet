import numpy as np
import matplotlib.pyplot as plt
from glovelet.sensorapi.sensorstream import SensorStream
from glovelet.sensorapi.glovelet_sensormonitor import GloveletBNO055IMUSensorMonitor, GloveletFlexSensorMonitor
from glovelet.utility.timeseries import DataSequence
from multiprocessing import Process, Queue
from serial.serialutil import SerialException
from scipy.signal import butter, filtfilt


np.set_printoptions(precision=4, suppress=True)


_PORT = '/dev/ttyACM0'
_BAUD = 115200


class ImuEvent:
    def __init__(self, velocity, acceleration, rotation, timestamp, tdelta):
        self.velocity = velocity
        self.acceleration = acceleration
        self.quaternion = rotation
        self.timestamp = timestamp
        self.tdelta = tdelta


class ImuPlotEvent:
    def __init__(self, acc_timeseries, vel_timeseries, rot_timeseries, dt_seq, t_seq):
        self.t_seq = np.flip(t_seq[:], 0)
        self.accel_x = np.flip(acc_timeseries[:, 0], 0)
        self.accel_y = np.flip(acc_timeseries[:, 1], 0)
        self.accel_z = np.flip(acc_timeseries[:, 2], 0)
        self.accel_max = max([max(acc_timeseries[:, i]) for i in range(3)])
        self.accel_min = min([min(acc_timeseries[:, i]) for i in range(3)])
        self.vel_x = np.flip(vel_timeseries[:, 0], 0)
        self.vel_y = np.flip(vel_timeseries[:, 1], 0)
        self.vel_z = np.flip(vel_timeseries[:, 2], 0)
        self.vel_max = max([max(vel_timeseries[:, i]) for i in range(3)])
        self.vel_min = min([min(vel_timeseries[:, i]) for i in range(3)])
        self.orient_x = np.flip(rot_timeseries[:, 0], 0)
        self.orient_y = np.flip(rot_timeseries[:, 1], 0)
        self.orient_z = np.flip(rot_timeseries[:, 2], 0)
        self.orient_w = np.flip(rot_timeseries[:, 3], 0)


class FlexPlotEvent:
    def __init__(self, flex_data, t_elapsed):
        self.index = np.flip(flex_data[:, 0], 0)
        self.middle = np.flip(flex_data[:, 1], 0)
        self.thumb0 = np.flip(flex_data[:, 2], 0)
        self.thumb1 = np.flip(flex_data[:, 3], 0)
        self.t_elapsed = np.flip(t_elapsed[:], 0)


def imu_stream(stream, monitor, q):
    try:
        stream.open()
        while stream.is_open():
            stream.update()
            imu_pltevnt = ImuPlotEvent(monitor.acceleration_sequence,
                                          monitor.velocity_sequence,
                                          monitor.orientation_timeseries,
                                          monitor.accel_tdelta, monitor.accel_time_elapsed)
            if q.full():
                q.get()
            q.put(imu_pltevnt)
            # print(' '.join([str(x) for x in monitor.orientation_timeseries[0]]))
    except SerialException as e:
        print(e)
        stream.close()


def flex_stream(stream, monitor, q):
    try:
        stream.open()
        while stream.is_open():
            stream.update()
            flex_pltevnt = FlexPlotEvent(monitor.data_sequence, monitor.time_elapsed)
            if q.full():
                q.get()
            q.put(flex_pltevnt)
    except SerialException as e:
        print(e)
    finally:
        stream.close()


def plot_imu_data(nsamples=None):
    if nsamples is None:
        nsamples = 500000
    s = SensorStream(_PORT, _BAUD, do_success_check=False, conn_delay=500)
    m = GloveletBNO055IMUSensorMonitor(100)
    s.register_monitor(m)
    pltevntqueue = Queue(5)
    stream_proc = Process(target=imu_stream, args=(s, m, pltevntqueue))
    stream_proc.start()
    plt.ion()
    fig = plt.figure(figsize=(8, 10))
    shape_orient = m.orientation_timeseries.shape
    acc_ax = fig.add_subplot(311)
    vel_ax = fig.add_subplot(312)
    quat_ax = fig.add_subplot(313)
    while pltevntqueue.empty():
        continue
    pltevnt = pltevntqueue.get()
    t_seq = pltevnt.t_seq
    line1, = acc_ax.plot(t_seq, pltevnt.accel_x, 'r-', label='x')
    line2, = acc_ax.plot(t_seq, pltevnt.accel_y, 'g-', label='y')
    line3, = acc_ax.plot(t_seq, pltevnt.accel_z, 'b-', label='z')
    vel_x, = vel_ax.plot(t_seq[:], pltevnt.vel_x, 'r-', label='x')
    vel_y, = vel_ax.plot(t_seq[:], pltevnt.vel_y, 'g-', label='y')
    vel_z, = vel_ax.plot(t_seq[:], pltevnt.vel_z, 'b-', label='z')
    t_seq_quat = t_seq[:shape_orient[0]]
    quat_line1, quat_line2,\
    quat_line3, quat_line4 = quat_ax.plot(t_seq_quat, pltevnt.orient_w, 'k-',
                                      t_seq_quat, pltevnt.orient_x, 'c-',
                                      t_seq_quat, pltevnt.orient_y, 'm-',
                                      t_seq_quat, pltevnt.orient_z, 'y-')
    quat_ax.set_ylim(-1, 1)
    plt.show()
    for i in range(nsamples):
        pltevnt = pltevntqueue.get()
        if isinstance(pltevnt, ImuPlotEvent):
            t_seq = pltevnt.t_seq
            line1.set_data(t_seq, pltevnt.accel_x)
            line2.set_data(t_seq, pltevnt.accel_y)
            line3.set_data(t_seq, pltevnt.accel_z)
            acc_ax.set_ylim((min(pltevnt.accel_min, -5), max(pltevnt.accel_max, 5)))
            acc_ax.set_xlim((min(t_seq), max(t_seq)))
            vel_x.set_data(t_seq[:], pltevnt.vel_x)
            vel_y.set_data(t_seq[:], pltevnt.vel_y)
            vel_z.set_data(t_seq[:], pltevnt.vel_z)
            vel_ax.set_ylim((min(pltevnt.vel_min, -2), max(pltevnt.vel_max, 2)))
            vel_ax.set_xlim((min(t_seq[:]), max(t_seq[:])))
            t_seq_quat = t_seq[:shape_orient[0]]
            quat_line1.set_data(t_seq_quat, pltevnt.orient_w)
            quat_line2.set_data(t_seq_quat, pltevnt.orient_x)
            quat_line3.set_data(t_seq_quat, pltevnt.orient_y)
            quat_line4.set_data(t_seq_quat, pltevnt.orient_z)
            quat_ax.set_xlim((min(t_seq_quat), max(t_seq_quat)))
            fig.canvas.draw()


def plot_flex_data(nsamples=None):
    if nsamples is None:
        nsamples = 500000
    s = SensorStream(_PORT, _BAUD, do_success_check=False, conn_delay=500)
    m = GloveletFlexSensorMonitor(100)
    s.register_monitor(m)
    pltevntqueue = Queue(5)
    stream_proc = Process(target=flex_stream, args=(s, m, pltevntqueue))
    stream_proc.start()
    plt.ion()
    fig = plt.figure(figsize=(8, 10))
    flex_plt = fig.add_subplot(111)
    while pltevntqueue.empty():
        continue
    pltevnt = pltevntqueue.get()
    t_seq = pltevnt.t_elapsed
    line1, = flex_plt.plot(t_seq, pltevnt.index, 'r-', label='index')
    line2, = flex_plt.plot(t_seq, pltevnt.middle, 'g-', label='middle')
    line3, = flex_plt.plot(t_seq, pltevnt.thumb0, 'b-', label='thumb0')
    line4, = flex_plt.plot(t_seq, pltevnt.thumb1, 'y-', label='thumb1')
    plt.show()
    for i in range(nsamples):
        pltevnt = pltevntqueue.get()
        if isinstance(pltevnt, FlexPlotEvent):
            t_seq = pltevnt.t_elapsed
            line1.set_data(t_seq, pltevnt.index)
            line2.set_data(t_seq, pltevnt.middle)
            line3.set_data(t_seq, pltevnt.thumb0)
            line4.set_data(t_seq, pltevnt.thumb1)
            flex_plt.set_ylim(-0.25, 1.25)
            flex_plt.set_xlim((min(t_seq), max(t_seq)))
            fig.canvas.draw()


def main():
    # plot_flex_data()
    plot_imu_data()


if __name__ == '__main__':
    main()
