/*
 * @author: Arnav Garg
 * @date: December 15, 2017
 */
#include <iostream>
#include "Serial.h"

int main() {
    Serial ser;
    while(true) {
        std::cout << ser.readData() << std::endl;
    }
}