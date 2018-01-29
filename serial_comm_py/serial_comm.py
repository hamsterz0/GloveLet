#!../3d-viewer-tool-python/venv/bin/python
import serial

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

while True:
    line = arduino.readline().decode('utf-8')
    data = line.strip().split(" ")
    print(data)
