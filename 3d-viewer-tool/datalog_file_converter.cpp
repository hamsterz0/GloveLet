//
// Created by joseph on 11/12/17.
//

#include <iostream>
#include <fstream>
#include "src/utility/DatalogReader.h"

using namespace std;

int main(const int argc, const char * argv[]) {
    if(argc < 3) {
        cerr << "Incorrect number of arguments." << endl;
        return 1;
    }

    string inputFile = argv[1];
    string outputFile = argv[2];

    DatalogReader reader(argv[1]);
    auto data = reader.get_data();
    ofstream writer;
    writer.open(argv[2], ios_base::trunc);
    for(auto line : data) {
        int i;
        for(i = 0; i < line.size() - 1; i++) {
            writer << (float)line[i] << " ";
        }
        writer << line[i] << endl;
    }
    writer.close();
    return 0;
}