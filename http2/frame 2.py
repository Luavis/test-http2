"""
 +-----------------------------------------------+
 |                 Length (24)                   |
 +---------------+---------------+---------------+
 |   Type (8)    |   Flags (8)   |
 +-+-------------+---------------+-------------------------------+
 |R|                 Stream Identifier (31)                      |
 +=+=============================================================+
 |                   Frame Payload (0...)                      ...
 +---------------------------------------------------------------+

 Length is minimum size = 2^14
 Length is maximum size = 2^24 - 1
"""


class Frame(object):

    FRAME_MIN_SIZE = 16384  # 2 ^ 14
    FRAME_MAX_SIZE = 16777215  # 2 ^ 24 - 1

    def __init__(self, type=0, flag=0, id=0, data=''):

        self._type = type
        self._flag = flag
        self._id_bin = id

        if len(data) > Frame.FRAME_MAX_SIZE:
            raise Exception('Data is out of size')

        self._data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if len(value) > Frame.FRAME_MAX_SIZE or \
                len(value) < Frame.FRAME_MIN_SIZE:
            raise Exception('Data size is invalid size')
        else:
            self._data = value

    @property
    def type(self):
        return self._type

    @data.setter
    def type(self, value):
        if value > 0xFF:
            raise Exception('Type is out of size')
        else:
            self._type = value

    @property
    def flag(self):
        return self._flag

    @data.setter
    def flag(self, value):
        if value > 0xFF:
            raise Exception('Flag is out of size')
        else:
            self._flag = value

    @property
    def id(self):
        return self._id_bin

    @data.setter
    def id(self, value):
        if value > 0xFFFFFFFF or not(value & 0x7FFFFFFF == value):
            raise Exception('ID is invalid')
        else:
            self._id_bin = value

    def get_frame_bin(self):

        ret_bin = bytearray()

        # append length field
        self._append_length_bin(ret_bin)

        # append type field
        self._append_type_bin(ret_bin)

        # append flag field
        self._append_flag_bin(ret_bin)

        # append stream identification field
        self._append_id_bin(ret_bin)

        # append payload data
        for d in self._data:
            ret_bin.append(d)

        return ret_bin

    def _append_length_bin(self, ret_bin):

        len_bin = len(self.data)

        if len_bin < Frame.FRAME_MIN_SIZE:
            raise Exception("Data size is invalid size")

        ret_bin.append((len_bin & 0xFF0000) >> 16)

        ret_bin.append((len_bin & 0x00FF00) >> 8)

        ret_bin.append((len_bin & 0x0000FF) >> 0)

    def _append_type_bin(self, ret_bin):

        type_bin = self._type

        ret_bin.append(type_bin & 0xFF)

    def _append_flag_bin(self, ret_bin):

        flag_bin = self._flag

        ret_bin.append(flag_bin & 0xFF)

    def _append_id_bin(self, ret_bin):

        id_bin = 0x7FFFFFFF & self._id_bin

        ret_bin.append((id_bin & 0xFF000000) >> 24)

        ret_bin.append((id_bin & 0x00FF0000) >> 16)

        ret_bin.append((id_bin & 0x0000FF00) >> 8)

        ret_bin.append((id_bin & 0x000000FF) >> 0)
