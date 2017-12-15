# Serial Communication API

## How to use
See the example code on how to use the API.

## Error Handling
If not able to read the port. Follow the instruction below.

If you are getting permission denied error to read the serial port, the best way to get around that is to add yourself to serial ports usergroup (which is dialout).
```
$ sudo usermod -a -G dialout $USER
```