
from http2.frame import DEFAULT_FRAME_MAX_SIZE
from http2.frame.push_promise_frame import PushPromiseFrame
from http2.stream import Stream
from http2.hpack.hpack import (Decoder, Encoder)


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
            pass  # if closed stream raise exception
        else:
            if stream_id % 2 is 0:  # even = server stream
                stream = self.create_stream()
            else:  # odd = client stream
                stream = self.created_stream(stream_id)

        return stream

    def push(self, req_headers=[], res_headers=[], res_data=bytearray()):

        # TODO: end headers when it can contain all headers in PP Frame
        promise_stream = self.create_stream()

        promise = PushPromiseFrame(promise_stream.id, req_headers, end_header=True)
        print('push promise stream id', promise_stream.id)

        push_stream = self.create_stream()

        promise.promised_stream_id = push_stream.id

        promise_stream.send_frame(promise)  # send push promise

        print('push stream id', push_stream.id)

        # TODO: end headers when it can contain all headers in PP Frame
        push_stream.send_header(res_headers, end_stream=True)

        push_stream.send_data(res_data)  # push

    # TODO : when there is too many streams, restrict to create it
    def created_stream(self, stream_id):  # when client create stream
        if stream_id % 2 == 0:
            raise Exception('Client create even stream id')  # TODO : raise protocol error exception
        stream = Stream(self, self._request_handler.wfile, stream_id)

        self.stream_list[stream.id] = stream

        return stream

    def stream_receive_frame(self, stream, frame_header, frame_raw):

        if stream is None:
            raise Exception('Unknonw stream received frame')  # TODO : raise protocol error exception

        stream.receive_frame(frame_header, frame_raw)

        return stream
