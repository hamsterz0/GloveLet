/*
 * @author: Arnav Garg
 * @date: December 15, 2017
 */
#include "Serial.h"
#include <termios.h>
#include <iostream>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <unistd.h>

Serial::Serial() {
    this->data_count = 0;
    this->fd = open("/dev/ttyACM0", O_RDWR | O_NOCTTY | O_NDELAY);
    if (this->fd == -1) {
        perror("Error opening the port.");
    } else {
        tcgetattr(fd, &port_config);
        cfsetspeed(&port_config, B115200);
        fcntl(this->fd, F_SETFL, 0);
        tcsetattr(fd, TCSAFLUSH, &port_config);
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
//    char* buffer = (char*) malloc(0x1 * sizeof(char));
    char buffer[1];
    read(this->fd, buffer, 1);
    while(buffer[0] != '@' && buffer[0] != '#') {
        memset(buffer, 0, sizeof buffer);
        read(this->fd, buffer, 1);
    }
    return (buffer[0] == '@') ? 1 : 0;
}

std::string Serial::read_data() {
    std::string line("");
    if(this->fd == -1 || this->imu_check == 0) {
        perror("Cannot read any data.");
        return line;
    } else {
        char* buffer = (char*) calloc(1, sizeof(char));
        read(fd, buffer, 1);
        while(buffer[0] != '\n') {
            line += buffer[0];
            memset(buffer, 0, sizeof buffer);
            read(this->fd, buffer, 1);
        }
        this->data_count++;
    }
    return line;
}