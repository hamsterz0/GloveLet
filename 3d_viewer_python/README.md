# Hardware Code

Python version: 3.5.2

## Setup

Setup a virtualenv
```
$ virtualenv -p python3 env
$ source env/bin/activate
```

Install the required packages
```
$ pip install requirements.txt
```
**NOTE**: Make sure pip is alias to pip3 and not pip2, otherwise, the packages would be installed for Python2 and won't work for Python3.

Run the code (_Make sure you have the Arduino connected to the computer_):
```
python main.py
```

## Serial Read Permission Denied Error
If you are getting permission denied error to read the serial port, the best way to get around that is to add yourself to serial ports usergroup (which is dialout).
```
$ sudo usermod -a -G dialout $USER
```
**Restart the computer for the changes to take effect**

## Optional: Setup Arduino code
If you want to change and upload a new script to the arduino, the steps are:
1. Download the Arduino IDE
2. Go into the source folder for the IDE and look for a folder named **libraries**
3. Add the **I2Cdev** and **MPU6050** folders in there.
4. Once done that, open the IDE and go the tools option in the menu bar.
5. Select the board (In my case "Arduino/Genuino Uno")
6. Select the port "/dev/ttyACM0"
7. Go to files->Examples->MPU6050->Examples->MPU6050_raw
8. Make the changes here and then click the upload button (->).
9. Open the Serial Monitor and set the baud rate to 38400 (**IMP**)

