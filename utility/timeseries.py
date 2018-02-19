import time
import numpy as np
from ctypes import c_float


__all__ = ["DataTimeSeries"]


class DataSequence:
    """
    Base class of DataTimeSeries.\n
    Allows for sequential access of data values.
    Old values are overwritten as new values are added.
    Does not record time deltas or time stamps.
    """

    def __init__(self, samples, dimensions):
        self.__nsamples = samples
        self.__ndim = dimensions
        self.__shape = (samples, dimensions)
        self.__added = 0
        self.__head = 0
        # initialize data series
        self.data_series = np.zeros((samples, dimensions), c_float)

    @property
    def nsamples(self):
        return self.__nsamples

    @property
    def ndim(self):
        return self.__ndim

    @property
    def shape(self):
        return self.__shape

    @property
    def head(self):
        return self.__head

    @property
    def added(self):
        return self.__added

    def add(self, data):
        """
        Add a data sample to the time series.\n
        If the time series is filled, the oldest value in the time series is overwritten.\t
        :param data:    The data. Must be of length `ndim` dimensions. Can be any iterable.
        """
        self._increment_added()
        self._increment_head()
        self.data_series[self.__head, :] = data

    def print_data(self, index=0):
        """
        Prints a data sample and associated time delta.\n
        By default, the most recent data sample is printed.\t
        Otherwise, specifiy the index of the data sample to print.\t
        :param index: The index of the data to convert to string. The most recent data sample is selected by default.
        """
        index = self._get_real_index(index)
        out = self.data2str(index)
        print(out + '  :  dt=' + str(self.__tdelta[index]))

    def data2str(self, index=0):
        """
        Returns a data sample as a string.

        By default, the most recent data sample is returned as a string.
        Otherwise, specifiy the index of the data sample to return.
        \t
        \tindex:    The index of the data to convert to string.
        \t          The most recent data sample is selected by default.
        """
        return np.array2string(self.data_series[index], precision=4)

    def _increment_head(self):
        self.__head += 1
        if self.__head >= self.__nsamples:
            self.__head = 0

    def _increment_added(self):
        if self.added < self.nsamples:
            self.__added += 1

    def _get_real_index(self, from_head):
        # FIXME: wrong index is being returned
        result = self.__head - from_head
        if result < 0:
            result += self.__added
        return result

    def __extract_range(self, start=-1, stop=-1, step=1):
        step = -step
        size = stop - start
        if stop >= self.__added:
            size = self.__added
        result = np.zeros((size, self.__ndim), c_float)
        start_ind = self._get_real_index(start)
        end_ind = self._get_real_index(stop)
        if end_ind >= start_ind:
            n = start_ind + 1
            result[:n] = self.data_series[start_ind::step]
            result[n:] = self.data_series[self.__added:end_ind:step]
        else:
            print(len(result))
            result[:] = self.data_series[start_ind:end_ind:step]
        return result

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            if step is None or step != 1:  # TODO: Implement support for 'step' slice argument
                step = 1
            if start is None:
                start = 0
            if stop is None:
                stop = self.__added
            return self.__extract_range(start, stop, step)
        else:
            i = self._get_real_index(key)
            return self.data_series[i]

    def __str__(self):
        output = list()
        for i in range(self.nsamples):
            output.append(str(self[i]))
        output = '\n'.join(output)
        return output


