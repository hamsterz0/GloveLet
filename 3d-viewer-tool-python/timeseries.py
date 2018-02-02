import time
import numpy as np
from ctypes import c_float


class DataTimeSeries:
    def __init__(self, dimensions=1, N=50, factor=1.0,
                 auto_filter=False, filter_alg='ewma', pre_filter=None, post_filter=None):
        self._size = N
        self._dimensions = dimensions
        self.shape = (N, dimensions)
        self._factor = factor
        self._added = 0
        self._exp_weights = np.zeros((N), c_float)
        self._weight = 1 - (2.0 / (N + 1))
        self._head = 0
        self._denom = 0.0
        self._tdelta = np.zeros(N)
        self._time = None
        # bind initial function for adding data to the series
        self.add = self._initial_time_add
        self._raw_data = np.zeros((N, dimensions), c_float)
        # initialize data series
        self.data_series = self._raw_data   # use raw data if not auto-filtered.
        self.compute_exponential_weights()
        self._filtered_data = None
        if auto_filter:
            self._filtered_data = np.zeros(self.data_series.shape, c_float)
            self.data_series = self._filtered_data  # use filtered data if auto-filtered.
        # bind auto-filter function
        self._filter = self.calc_ewma
        if filter_alg == 'sma':
            self._filter = self.sma
        # bind pre-filter and post-filter callback
        self.pre_filter = pre_filter
        self.post_filter = post_filter

    def compute_exponential_weights(self):
        for i in range(self._size):
            self._exp_weights[i] = self._weight**(i * self._factor)
            self._denom += self._exp_weights[i]

    def _initial_time_add(self, data):
        self._added = 1
        # bind next function for adding data to series until series is fully initialized
        self.add = self._initial_series_add
        self._raw_data[self._head, :] = data
        if self._filtered_data is not None:
            self._filter_data
        self._time = time.time()

    def _initial_series_add(self, data):
        """
        Repeats everytime 'add' is called until the data series has
        been completely initialized/filled with data.
        """
        if self._added < self._dimensions:
            self._added += 1
        else:
            # rebind once series had bee initialized/filled with data
            self.add = self._add
        self._add(data)

    def _add(self, data):
        self._increment_head()
        self._tdelta[self._head] = time.time() - self._time
        self._raw_data[self._head, :] = data
        if self._filtered_data is not None:
            self._filter_data()
        self._time = time.time()

    def _filter_data(self):
        self.data_series = self._raw_data
        if callable(self.pre_filter):
            # pre-filter callable must take DataTimeSeries and return single data record.
            self._filtered_data[self._head, :] = self.pre_filter(self)
        self._filtered_data[self._head, :] = self._filter()
        self.data_series = self._filtered_data
        if callable(self.post_filter):
            # post-filter callable must take DataTimeSeries and return single data record.
            self._filtered_data[self._head, :] = self.post_filter(self)

    def _increment_head(self):
        self._head += 1
        if self._head >= self._size:
            self._head = 0

    def _get_previous_index(self, count=1):
        prev = self._head
        if count >= self._added:
            count = self._added - 1
        prev -= count
        if prev < 0:
            prev += self._size
        return prev

    def get_tdelta(self):
        return self._tdelta[self._head]

    def get_data(self):
        return self.data_series[self._head]

    def get_previous_data(self, count=1, get_tdelta=False):
        prev = self._get_previous_index(count)
        if not get_tdelta:
            return self.data_series[prev, :]
        else:
            return self.data_series[prev, :], self._tdelta[prev]

    def calc_ewma(self):
        result = np.zeros((self._dimensions), c_float)
        it = self._head
        for i in range(self._added):
            if it < 0:
                it = self._size - 1
            result += (self._exp_weights[i] * self.data_series[i, :])
        return result / self._denom

    def calc_sma(self):
        result = np.zeros((self._dimensions), c_float)
        it = self._head
        for i in range(self._added):
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
