/*
 * @author: Arnav Garg
 * @date: December 15, 2017
 */
#include <iostream>
#include "Serial.h"

int main() {
    Serial ser;
    std::string line("");
    while(true) {
        line = ser.read_data();
        if (line.size() < 1) {
            break;
        } else {
            std::cout << ser.read_data() << std::endl;
        }
    }
}