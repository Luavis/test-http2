"""
    htt.htt
    ~~~~~~~

"""

import socket
from threading import Thread
import ssl
from http2.setting_frame import SettingFrame
from http2.frame import Frame
from http2.header_frame import HeaderFrame
from http2.data_frame import DataFrame

PREFACE_CODE = b"\x50\x52\x49\x20\x2a\x20\x48\x54\x54\x50\x2f\x32\x2e\x30\x0d\x0a\x0d\x0a\x53\x4d\x0d\x0a\x0d\x0a"


class HTTPSocket:

    def __init__(self):
        self.listensock = None

    def bind(self, port):

        self.listensock = socket.socket()

        self.listensock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.listensock.bind(('localhost', port))
        # self.listensock.settimeout(10 * 1000)

        self.listensock.listen(5)

    def accept(self):
        conn, addr = self.listensock.accept()
        return conn, addr


class HTTPMainThread(Thread):

    # default max header size is 64KB, default max content size 2MB

    def __init__(self, conn, buf_size, user_ip='', user_port=0, max_header_size=640000, max_content_size=2000000):

        Thread.__init__(self)

        self.buf_size = buf_size

        self.conn = conn

        self.last_msg_char = ''

        self.user_ip = user_ip

        self.user_port = user_port

        self.max_header_size = max_header_size

        self.max_content_size = max_content_size

    def run(self):

        is_http2 = False

        while True:
            try:
                read_msg = self.conn.recv(self.buf_size)
            except:
                continue

            if not len(read_msg) == 0:
                print(read_msg)

                if read_msg == PREFACE_CODE:
                    print('check preface')
                    setting_frame = SettingFrame(is_ack=True)
                    settings_bin = setting_frame.get_frame_bin()

                    self.conn.write(settings_bin)

                    is_http2 = True
                elif is_http2:

                    try:
                        frame = Frame.load(read_msg)
                        if isinstance(frame, HeaderFrame):
                            if frame.path == '/':
                                content = u'<h1>Hello World</h1><hr><p>It working in HTT server(HTTP/2)</p>'.encode()
                                # send header
                                response_header = HeaderFrame(id=0x1)
                                response_header.status = '200'
                                response_header.authority = 'localhost'
                                response_header.add('content-type', 'text/html')
                                response_header.add('content-length', str(len(content)))
                                header_bin = response_header.get_frame_bin()

                                print('send header : ', header_bin)
                                self.conn.write(header_bin)

                                # send data

                                data_frame = DataFrame(id=0x1, end_stream=True)
                                data_frame.data = content
                                data_bin = data_frame.get_frame_bin()

                                print('send data : ', data_bin)
                                self.conn.write(data_bin)
                    except:
                        print('unknown type')
                elif read_msg[-4:] == b'\r\n\r\n':
                    self.conn.write(b"HTTP/1.1 200 OK\r\nContent-Length: 11\r\n\r\nHello World")
                    self.conn.close()
                    return
            else:
                break

        self.conn.close()  # close it now


def main():

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.set_npn_protocols(['h2'])
    ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    print("[HTT] Start server")
    socket = HTTPSocket()

    print("[HTT] bind 443")
    socket.bind(443)

    while True:
        conn, addr = socket.accept()

        conn = ssl_context.wrap_socket(conn, server_side=True)

        thread = HTTPMainThread(conn, 1024, addr[0], addr[1])

        thread.run()

if __name__ == '__main__':
    main()
