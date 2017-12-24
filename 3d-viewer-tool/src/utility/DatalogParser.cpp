//
// Created by joseph on 10/20/17.
//

#include <iostream>
#include <fstream>
#include <regex>
#include "DatalogParser.h"

/*!
 * Parses IMU data log files with the file extension '.log1'.
 * @param file_path
 * @return \c data_set - Each row will store the data of the gyroscope,
        accelerometer, \& magnetometer in the form:
        \code{.unparsed}
        GyroR, GyroP, GyroY, AccX, AccY, AccZ, MagX, MagY, MagZ
        \endcode
 */
std::vector<std::vector<float>> DatalogParserLog1::parse(std::string file_path) {
    std::vector<std::vector<float>> data;
    std::string str;
    const std::regex data_line_expr("^\\s*\\-?\\d+.*"); // starts with integer
    const std::regex integer("-?\\d+");

    std::ifstream input;
    input.open(file_path);

    if(input.good()) {
        std::smatch data_line;
        while(!input.eof()) {
            getline(input, str);
            if(str.back() == '\n' || str.back() == '\r')
                str.pop_back();
            if(regex_match(str, data_line_expr)) {
                std::vector<float> m = get_data_line(str);
                std::vector<float> d(9);
                // Accelerometer
                d[0] = m[4]; // AccX
                d[1] = m[5]; // AccY
                d[2] = m[6]; // AccZ
                // Gyroscope
                d[3] = m[7]; // Gyro Pitch
                d[4] = m[8]; // Gyro Roll
                d[5] = m[9]; // Gyro Yaw
                // Magnetometer
                d[6] = m[1]; // MagX
                d[7] = m[2]; // MagY
                d[8] = m[3]; // MagZ

                data.push_back(d);
            }
        }
    } else std::cerr << "Error when parsing from file \'" << file_path << "\'." << std::endl;

    input.close();
    return data;
}

std::vector<float> DatalogParser::get_data_line(std::string line) {
    const std::regex integer("-?\\d+");
    std::sregex_iterator it(line.begin(), line.end(), integer);
    std::sregex_iterator end;
    std::vector<float> list;

    for(it; it != end; it++) {
        float f = std::stof(it->str());
        list.push_back(f);
    }

    return list;
}

