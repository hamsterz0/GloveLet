/*
 * @author: Arnav Garg
 * @date: December 15, 2017
 */
#include <string>

class Serial {
public:
    Serial();
    ~Serial();
    std::string readData();

private:
    int fd;
    int imu_check = 0;
    int flush_init();
};