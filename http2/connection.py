
from http2.frame import DEFAULT_FRAME_MAX_SIZE
from http2.stream import Stream
from http2.hpack.hpack import (Decoder, Encoder)
from http2.errors import StreamClosedError, ProtocolError


class Connection(object):

    LAST_STREAM_ID = 0x0  # server stream is even number

    @classmethod
    def _create_stream_id(cls):  # TODO: make random to do not duplicate in one connection

        Connection.LAST_STREAM_ID += 2

        return Connection.LAST_STREAM_ID

    def __init__(self, request_handler):
        self.frame_max_size = DEFAULT_FRAME_MAX_SIZE
        self.stream_list = {}
        self._request_handler = request_handler
        self.decoder = Decoder()
        self.encoder = Encoder()

        self.stream_list[0] = Stream(self, self._request_handler.wfile, 0)  # setting stream

    def create_stream(self):  # when server create stream
        stream = Stream(self, self._request_handler.wfile, Connection._create_stream_id())

        self.stream_list[stream.id] = stream

        return stream

    def get_stream(self, stream_id):
        stream = self.stream_list.get(stream_id)

        if stream is not None:
            if stream.is_closed:
                raise StreamClosedError()  # if closed stream raise exception
        else:
            if stream_id % 2 is 0:  # even = server stream
                stream = self.create_stream()
            else:  # odd = client stream
                stream = self.created_stream(stream_id)

        return stream

    def promise(self, req_headers=[]):

        promise_stream = self.create_stream()
        return promise_stream.promise(promise_headers=req_headers)

    # TODO : when there is too many streams, restrict to create it
    def created_stream(self, stream_id):  # when client create stream
        if stream_id % 2 == 0:
            raise Exception('Client create even stream id')  # TODO : raise protocol error exception
        stream = Stream(self, self._request_handler.wfile, stream_id)

        self.stream_list[stream.id] = stream

        return stream

    def stream_receive_frame(self, stream, frame_header, frame_raw):

        """
            Receiving any frame other than HEADERS or PRIORITY on a stream in
            this state MUST be treated as a connection error (Section 5.4.1)
            of type PROTOCOL_ERROR.
        """
        if stream is None:
            raise ProtocolError()

        stream.receive_frame(frame_header, frame_raw)

        return stream
