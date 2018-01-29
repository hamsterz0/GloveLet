import numpy as np
from ctypes import c_float


class DataTimeSeries:
    def __init__(self, size=20, dimensions=1, N=50, factor=1.0, dtype=c_float):
        self._size = size
        self._dimensions = dimensions
        self._factor = factor
        self._dtype = dtype
        self._exp_weights = np.zeros((size), c_float)
        self._weight = 2.0 / (N + 1)
        self._head = 0
        self._denom = 0.0
        self.data_series = np.zeros((size, dimensions), dtype)
        self.compute_exponential_weights()

    def compute_exponential_weights(self):
        for i in range(self._size):
            self._exp_weights[i] = self._weight**(i * self._factor)
            self._denom += self._exp_weights[i]

    def add(self, data):
        self._head += 1
        if self._head >= self._size:
            self._head = 0
        self.data_series[self._head, :] = data

    def calc_ewma(self):
        result = np.zeros((self._dimensions), self._dtype)
        it = self._head
        for i in range(self._size):
            if it < 0:
                it = self._size - 1
            result += (self._exp_weights[i] * self.data_series[i, :])
        return result / self._denom

    def calc_sma(self):
        result = np.zeros((self._dimensions), self._dtype)
        it = self._head
        for i in range(self._size):
            if it < 0:
                it = self._size - 1
            result += self.data_series[i, :]
        return result / self._denom
