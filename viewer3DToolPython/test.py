import time
import numpy as np
import glm
import serial
import atexit
from timeseries import DataTimeSeries
from ctypes import c_float
from viewer3d_utility import convert_raw_data


np.set_printoptions(precision=4)

data_sample = [
    [-12,   140, 16432,  -508,    77,  -239],
    [-240,   224, 16480,  -554,    21,  -214],
    [-676,  -104, 16140,  -511,   -35,  -232],
    [-368,   -20, 16356,  -498,    64,  -231],
    [-112,   276, 16384,  -524,    19,  -190],
    [-632,   -48, 16024,  -527,   -41,  -227],
    [-456,   -80, 16160,  -517,    28,  -249],
    [32,   276, 16344,  -550,    83,  -181],
    [-416,     0, 16000,  -544,   -46,  -227],
    [-324,   -48, 16280,  -503,    10,  -262],
    [-100,    64, 16468,  -549,   101,  -218],
    [-316,   212, 16252,  -528,   -11,  -209],
    [-648,   -40, 16032,  -511,     0,  -264],
    [16,   196, 16332,  -522,    64,  -209],
    [-104,   196, 16432,  -563,    29,  -205],
    [-624,   -48, 15988,  -514,   -63,  -273],
    [-328,    -8, 16300,  -487,    59,  -251],
    [-180,   256, 16444,  -539,    51,  -207],
    [-548,   -44, 16036,  -512,   -56,  -238],
    [-348,   -88, 16192,  -516,    36,  -243],
    [-68,   152, 16380,  -547,    93,  -219],
    [-372,   112, 16308,  -561,   -25,  -229],
    [-528,  -128, 16152,  -487,     8,  -258],
    [-112,   180, 16332,  -535,    81,  -223],
    [-220,   124, 16352,  -545,     3,  -211],
    [-560,  -148, 16056,  -536,   -14,  -260],
    [-56,   124, 16340,  -515,   101,  -223],
    [-352,   144, 16272,  -540,    10,  -202],
    [-608,  -128, 16180,  -496,   -51,  -238],
    [-244,    60, 16316,  -533,    52,  -234],
    [-44,   168, 16420,  -525,    47,  -229],
    [-528,   -24, 16172,  -509,   -32,  -221],
    [-428,  -100, 16036,  -509,    23,  -258],
    [16,   244, 16388,  -552,    64,  -202]
]

_ACC_VZEROG = np.array([1.09375, 1.09375, 1.09375], c_float)
_ACC_SENSITIVITY = 16384  # 16384, 8192, 4096, 2048
_GYR_VRO = np.array([0.2, 0.2, 4.0], c_float)
_GYR_SENSITIVITY = 131

_SERIAL = None
try:
    _SERIAL = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    _CONNECTED = False
except Exception as e:
    print(e)

D = np.array(data_sample, int)
dts = None


def close_port():
    if _SERIAL.isOpen():
        _SERIAL.close()


atexit.register(close_port)


def init_dts(N=20, n=len(data_sample)):
    global dts
    dts = DataTimeSeries(N, D.shape[1], auto_filter=True, post_filter=convert_raw_data)
    for i in range(n):
        dts.add(D[i])
        time.sleep(0.010)
    print(dts)
    return dts


dts = init_dts()


def clear():
    print('\n' * 100)


def serial_dts(exp_factor=1.0):
    global _SERIAL, _CONNECTED
    N = 50
    dts = DataTimeSeries(N, 6, factor=exp_factor, auto_filter=True, post_filter=convert_raw_data)
    while not _CONNECTED:
        data = read_data()
        if len(data) == 3 and data[2] == 'successful@':
            _CONNECTED = True
            break
    for i in range(N):
        data = read_data()
        if len(data) == 6:
            dts.add(data)
            dts.print_data()
    while True:
        data = read_data()
        if len(data) == 6:
            dts.add(data)
            dts.print_data()


def read_data():
    global _SERIAL
    success = False
    while not success:
        try:
            line = _SERIAL.readline().decode('ascii')
            success = True
        except UnicodeDecodeError as e:
            print(e)
    data = line.strip().split(" ")
    if len(data) == 6:
        data = np.array(data, c_float)
    return data


def clamp(a, mn, mx):
    return (a - mn) / (mx - mn)


if __name__ == '__main__':
    init_dts()
    serial_dts()
