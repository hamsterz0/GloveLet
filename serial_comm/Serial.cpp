
#include "Serial.h"
#include <iostream>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <unistd.h>

Serial::Serial() {
    this->fd = open("/dev/ttyACM0", O_RDWR | O_NOCTTY | O_NDELAY);
    if (this->fd == -1) {
        perror("Error opening the port.");
    } else {
        fcntl(this->fd, F_SETFL, 0);
        std::cout << "Successfully connected to the port." << std::endl;
        this->imu_check = flush_init();
        if(imu_check == 0) {
            perror("Error reading values from the IMU, check the hardware.");
        } else {
            std::cout << "Receiving values from the IMU" << std::endl;
        }
    }
}

Serial::~Serial() {
    close(this->fd);
}

int Serial::flush_init() {
    char* buffer = (char*) malloc(0x1 * sizeof(char));
    read(this->fd, buffer, 1);
    while(buffer[0] != '@' && buffer[0] != '#') {
        memset(buffer, 0, sizeof buffer);
        read(this->fd, buffer, 1);
    }
    return (buffer[0] == '@') ? 1 : 0;
}

std::string Serial::readData() {
    std::string line("");
    if(this->fd == -1 || this->imu_check == 0) {
        perror("Cannot read any data.");
        return line;
    } else {
        char* buffer = (char*) malloc(0x1 * sizeof(char));
        read(fd, buffer, 1);
        while(buffer[0] != '*') {
            line += buffer[0];
            memset(buffer, 0, sizeof buffer);
            read(this->fd, buffer, 1);
        }
    }
    return line;
}