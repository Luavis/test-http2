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
from http2.header_frame import HeaderFrame
from http2.data_frame import DataFrame


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

        # If connection control stream id must 0x0
        self.connection = connection
        self._stream_id = stream_id
        self._wfile = wfile
        self._client_headers = []
        self._server_headers = []
        self._last_header_raw = bytearray(0)  # empty header raw

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

    def receive_frame(self, frame_header, frame_raw):

        try:
            frame = Frame.load(frame_raw, frame_header, decoder=self.connection.decoder)

            if isinstance(frame, HeaderFrame):
                self._last_header_raw = frame.data  # get payload of frame raw
                print(self._last_header_raw)
                self._client_headers = frame.get_all()
            if isinstance(frame, DataFrame):
                pass  # TODO : Not impl
            else:
                pass

            if hasattr(frame, 'is_end_stream') and frame.is_end_stream:  # if frame can end stream
                self.close()

        except Exception as e:  # TODO : if unknown frame send protocol error
            print('unknown header')
            print(e)

            return False

        return True

    def send_header(self, headers, end_stream=False):  # TODO : if header block is bigger than stream size make it sep

        self._server_headers = headers
        header_frame = HeaderFrame(id=self._stream_id, header_list=headers, end_stream=end_stream)

        header_bin = header_frame.get_frame_bin()
        print(header_bin)
        self._wfile.write(header_bin)

    def send_data(self, data, end_stream=False):

        data_frame = DataFrame(id=self._stream_id, end_stream=end_stream)
        data_frame.data = data

        data_bin = data_frame.get_frame_bin()

        print(data_bin)

        self._wfile.write(data_bin)

    def close(self):
        self.state = StreamState.CLOSED
