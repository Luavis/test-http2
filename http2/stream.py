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

    @classmethod
    def _create_stream_id(cls):  # TODO: make random to do not duplicate in one connection
        return int(math.floor(random.random() * 10000))

    def __init__(self, conn_control=False):

        self._state = StreamState.IDLE

        if conn_control:  # If connection control stream make it 0x0
            self._stream_id = 0x0
        else:
            self._stream_id = Stream._create_stream_id()

    @property
    def state(self):
        return self._state

    @property
    def stream_id(self):
        return self._stream_id
