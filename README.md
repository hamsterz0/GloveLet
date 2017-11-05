## Getting Started

In console:
```
git clone https://bitbucket.org/piedpiperuta/imu-tracking
git fetch
git checkout 3d-viewer-tool
```
### Prerequisites

For building:
	- cmake 3.6.x or higher

Libraries:
	- GLUT (OpenGL utility)
	- GLM (OpenGL Mathematics)

Installing the dependencies on Linux:
```
sudo apt-get install freeglut3-dev libglm-dev cmake
```

*No instructions for Windows yet...*

### Building

In a terminal or command line tool, change to 3d-viewer-tool directory:
```
cmake CMakeLists.txt
make 3d-viewer-tool.exe
```

This will build and compile the 3d-viewer-tool.exe object file.