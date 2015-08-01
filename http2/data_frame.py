"""
    +---------------+
    |Pad Length? (8)|
    +---------------+-----------------------------------------------+
    |                            Data (*)                         ...
    +---------------------------------------------------------------+
    |                           Padding (*)                       ...
    +---------------------------------------------------------------+

"""

from http2.frame import (Frame, FrameType)


class DataFrame(Frame):

    PAD_MAX_LENGTH = 255

    # HEADERS frame flags

    END_STREAM_FLAG = 0x1

    PADDED_FLAG = 0x8

    def __init__(self, id, end_stream=False):

        self.is_end_header = end_stream

        self._is_padded = False

        Frame.__init__(self, type=FrameType.DATA, flag=0x0, id=id)

    def get_frame_bin(self):

        headers_frame_field = bytearray()

        if self._data is None:
            self._data = bytearray()  # check for safe

        self._flag = self.flag  # get flag by method

        if self._is_padded:

            headers_frame_field.append(self._pad_len)  # append pad length

            self._data += bytearray(self._pad_len)  # append pad byte in pad length

        self._data = headers_frame_field + self._data  # append HEADERS field

        return Frame.get_frame_bin(self)

    @property
    def flag(self):
        flag = 0x0

        if self.is_end_stream:
            flag |= DataFrame.END_STREAM_FLAG

        if self.is_padded:
            flag |= DataFrame.PADDED_FLAG

        return flag

    def padding(self, pad_len):

        if pad_len > DataFrame.PAD_MAX_LENGTH:  # padding length error
            raise ValueError("pad_len is greater then pad max length")

        self._flag |= DataFrame.PADDED_FLAG  # flag padded
        self._is_padded = True
        self._pad_len = pad_len
