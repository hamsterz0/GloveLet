//
// Created by joseph on 1/13/18.
//

#ifndef CSTDDEF_H
#include <cstddef>
#endif //CSTDDEF_H

#ifndef DataTimeSeries_H
#define DataTimeSeries_H

template<class T, size_t SIZE=20>
class DataTimeSeries {
private:
    size_t sz, head = 0, tail = 1;
    float w;
    /// pre-calculated exponential weights used in EWMA filter
    float expWeights[SIZE];
    /// denominator in EWMA filter formula, pre-calculated at DataTimeSeries instantiation
    float denom;
    T dataSeries[SIZE];
public:
    DataTimeSeries(unsigned short N = 50);
    void add(T data);
    T calcEWMA();
    T getValueAtHead();
};

/**
 * Supports arithmetic types that have defined operations for addition, multiplication, and division.
 * @param N - *optional* Used to determine weight used in EWMA filter. Must be unsigned short, 2 or greater.
 */
template<typename T, size_t SIZE>
DataTimeSeries<T, SIZE>::DataTimeSeries(unsigned short N) {
    sz = SIZE;
    w = 2.0f / ((float)N+1.0f);
    denom = 0.0f;
    for(int i = 0; i < sz; i++) {
        expWeights[i] = (float)pow((double)w, i);
        denom += expWeights[i];
    }
}
/**
 * Simultaneously adds the specified data to the series and removes the oldest element.
 * @param data
 */
template<typename T, size_t SIZE>
void DataTimeSeries<T, SIZE>::add(T data) {
//    std::cout << "head before = " << head; // FIXME DEBUGGING, remove later
    if(++head >= sz) head = 0;
    dataSeries[head] = data;
//    std::cout << ", head after = " << head << std::endl; // FIXME DEBUGGING, remove later
}

template<typename T, size_t SIZE>
T DataTimeSeries<T, SIZE>::calcEWMA() {
    /// instantiate a zeroed value of the template value.
    T result = T();
    for(int i = 0, it = (int)head; i < sz; i++, it--) {
        if(it < 0) it = (int)sz - 1;
        result += (expWeights[i] * dataSeries[it]);
    }
    return (result / denom);
}

template<typename T, size_t SIZE>
T DataTimeSeries<T, SIZE>::getValueAtHead() {
    return dataSeries[head];
}

#endif //DataTimeSeries_H
