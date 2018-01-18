/*!
 * @author: Arnav Garg
 * @date: December 15, 2017
 */
#include <iostream>
#include "src/utility/Serial.h"

int main() {
    Serial ser;
    std::string line("");
    while(true) {
        line = ser.read_data();
        if (line.empty()) {
            break;
        } else {
            std::cout << line << std::endl;
        }
    }
}