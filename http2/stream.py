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
from http2.frame import Frame
from http2.frame.header_frame import HeaderFrame
from http2.frame.data_frame import DataFrame
from http2.frame.push_promise_frame import PushPromiseFrame
from http2.frame.rst_frame import RSTFrame
from http2.frame.priority_frame import PriorityFrame
from http2.data_frame_io import DataFrameIO

from http2.errors import ProtocolError
from time import time


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

    def __init__(self, connection, wfile, stream_id=0x0):

        self.state = StreamState.IDLE

        # If8 connection control stream id must 0x0
        self.connection = connection
        self._stream_id = stream_id
        self._wfile = wfile
        self._client_headers = []
        self._server_headers = []
        self._last_header_raw = bytearray(0)  # empty header raw
        self.is_end_header = False
        self.req_stream_io = DataFrameIO()

    @property
    def id(self):
        return self._stream_id

    @property
    def is_connection_stream(self):
        return self._stream_id == 0x0

    @property
    def client_headers(self):
        return self._client_headers

    @property
    def server_headers(self):
        return self._server_headers

    @property
    def method(self):

        if self._client_headers:
            for header in self._client_headers:
                if header[0] == ':method':
                    return header[1]

        else:  # stream didn't end
            return None

        return 'GET'  # default method

    @property
    def path(self):

        if self._client_headers:
            for header in self._client_headers:
                if header[0] == ':path':
                    return header[1]

        else:  # stream didn't end
            return None

        return '/'  # default path

    @property
    def is_closed(self):
        return self.state == StreamState.CLOSED

    @property
    def is_wait_for_res(self):
        # self.is_end_header
        return self.state == StreamState.HALF_CLOSED_REMOTE

    def receive_frame(self, frame_header, frame_raw):

        try:
            frame = Frame.load(frame_raw, frame_header, decoder=self.connection.decoder)

            if isinstance(frame, HeaderFrame):
                self._last_header_raw = frame.data  # get payload of frame raw
                self._client_headers = frame.get_all()
                self.state = StreamState.OPEN  # if header recv, open stream

                if frame.is_end_header:
                    self.is_end_header = frame.is_end_header
                print('is_end_stream ', frame.is_end_stream)
            elif isinstance(frame, DataFrame):
                # TODO : need test
                self.req_stream_io.write(frame.data)
                print('is_end_stream ', frame.is_end_stream)

            else:
                # ignore unknow frame
                return False

            if not isinstance(frame, PriorityFrame):  # priority frame always be able to recieved

                if self.state == StreamState.HALF_CLOSED_REMOTE:
                    if not(isinstance(frame.RSTFrame)):  # or TODO: WINDOW_UPDATE
                        raise ProtocolError()
                elif self.state == StreamState.CLOSED:
                    if not(isinstance(frame.RSTFrame)):  # or TODO: WINDOW_UPDATE
                        raise ProtocolError()
                    elif time() - self._closed_time > 1:  # if these streams are recv after 1 sec
                        raise ProtocolError()

            if hasattr(frame, 'is_end_stream') and frame.is_end_stream:  # stream that can change state

                if self.state == StreamState.HALF_CLOSED_LOCAL:
                    self.close()
                elif self.state == StreamState.OPEN:
                    self.state = StreamState.HALF_CLOSED_REMOTE
                else:  # it would not be occured
                    raise ProtocolError()

            if isinstance(frame, RSTFrame):
                self.close()

        except:
            raise ProtocolError()  # unknow exception occur protocol error
            return False

        return True

    def send_header(self, headers, end_stream=False):  # TODO : if header block is bigger than stream size make it sep

        self._server_headers = headers
        header_frame = HeaderFrame(id=self._stream_id, header_list=headers, end_stream=end_stream)

        self.send_frame(header_frame)

    def send_data(self, data, end_stream=False):

        data_frame = DataFrame(id=self._stream_id, end_stream=end_stream)
        data_frame.data = data

        self.send_frame(data_frame)

    def promise(self, promise_headers=[]):

        # TODO: end headers when it can contain all headers in PP Frame

        promise = PushPromiseFrame(self.id, promise_headers, end_header=True)

        push_stream = self.connection.create_stream()

        promise.promised_stream_id = push_stream.id

        self.send_frame(promise)  # send push promise

        return push_stream

    def send_frame(self, frame):
        frame_bin = frame.get_frame_bin()

        self._wfile.write(frame_bin)

    def close(self):
        self.state = StreamState.CLOSED
        self._closed_time = time()
