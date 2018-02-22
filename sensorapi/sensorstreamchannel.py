__all__ = ['SensorStreamDataChannel']


class SensorStreamDataChannel:
    def __init__(self, name, ch_range):
        if not isinstance(ch_range, tuple) or len(ch_range) != 2:
            raise TypeError('Expected tuple of length 2 for argument \'ch_range\'.')
        self.__name = name
        self.__ch_range = range(*ch_range)

    def get_name(self):
        """
        Get channel name.\n
        This is the channel name.
        """
        return self.__name

    def get_range(self):
        return self.__ch_range

    def get_start(self):
        return self.__ch_range.start

    def get_stop(self):
        return self.__ch_range.stop

    def get_width(self):
        """
        Get channel width.\n
        This is the number of data features this channel monitors.\t
        :returns: `int`
        """
        return len(self.__ch_range)

    def set_range(self, ch_range):
        if not isinstance(ch_range, tuple) or len(ch_range) != 2:
            raise TypeError('Expected tuple of length 2 for argument \'ch_range\'.')
        self.__ch_range = range(*ch_range)
