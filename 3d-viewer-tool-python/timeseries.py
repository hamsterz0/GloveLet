import time
import numpy as np
from ctypes import c_float


class DataTimeSeries:
    def __init__(self, dimensions=1, N=50,  factor=1.0,
                 auto_filter=False, filter_alg='ewma',
                 pre_filter=None, post_filter=None):
        self._size = N
        self._dimensions = dimensions
        self.shape = (N, dimensions)
        self._factor = factor
        self._added = 0
        self._exp_weights = np.zeros((N), c_float)
        self._weight = 0.0
        self._head = 0
        self._denom = 0.0
        self._tdelta = np.zeros(N)
        self._time = None
        # bind initial function for adding data to the series
        self.add = self._initial_time_add
        self._raw_data = np.zeros((N, dimensions), c_float)
        # initialize data series
        self.data_series = self._raw_data   # use raw data if not auto-filtered.
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

    def _compute_exponential_weights(self):
        self._weight = 1 - (2.0 / (self._added + 1))
        self._denom = 0.0
        for i in range(self._added):
            self._exp_weights[i] = self._weight**(i * self._factor)
            self._denom += self._exp_weights[i]

    def _initial_time_add(self, data):
        self._added = 1
        # bind next function for adding data to series until series is fully initialized
        self.add = self._initial_series_add
        self._raw_data[self._head, :] = data
        if self._filtered_data is not None:
            self._compute_exponential_weights()
            self._filter_data()
        self._time = time.time()

    def _initial_series_add(self, data):
        """
        Repeats everytime 'add' is called until the data series has
        been completely initialized/filled with data.
        """
        if self._added < self._size:
            self._added += 1
        else:
            # rebind once series had bee initialized/filled with data
            self.add = self._add
        if self._filtered_data is not None:
            # weights for EWMA must be recomputed each time _added is incremented
            self._compute_exponential_weights()
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
        result = self._head
        if count >= self._added:
            count = self._added - 1
        result -= count
        if result < 0:
            result += self._added
        return result

    def get_tdelta(self):
        """
        Returns the most recent time delta.
        """
        return self._tdelta[self._head]

    def get_data(self, index=-1):
        """
        Returns a data sample.

        By default, the most recent data sample is returned.
        Otherwise, specifiy the index of the data sample to return. If the given
        index is out of bounds, the most recent data sample is returned.
        \t
        \tindex:    The index of the data to return.
        \t          The most recent data sample is returned by default.
        """
        if index < 0 or index >= self.shape[0]:
            index = self._head
        return self.data_series[index]

    def get_previous_data(self, count=1, get_tdelta=False):
        """
        Retrieve previous data.
        \t
        \tcount:        number of samples to walk backward from head
        \tget_tdelta:   retrieve time delta of sample
        """
        prev = self._get_previous_index(count)
        if not get_tdelta:
            return self.data_series[prev, :]
        else:
            return self.data_series[prev, :], self._tdelta[prev]

    def calc_ewma(self):
        """
        Calculate the Exponential Weighted Moving Average
        over the initialized values of the data series and return the result.
        """
        result = np.zeros((self._dimensions), c_float)
        it = self._head
        for i in range(self._size):
            if it < 0:
                it = self._size - 1
            result += (self._exp_weights[it] * self.data_series[it, :])
            it -= 1
        return result / self._denom

    def calc_sma(self):
        """
        Calculate the Simple Moving Average over the
        initialized values of the data series and return the result.
        """
        result = np.zeros(self._dimensions, c_float)
        it = self._head
        for i in range(self._added):
            if it < 0:
                it = self._size - 1
            result += self.data_series[it, :]
            it -= 1
        return result / self._added

    def print_data(self, index=-1):
        """
        Prints a data sample and associated time delta.

        By default, the most recent data sample is printed.
        Otherwise, specifiy the index of the data sample to print.
        \t
        \tindex:    The index of the data to convert to string.
        \t          The most recent data sample is selected by default.
        """
        out = self.data2str(index)
        print(out + '  :  dt=' + str(self._tdelta[index]))

    def data2str(self, index=-1):
        """
        Returns a data sample as a string.

        By default, the most recent data sample is returned as a string.
        Otherwise, specifiy the index of the data sample to return.
        \t
        \tindex:    The index of the data to convert to string.
        \t          The most recent data sample is selected by default.
        """
        if index < 0 or index >= self.shape[0]:
            index = self._head
        return np.array2string(self.data_series[index], precision=4)

    def max(self, axis, start=-1, end=-1):
        """
        Returns maximum value along the specified axis.

        Returns maximum along the specified axis within the given range.
        By default, this will give the maximum over the entire time series.
        Otherwise, it will return the maximum from index 'start' to 'end',
        where 0 is the index of the oldest data, and N is the index of the
        newest data.
        """
        if axis < 0 or axis >= self._dimensions:
            raise IndexError
        if start < 0 or start >= end:
            start = 0
        if end >= self._size:
            end = self._size - 1
        start = self._get_previous_index(self._size - 1 - start)
        end = self._get_previous_index(self._size - 1 - end)

    def _extract_range(self, start=-1, stop=-1, step=1):
        step = -step
        result = np.zeros((stop - start, self._dimensions), c_float)
        start_ind = self._get_previous_index(start)
        end_ind = self._get_previous_index(stop)
        print('start:  {:d}, start_ind:  {:d}'.format(start, start_ind))
        print('stop:  {:d}, end_ind:  {:d}'.format(stop, end_ind))
        if end_ind > start_ind:
            n = start_ind
            result[:n] = self.data_series[start_ind:0:step]
            result[n:] = self.data_series[self._added:end_ind-1:step]
        else:
            result[:] = self.data_series[start_ind:end_ind:step]
        return result

    def __getitem__(self, key):
        if isinstance(key, slice):
            # TODO: Implement support for 'step' slice argument
            start, stop, step = key.start, key.stop, key.step
            if step is None:
                step = 1
            if start is None:
                start = 0
            elif start < 0:
                start += self._added
            if stop is None:
                stop = self._added
            elif stop < 0:
                stop += self._added
            return self._extract_range(start, stop, step)
        else:
            i = self._get_previous_index(key)
            return self.data_series[i]

    def __str__(self):
        output = str()
        i = self._get_previous_index(self._added)
        while i != self._head:
            output += str(self.data2str(i)) + '  :  dt=' + str(self._tdelta[i]) + '\n'
            i += 1
            if i >= self._added:
                i = 0
        output += str(self.data2str(i)) + '  :  dt=' + str(self._tdelta[i])
        return output
