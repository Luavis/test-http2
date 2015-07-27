from socket import socket, AF_INET, SOCK_STREAM

BUFF_SIZE = 1024
ADDR = ('localhost', 8080)


def main():  # Testing HTTP/1.1

    client = socket(AF_INET, SOCK_STREAM)

    client.connect(ADDR)

    client.send('GET / HTTP/1.1\r\n\r\n')

    while True:

        data = client.recv(BUFF_SIZE)
        print(data)

if __name__ == '__main__':
    main()
