//
// Created by joseph on 10/20/17.
//
#pragma once

#include <iostream>
#include <regex>
#include "DatalogReader.h"


DatalogReader::~DatalogReader() {
    delete parser;
}

DatalogReader::DatalogReader(std::string filePath) {
    const std::regex extension_pattern("\\.\\w+$");
    std::smatch sm;

    this->filePath = filePath;

    std::regex_search(filePath,sm,extension_pattern);
    std::string extension = sm.str();

    LogType logType = determine_log_type();
    switch (logType) {
        case LOG1:
            parser = new DatalogParserLog1();
            break;
        case LOG2:
            std::cerr << "Datalog file extension \'.log2\' not supported yet." << std::endl;
            break;
        default:
            std::cerr << "Unsupported file extension \'" << extension << "\' not supported." << std::endl;
            break;
    }
}

/*!
 * \brief Determines the correct datalog file parsing method.
 * @param file_path - <code>string</code>
 * @return \code enum log_type \endcode
 */
LogType DatalogReader::determine_log_type() {
    const std::regex extension_pattern("\\.\\w+$");
    std::smatch sm;
    LogType log;

    std::regex_search(filePath,sm,extension_pattern);
    std::string extension = sm.str();

    if(!extension.compare(".log1")) log = LOG1;
    else if(!extension.compare(".log2")) log = LOG2;
    else return LOG1;

    return log;
}

std::vector<std::vector<float>> DatalogReader::get_data() {
    return parser->parse(filePath);
}
