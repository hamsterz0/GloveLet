from glovelet.sensorapi.sensorstreamchannel import SensorStreamDataChannel

__all__ = ["Sensor"]


class Sensor:
    def __init__(self, name, ndatapoints, ch_name=None, ch_offset=0):
        """
        Basic sensor class for creating different types of sensor objects.\n
        :param name: `str` name of sensor\t
        :param ndatapoints: `int` number of data points this sensor outputs
        :param ch_name: `str` Channel name. Equals `name` if left as `None`
        """
        if ch_name is None:
            ch_name = name
        self.__name = name
        self.__ch_name = ch_name
        self.__ndatapoints = ndatapoints
        self.__ch_offset = ch_offset
        self.__channel = SensorStreamDataChannel(ch_name, (ch_offset, ch_offset + ndatapoints))

    @property
    def name(self):
        return self.__name

    @property
    def ndatapoints(self):
        return self.__ndatapoints

    @property
    def channel(self):
        return self.__channel

    @property
    def channel_offset(self):
        return self.__ch_offset

    def set_channel_offset(self, ch_offset):
        self.__ch_offset = ch_offset
        self.__channel.set_range((ch_offset, ch_offset + self.ndatapoints))
