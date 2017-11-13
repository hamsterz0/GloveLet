//
// Created by joseph on 10/20/17.
//
#pragma once

#ifndef DATALOG_PARSER_H
#include "DatalogParser.h"
#endif

#ifndef DATALOG_READER_H
#define DATALOG_READER_H

//typedef struct invalid_datalog_extension : public std::exception {
//    const char* what() const noexcept { return "Invalid data log file extension."; }
//};

class DatalogReader {
private:
    DatalogParser* parser;
    std::string filePath;
    log_type determine_log_type();
public:
    ~DatalogReader();
    DatalogReader(std::string filePath);
    std::vector<std::vector<float>> get_data();
};

#endif //DATALOG_READER_H
