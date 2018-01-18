/*
 * @author: Arnav Garg
 * @date: December 15, 2017
 */
#ifndef STRING_H
#include <string>
#endif //STRING_H

#ifndef TERMIOS_H
#include <termios.h>
#endif //TERMIOS_H

class Serial {
public:
    Serial();
    ~Serial();
    std::string read_data();

private:
    struct termios port_config;
    int fd;
    int data_count;
    int imu_check = 0;
    int flush_init();
};