"""
                             +--------+
                     send PP |        | recv PP
                    ,--------|  idle  |--------.
                   /         |        |         \
                  v          +--------+          v
           +----------+          |           +----------+
           |          |          | send H /  |          |
    ,------| reserved |          | recv H    | reserved |------.
    |      | (local)  |          |           | (remote) |      |
    |      +----------+          v           +----------+      |
    |          |             +--------+             |          |
    |          |     recv ES |        | send ES     |          |
    |   send H |     ,-------|  open  |-------.     | recv H   |
    |          |    /        |        |        \    |          |
    |          v   v         +--------+         v   v          |
    |      +----------+          |           +----------+      |
    |      |   half   |          |           |   half   |      |
    |      |  closed  |          | send R /  |  closed  |      |
    |      | (remote) |          | recv R    | (local)  |      |
    |      +----------+          |           +----------+      |
    |           |                |                 |           |
    |           | send ES /      |       recv ES / |           |
    |           | send R /       v        send R / |           |
    |           | recv R     +--------+   recv R   |           |
    | send R /  `----------->|        |<-----------'  send R / |
    | recv R                 | closed |               recv R   |
    `----------------------->|        |<----------------------'
                             +--------+

       send:   endpoint sends this frame
       recv:   endpoint receives this frame

       H:  HEADERS frame (with implied CONTINUATIONs)
       PP: PUSH_PROMISE frame (with implied CONTINUATIONs)
       ES: END_STREAM flag
       R:  RST_STREAM frame
"""

from frame import (Frame, FrameType)
from http import (HTTPMessage, Status)
from hpack.hpack import Encoder

import math
import random


class StreamState(object):

    IDLE = 0x0

    RESERVED_LOCAL = 0x1

    RESERVED_REMOTE = 0x2

    OPEN = 0x3

    HALF_CLOSED_REMOTE = 0x4

    HALF_CLOSED_LOCAL = 0x5

    CLOSED = 0x6


class Stream(object):

    CRLF = '\r\n'

    @classmethod
    def _create_stream_id(cls):  # TODO: make random to do not duplicate in one connection
        return int(math.floor(random.random() * 10000))

    def __init__(self, conn_control=False):

        self._state = StreamState.IDLE

        if conn_control:  # If connection control stream make it 0x0
            self._stream_id = 0x0
        else:
            self._stream_id = Stream._create_stream_id()

        self._msg = None

    @property
    def state(self):
        return self._state

    @property
    def stream_id(self):
        return self._stream_id

    @property
    def msg(self):
        return self._msg

    def send_http_msg(self, msg):  # general situation
        if not isinstance(msg, HTTPMessage):
            raise ValueError('`msg` must be instance of HTTPMessage')

        self._msg = msg

        # TODO : get client socket and send it

        return self._send_headers()

    def _get_header_buf(self):

        encoder = Encoder()
        header_list = []

        # add status

        if self._msg.status.type == Status.REQ:
            header_list.append((':method', self._msg.status.method))
            header_list.append((':scheme', 'http'))
            header_list.append((':authority', 'localhost'))
            header_list.append((':path', self._msg.status.path))

        if self.msg.headers is not None:

            for (h_name, header) in self.msg.headers.items():
                header_list.append((h_name, header.value))

        header_buf = encoder.encode(header_list)

        return header_buf

    def _send_headers(self):

        stream_payload = bytearray()

        header_buf = self._get_header_buf()

        frame = Frame()
        frame.type = FrameType.HEADERS
        frame.id = self.stream_id
        frame.flag = 0x05

        pad_len = 0

        header_buf_len = len(header_buf)

        if header_buf_len < Frame.FRAME_MIN_SIZE:  # Padding without HEADERS frame header
            pad_len = Frame.FRAME_MIN_SIZE - header_buf_len
            header_buf += bytearray(pad_len)  # padding empty data
            header_buf_len = Frame.FRAME_MIN_SIZE

        stream_payload += header_buf

        # TODO : get client socket and send it

        frame.data = stream_payload

        return frame.get_frame_bin()
