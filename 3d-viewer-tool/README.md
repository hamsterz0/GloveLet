# IMU Data 3D Viewer Utility

A simple 3D model viewer to be used for visualizing data captured by the Glovelet's sensors.

## Getting Started

In console:
```
git clone https://bitbucket.org/piedpiperuta/imu-tracking
git fetch
git checkout 3d-viewer-tool
```
### Prerequisites & Dependencies

For building:<br>
- [CMake 3.6.x or higher](https://cmake.org/download/)

Libraries:<br>
- [FreeGLUT - OpenGL Utility](https://sourceforge.net/projects/freeglut/)
- [GLM - OpenGL Mathematics](https://github.com/g-truc/glm/tags) 

##### Installing the dependencies on Linux (*tested only for Ubuntu 16.04*):
```
sudo apt-get install freeglut3-dev libglm-dev cmake
```
##### Installing the dependencies on Windows (*tested only for Windows 10*):
*No instructions for Windows yet...*

### Building

In a terminal or command line tool, change to 3d-viewer-tool directory:
```
cmake CMakeLists.txt
make
```
This will build and compile the `3d-viewer-utility`, `datalog-file-converter`, & `opengl-debugger` object files.

## Object Files

### 3d-viewer-utility
##### Description
This utility program takes 9-DoF IMU data as input and displays a rectangular prism as the 3D model analog for the IMU. IMU sensor data should roughly translate to motion of the 3D object being displayed.
##### Use
Run the program via a command line or terminal. Use the `-h` or `--help` option to view program options. Input file piping is supported, however data should be of the format:
```
<Gyro Pitch>  <Gyro Roll>  <Gyro Yaw>  <Acc X>  <Acc Y>  <Acc Z>  <Mag X>  <Mag Y>  <Mag Z>
```
Where Gyro is the gyroscope, Acc is accelerometer, and Mag is magnitometer. Spaces will be ignored. If data is not in this format, unexpected results may occur.
### datalog-file-converter
##### Description
A program meant to convert recorded IMU datalog files. So far only supports one format type of datalog file.
##### Use
Run the program via a command line or terminal. An input file path and output file path (in strict order) are required arguments.
```
./datalog-file-converter <input path> <output path> 
```
### opengl-debugger
##### Description
This program is only for debugging OpenGL rendering logic and demonstration purposes.
##### Use
Run the program via a command line or terminal. Does not take any arguments.
```
./opengl-debugger
```
