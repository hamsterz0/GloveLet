# Serial Communication API

## How to use
See the example code on how to use the API.

## Error Handling
If not able to read the port. Follow the instruction below.

If you are getting permission denied error to read the serial port, the best way to get around that is to add yourself to serial ports usergroup (which is dialout).
```
$ sudo usermod -a -G dialout $USER
```

## Arduino Code (Optional)
In order to set the arduino code do that following:

1. Download the Arduino IDE
2. Go into the source folder for the IDE and look for a folder named **libraries**
3. Add the **I2Cdev** folder in there.
4. Open the ino file in the **MPU6050** folder.
5. Once done that, open the IDE and go the tools option in the menu bar.
6. Select the board (In my case "Arduino/Genuino Uno")
7. Select the port "/dev/ttyACM0"
Make the changes in the ino file and then click the upload button (->).
Open the Serial Monitor and set the baud rate to 38400 (IMP)