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

