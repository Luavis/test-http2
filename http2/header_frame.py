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
from http2.hpack.hpack import (Encoder, Decoder)


class HeaderFrame(Frame):

    PAD_MAX_LENGTH = 255

    # HEADERS frame flags

    END_STREAM_FLAG = 0x1

    END_HEADER_FLAG = 0x4

    PADDED_FLAG = 0x8

    PRIORITY_FLAG = 0x20

    @classmethod
    def load(cls, frame, header, encoded_headers=[]):

        # frame length, type, flag, id
        frm_len, frm_type, frm_flag, frm_id = header

        if frm_id is 0x0:  # protocol error
            raise ValueError("'frm_id must not be 0x0")

        if frm_type is not FrameType.HEADERS:
            raise Exception("frame is not type of HEADERS type")

        end_stream = False
        end_header = False

        header_start_index = 9  # default is payload stat index
        header_pad_length = 0

        if frm_flag & HeaderFrame.END_STREAM_FLAG is not 0:
            end_stream = True

        if frm_flag & HeaderFrame.END_HEADER_FLAG is not 0:
            end_header = True

        # create header frame to return
        header_frame = cls(frm_id, end_header, end_stream)

        if frm_flag & HeaderFrame.PADDED_FLAG is not 0:  # if it is padded
            header_pad_length = frame[header_start_index]
            header_start_index += 1  # if padded, first byte is pad length

        if frm_flag & HeaderFrame.PRIORITY_FLAG is not 0:  # if priority is set
            dep_stream_id = frame[header_start_index] << 24
            dep_stream_id += frame[header_start_index + 1] << 16
            dep_stream_id += frame[header_start_index + 2] << 8
            dep_stream_id += frame[header_start_index + 3]

            weight = frame[header_start_index + 4]

            header_frame.priority(dep_stream_id, weight)

            header_start_index += 5  # if priority set, pass 5 byte(stream id, weight)

        # create header block

        header_end_index = 9 + frm_len - header_pad_length

        # get header block fragment

        header_block_frag = frame[header_start_index:header_end_index]

        if end_header:
            header_buffer = bytearray()

            for encoded_header in encoded_headers:
                if encoded_header.is_encoded:
                    header_buffer += encoded_header._encoded_data
                else:
                    raise ValueError("encoded header didn't encoded")

            decoder = Decoder()
            header_buffer += header_block_frag

            header_frame._header_list = decoder.decode(header_buffer)
        else:
            header_frame._encoded_data = header_block_frag

        return header_frame

    def __init__(self, id, end_header=True, end_stream=False):

        self.is_end_stream = end_header

        self.is_end_header = end_stream

        self._is_priority = False

        self._is_padded = False

        self._header_list = []  # http header list

        self._encoded_data = None

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

    def status(self, status=None):
        if status is not None:
            self.add(':status', status)
        else:
            for header in self._header_list:
                if header[0] == ':status':
                    return header[1]

    def method(self, method=None):
        if method is not None:
            self.add(':method', method)
        else:
            for header in self._header_list:
                if header[0] == ':method':
                    return header[1]

    def scheme(self, scheme=None):
        if scheme is not None:
            self.add(':scheme', scheme)
        else:
            for header in self._header_list:
                if header[0] == ':scheme':
                    return header[1]

    def authority(self, authority=None):
        if authority is not None:
            self.add(':authority', authority)
        else:
            for header in self._header_list:
                if header[0] == ':authority':
                    return header[1]

    def path(self, path=None):
        if path is not None:
            self.add(':path', path)
        else:
            for header in self._header_list:
                if header[0] == ':path':
                    return header[1]

    # Remove headers

    def remove(self, name):

        for header in self._header_list:
            if header[0] == name:
                self._header_list.remove(header)

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

    @property
    def is_encoded(self):
        return self._encoded_data is not None

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
