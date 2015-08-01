"""
    +---------------+
    |Pad Length? (8)|
    +-+-------------+-----------------------------------------------+
    |E|                 Stream Dependency? (31)                     |
    +-+-------------+-----------------------------------------------+
    |  Weight? (8)  |
    +-+-------------+-----------------------------------------------+
    |                   Header Block Fragment (*)                 ...
    +---------------------------------------------------------------+
    |                           Padding (*)                       ...
    +---------------------------------------------------------------+

"""

from http2.frame import (Frame, FrameType)
from http2.util import int_to_bytes
from http2.hpack.hpack import Encoder


class HeaderFrame(Frame):

    PAD_MAX_LENGTH = 255

    # HEADERS frame flags

    END_STREAM_FLAG = 0x1

    END_HEADER_FLAG = 0x4

    PADDED_FLAG = 0x8

    PRIORITY_FLAG = 0x20

    def __init__(self, id, end_header=False, end_stream=False):

        self.is_end_stream = end_header

        self.is_end_header = end_stream

        self._is_priority = False

        self._is_padded = False

        self._header_list = []  # http header list

        Frame.__init__(self, type=FrameType.HEADERS, flag=0x0, id=id, data=None)

    def get_frame_bin(self):

        # Encode header

        encoder = Encoder()

        headers_frame_field = bytearray()

        if self._data is None:  # if user didn't touch data
            self._data = encoder.encode(self._header_list)  # encode header list

        self._flag = self.flag  # get flag by method

        if self._is_padded:

            headers_frame_field.append(self._pad_len)  # append pad length

            self._data += bytearray(self._pad_len)  # append pad byte in pad length

        if self._is_priority:
            headers_frame_field += int_to_bytes(self._dependency_id)  # append dependency stream id
            headers_frame_field.append(self._weight)

        self._data = headers_frame_field + self._data  # append HEADERS field

        return Frame.get_frame_bin(self)

    def add(self, name, value):

        self._header_list.append((name.lower(), value))

    def status(self, status):
        self.add(':status', str(status))

    def method(self, method):

        self.add(':method', method)

    def scheme(self, scheme):

        self.add(':scheme', scheme)

    def authority(self, authority):

        self.add(':authority', authority)

    def path(self, path):

        self.add(':path', path)

    # Remove headers

    def remove(self, name):

        for header in self._header_list:
            if header[0] == name:
                pass

    @property
    def flag(self):
        flag = 0x0

        if self.is_end_header:
            flag |= HeaderFrame.END_HEADER_FLAG

        if self.is_end_stream:
            flag |= HeaderFrame.END_STREAM_FLAG

        if self._is_padded:
            flag |= HeaderFrame.PADDED_FLAG

        if self._is_priority:
            flag |= HeaderFrame.PRIORITY_FLAG

        return flag

    def padding(self, pad_len):

        if pad_len > HeaderFrame.PAD_MAX_LENGTH:  # padding length error
            raise ValueError("pad_len is greater then pad max length")

        self._flag |= HeaderFrame.PADDED_FLAG  # flag padded
        self._is_padded = True
        self._pad_len = pad_len

    def priority(self, dep_stream_id, weight):

        self._is_priority = True

        self._dependency_id = dep_stream_id

        self._weight = weight  # set priority weight
