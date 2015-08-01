"""
    htt.htt
    ~~~~~~~

"""

import socket
from threading import Thread
import ssl

PREFACE_CODE = "\x50\x52\x49\x20\x2a\x20\x48\x54\x54\x50\x2f\x32\x2e\x30\x0d\x0a\x0d\x0a\x53\x4d\x0d\x0a\x0d\x0a"


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

        while True:
            read_msg = self.conn.recv(self.buf_size)
            if not len(read_msg) == 0:
                print(read_msg)

                if read_msg == PREFACE_CODE:
                    print('check preface')

                if read_msg[-4:] == b'\r\n\r\n':
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
