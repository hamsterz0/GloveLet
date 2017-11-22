//
// Created by joseph on 10/20/17.
//

#ifndef STD_VECTOR_H
#define STD_VECTOR_H
#include <vector>
#endif // STD_VECTOR_H

#ifndef DATALOG_PARSER_H
#define DATALOG_PARSER_H

enum LogType {LOG1, LOG2};

class DatalogParser {
protected:
    virtual std::vector<float> get_data_line(std::string line);
public:
    virtual std::vector<std::vector<float>> parse(std::string file_path)=0;
};

class DatalogParserLog1 : public DatalogParser {
public:
    std::vector<std::vector<float>> parse(std::string file_path);
};

#endif //DATALOG_PARSER_H
