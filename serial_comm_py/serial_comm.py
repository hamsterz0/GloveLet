import serial

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

while True:
    line = arduino.readline()
    data = line.split(" ")
    print data


