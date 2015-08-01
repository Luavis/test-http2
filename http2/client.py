from socket import socket, AF_INET, SOCK_STREAM
from stream import Stream
from http import (Request, Status)

BUFF_SIZE = 1024
ADDR = ('localhost', 8080)


def main():  # Testing HTTP/1.1

    client = socket(AF_INET, SOCK_STREAM)

    client.connect(ADDR)

    # client.send('GET / HTTP/1.1\r\n\r\n')

    data = client.recv(BUFF_SIZE)
    print(':'.join(x.encode('hex') for x in data))

    # send preface
    client.send('\x50\x52\x49\x20\x2a\x20\x48\x54\x54\x50\x2f\x32\x2e\x30\x0d\x0a\x0d\x0a\x53\x4d\x0d\x0a\x0d\x0a')

    client.send('\x00\x00\x00\x04\x00\x00\x00\x00\x00')  # Setting Frame

    data = client.recv(BUFF_SIZE)
    print(':'.join(x.encode('hex') for x in data))

    stream = Stream()

    request = Request()

    request.status = Status()
    request.status.path = '/'
    request.status.method = 'GET'
    request.headers = {}

    # request.headers['date'] = Header('Date', 'Sun, 06 Nov 2015 08:49:37 GMT')

    msg = stream.send_http_msg(request)
    print(':'.join(hex(x) for x in msg))

    client.send(msg)

    data = client.recv(BUFF_SIZE)
    print(':'.join(x.encode('hex') for x in data))

    client.send('\x00\x00\x00\x04\x01\x00\x00\x00\x00')  # Setting Frame

    data = client.recv(BUFF_SIZE)
    print(':'.join(x.encode('hex') for x in data))

    # client.send('\x00\x00\x00\x04\x01\x00\x00\x00\x00')  # Setting Frame

    # data = client.recv(BUFF_SIZE)
    # print(':'.join(x.encode('hex') for x in data))

    # while True:
    # print(':'.join(x.encode('hex') for x in data))
    #     print(data)

    # Server

    # server = socket(AF_INET, SOCK_STREAM)

    # server.bind(('0.0.0.0', 8000))

    # server.listen(5)

    # conn, addr = server.accept()

    # data = conn.recv(1024)
    # print(':'.join(x.encode('hex') for x in data))

    # conn.send('\x00\x00\x00\x04\x00\x00\x00\x00\x00')  # Setting

    # while True:

    #     data = conn.recv(1024)
    #     print(':'.join(x.encode('hex') for x in data))


if __name__ == '__main__':
    main()
