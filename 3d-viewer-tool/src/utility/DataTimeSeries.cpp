//
// Created by joseph on 1/13/18.
//

#include <iostream>
#include <tgmath.h>
#include "DataTimeSeries.h"

//
///**
// * Supports arithmetic types that have defined operations for addition, multiplication, and division.
// * @param N - *optional* Used to determine weight used in EWMA filter. Must be unsigned short, 2 or greater.
// */
//template<typename T, size_t SIZE=20>
//DataTimeSeries::DataTimeSeries(unsigned short N) : {
//    sz = SIZE;
//    w = 2.0f / ((float)N+1.0f);denom = 0;
//    for(int i = 0; i < sz; i++) {
//        expWeights[i] = (float)pow((double)w, i);
//        denom += expWeights[i];
//    }
//}
///**
// * Simultaneously adds the specified data to the series and removes the oldest element.
// * @param data
// */
//template<typename T>
//void DataTimeSeries::add(T data) {
//    std::cout << "head before = " << head;
//    if(++head >= sz) head = 0;
//    dataSeries[head] = data;
//    std::cout << ", head after = " << head;
//}
//
//T DataTimeSeries::calcEWMA() {
//    /// instantiate a zeroed value of the template value.
//    auto result = dataSeries[head] * 0;
//    for(int i = 0, it = (int)head; i < sz; i++, it--) {
//        if(it < 0) it = (int)sz - 1;
//        result += (expWeights[i] * dataSeries[it]);
//    }
//    return (result / denom);
//}
//
//T DataTimeSeries::getValueAtHead() {
//    return dataSeries[head];
//}
