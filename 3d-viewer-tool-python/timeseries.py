import time
import numpy as np
from ctypes import c_float


class DataTimeSeries:
    def __init__(self, dimensions=1, N=50, factor=1.0):
        self._size = N
        self._dimensions = dimensions
        self._factor = factor
        self._exp_weights = np.zeros((N), c_float)
        self._weight = 1 - (2.0 / (N + 1))
        self._head = 0
        self._denom = 0.0
        self._tdelta = np.zeros(N)
        self._time = None
        self.add = self._initial_time_add  # callback to function for initial data entry
        self.data_series = np.zeros((N, dimensions), c_float)
        self.compute_exponential_weights()

    def compute_exponential_weights(self):
        for i in range(self._size):
            self._exp_weights[i] = self._weight**(i * self._factor)
            self._denom += self._exp_weights[i]

    def _initial_time_add(self, data):
        self._time = time.time()
        self.data_series[self._head, :] = data
        self.add = self._initial_tdelta_add

    def _initial_tdelta_add(self, data):
        self._increment_head()
        self._tdelta[self._head] = time.time() - self._time
        self.data_series[self._head, :] = data
        self.add = self._add
        self._time = time.time()

    def _add(self, data):
        self._increment_head()
        self._tdelta[self._head] = time.time() - self._time
        self.data_series[self._head, :] = data
        self._time = time.time()

    def _increment_head(self):
        self._head += 1
        if self._head >= self._size:
            self._head = 0

    def calc_ewma(self):
        result = np.zeros((self._dimensions), c_float)
        it = self._head
        for i in range(self._size):
            if it < 0:
                it = self._size - 1
            result += (self._exp_weights[i] * self.data_series[i, :])
        return result / self._denom

    def calc_sma(self):
        result = np.zeros((self._dimensions), c_float)
        it = self._head
        for i in range(self._size):
            if it < 0:
                it = self._size - 1
            result += self.data_series[i, :]
        return result / self._denom

    def print_head(self):
        print(str(self.data_series[self._head])
              + '  :  dt='
              + str(self._tdelta[self._head]))

    def __str__(self):
        output = str()
        i = self._head - 1
        while i != self._head:
            output += str(self.data_series[i]) + '  :  dt=' + str(self._tdelta[i]) + '\n'
            i -= 1
            if i <= -1:
                i = self._size - 1
        output += str(self.data_series[i]) + '  :  dt=' + str(self._tdelta[i])
        return output
