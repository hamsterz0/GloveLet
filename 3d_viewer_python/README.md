# Hardware Code

Python version: 3.5.2

## Installation

```
> pip install requirements.txt
> python imu_data.py
```

## Using the output in C++

```
> python imu_data.py | ./bin
```

In the C++ code, add the following lines:

```
std::string line;

while(std::getline(std::cin, line)) {
   // process the line here.
}
```
