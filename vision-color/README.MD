# Vision Tracking API

This contains the computer vision script for tracking the hand/finger motion and translate it to the computer mouse pointer location.

**NOTE:** The code is written in Python 3.5.2

## How to run?

**Important** : This script right now is developed on a Linux machine (Linux Mint 18.3 x86_64 Linux 4.10.0-38-generic)

### Download a couple of things before we get started.

1. Xlib library for Python 
```sudo apt-get install python3-xlib```


2. Opencv3 (Steps descripted below, thanks to Stackoverflow.)
Update the repository: ```sudo apt-get update```
Download the required packages to compile OpenCV:
```
 sudo apt-get install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
```
    
Install the developer packages for Python3.5: ```sudo apt-get install python3.5-dev```
Copy the dev files:python3.5-config --includes The output should be similar to: -I/usr/include/python3.5m -I/usr/include/x86_64-linux-gnu/python3.5m. The first part of the output is the expected location & the second part shows the current location of the config file. To solve this problem, we’ll copy the file from the current location to the expected location: sudo cp /usr/include/x86_64-linux-gnu/python3.5m/pyconfig.h /usr/include/python3.5m/

Create a temporary directory, move into it and run: ```git clone https://github.com/Itseez/opencv.git``` This will download OpenCV 3. Then rename the folder opencv to opencv-3

Create a build directory, move to it and run:
```cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ../opencv-3```

 After the process is finished, run ```make``` and then ```sudo make install```.


3. Download the remaining packages from the requirements.txt file. 
```pip3 install requirements.txt```


### How does it work?

Initially when you are running it for the very first time, the program will ask you to seclude the color that you want to track. Once you do this twice (Once for each color), then it would store the settings in the .vision.conf file which would be read next time you run the code again. 

Once you set the Min and Max HSV for the first color, press 'q'. Do the same when you complete setting the HSV bounds for the next color. 

Once the colors are set, you will be able to start the tracking. 