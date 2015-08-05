
from socket import SocketIO
from http2.frame import DEFAULT_FRAME_MAX_SIZE
from http2.data_frame import DataFrame


class DataSocketIO(SocketIO):

    def __init__(self, sock, mode, stream=None):
        self.stream = stream
        SocketIO.__init__(self, sock, mode)

    def write(self, b, max_frame_size=DEFAULT_FRAME_MAX_SIZE):
        """Write the given bytes or bytearray object *b* to the socket
        and return the number of bytes written.  This can be less than
        len(b) if not all data could be written.  If the socket is
        non-blocking and no bytes could be written None is returned.
        """

        print('send_data', self.stream.id)
        print(b)

        b_len = len(b)

        if b_len > max_frame_size:

            indicator = max_frame_size

            while indicator < b_len:
                self.write(b[indicator:(indicator + max_frame_size)], max_frame_size)
                indicator += max_frame_size
        else:
            frame = DataFrame(self.stream.id, end_stream=True)
            frame.data = b
            SocketIO.write(self, frame.get_frame_bin())

    # def flush(self):
    #     frame = DataFrame(self.stream.id, end_stream=True)
    #     frame.data = bytearray()
    #     print('end stream')
    #     print(frame.get_frame_bin())
    #     SocketIO.write(self, frame.get_frame_bin())
