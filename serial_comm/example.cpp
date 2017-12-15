#include <iostream>
#include "Serial.h"

int main() {
    Serial ser;
    while(true) {
        std::cout << ser.readData() << std::endl;
    }
}