class DataTimeSeries(DataSequence):
    def __init__(self, nsamples, ndim,  factor=1.0,
                 auto_filter=False, filter_alg='ewma',
                 pre_filter=None, post_filter=None):
        super().__init__(nsamples, ndim)
        self.__factor = factor
        self.__exp_weights = np.zeros((nsamples), c_float)
        self.__weight = 0.0
        self.__denom = 0.0
        self.tdelta = DataSequence(nsamples, 1)
        self.timestamp = DataSequence(nsamples, 1)
        # bind initial function for adding data to the series
        self.add = self.__initial_time_add
        self.__raw_data = np.zeros((nsamples, ndim), c_float)
        # initialize data series
        self.data_series = self.__raw_data   # use raw data if not auto-filtered.
        self.__filtered_data = None
        if auto_filter:
            self.__filtered_data = np.zeros(self.shape, c_float)
            self.data_series = self.__filtered_data  # use filtered data if auto-filtered.
        # bind auto-filter function
        self.__filter = self.calc_ewma
        if filter_alg == 'sma':
            self.__filter = self.sma
        # bind pre-filter and post-filter callback
        self.pre_filter = pre_filter
        self.post_filter = post_filter

    def add(self, data):
        """
        Add a data sample to the time series.\n
        If the time series is filled, the oldest value in the time series is overwritten.\t
        :param data:    The data. Must be of length `ndim` dimensions. Can be any iterable.
        """
        # NOTE: `add` is rebound at DataTimeSeries object creation
        pass

    def get_tdelta(self, index=0):
        """
        Returns the most recent time delta.
        """
        tdelta = self.tdelta[index][0]
        return tdelta

    def calc_ewma(self):
        """
        Calculate the Exponential Weighted Moving Average
        over the initialized values of the data series and return the result.
        """
        result = np.zeros((self.ndim), c_float)
        it = self.head
        for i in range(self.nsamples):
            if it < 0:
                it = self.nsamples - 1
            result += (self.__exp_weights[it] * self.data_series[it, :])
            it -= 1
        return result / self.__denom

    def calc_sma(self):
        """
        Calculate the Simple Moving Average over the
        initialized values of the data series and return the result.
        """
        result = np.zeros(self.ndim, c_float)
        it = self.head
        for i in range(self.added):
            if it < 0:
                it = self.added - 1
            result += self.data_series[it, :]
            it -= 1
        return result / self.added

    def print_data(self, index=0):
        """
        Prints a data sample and associated time delta.\n
        By default, the most recent data sample is printed.\t
        Otherwise, specifiy the index of the data sample to print.\t
        :param index: The index of the data to convert to string. The most recent data sample is selected by default.
        """
        index = self._get_real_index(index)
        out = self.data2str(index)
        print(out + '  :  dt=' + str(self.__tdelta[index]))

    def data2str(self, index=-1):
        """
        Returns a data sample as a string.

        By default, the most recent data sample is returned as a string.
        Otherwise, specifiy the index of the data sample to return.
        \t
        \tindex:    The index of the data to convert to string.
        \t          The most recent data sample is selected by default.
        """
        index = self._get_real_index(index)
        return np.array2string(self.data_series[index], precision=4)

    def __compute_exponential_weights(self):
        self.__weight = 1 - (2.0 / (self.added + 1))
        self.__denom = 0.0
        for i in range(self.added):
            self.__exp_weights[i] = self.__weight**(i * self.__factor)
            self.__denom += self.__exp_weights[i]

    def __initial_time_add(self, data, timestamp=None):
        # bind next function for adding data to series until series is fully initialized
        self.add = self.__initial_series_add
        self.data_series = self.__raw_data
        super().add(data)
        if self.__filtered_data is not None:
            self.__compute_exponential_weights()
            self.__filter_data()
            self.data_series = self.__filtered_data
        if timestamp is None:
            timestamp = time.time()
        self.timestamp.add(timestamp)

    def __initial_series_add(self, data, timestamp=None):
        """
        Repeats everytime 'add' is called until the data series has been completely initialized/filled with data.
        """
        if self.added >= self.nsamples:
            # rebind once series had bee initialized/filled with data
            self.add = self.__add
        if self.__filtered_data is not None:
            # weights for EWMA must be recomputed each time __added is incremented
            self.__compute_exponential_weights()
        self.__add(data)

    def __add(self, data, timestamp=None):
        """The optimised version of the `add` function."""
        self.data_series = self.__raw_data
        super().add(data)
        if timestamp is None:
            timestamp = time.time()
        self.tdelta.add(timestamp - self.timestamp[0][0])
        if self.__filtered_data is not None:
            self.__filter_data()
            self.data_series = self.__filtered_data
        self.timestamp.add(timestamp)

    def __filter_data(self):
        self.data_series = self.__raw_data
        if callable(self.pre_filter):
            # pre-filter callable must take DataTimeSeries and return single data record.
            self.__filtered_data[self.head, :] = self.pre_filter(self)
        self.__filtered_data[self.head, :] = self.__filter()
        if callable(self.post_filter):
            # post-filter callable must take DataTimeSeries and return single data record.
            self.__filtered_data[self.head, :] = self.post_filter(self)

    def __str__(self):
        output = list()
        for i in range(self.nsamples):
            output.append(str(self[i]) + '  :  dt=' + str(self.__tdelta[i]))
        output = '\n'.join(output)
        return output
