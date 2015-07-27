from socket import socket, AF_INET, SOCK_STREAM
from frame import Frame

BUFF_SIZE = 1024
ADDR = ('localhost', 8080)


def main():

    client = socket(AF_INET, SOCK_STREAM)

    client.connect(ADDR)

    # client.send('GET / HTTP/1.1\r\n\r\n')

    # while True:

    #     data = client.recv(BUFF_SIZE)
    #     print(data)

if __name__ == '__main__':
    main()
