#!../3d-viewer-tool-python/venv/bin/python
import serial
import numpy as np
from ctypes import c_int

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

while True:
    line = arduino.readline().decode('ascii')
    data = line.strip().split(" ")
    if len(data) == 6:
        data = np.array(data, c_int)
    print(data)
