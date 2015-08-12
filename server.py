"""
    htt.htt
    ~~~~~~~

"""

import ssl
from http2.server import (BaseHTTP2RequestHandler, HTTP2Server)

PORT = 8000


class EchoHTTPRequestHandler(BaseHTTP2RequestHandler):  # for test

    def do_POST(self):
        """Serve a POST request."""

        if self.path == '/upload':
            import io
            reader = io.BufferedReader(self.stream.req_stream_io)

            msg = reader.read(1024)
            print('msg ', msg)

            self.send_response(200)
            self.send_header("Content-Length", len(msg))
            self.send_header("Content-Type", 'text/html')
            self.end_headers()

            self.send_data(msg)
            self.flush()

    def do_GET(self):
        """Serve a GET request."""

        if self.path == '/':

            push_req_headers = [(':authority', 'localhost:8000'),
                                                (':scheme', 'https'),
                                                (':method', 'GET'),
                                                (':path', '/style.css')]

            push_stream = self.push(self.stream, push_req_headers)
            if push_stream:
                push_res_headers = [(':scheme', 'https')]

                res_data = u'h1 {color: blue}'.encode()

                push_res_headers.append((':status', '200'))
                push_res_headers.append(("content-length", len(res_data)))
                push_res_headers.append(("content-type", 'text/css'))
                push_res_headers.append(('cache-control', 'public, max-age=3600'))

                push_stream.send_header(push_res_headers)

                push_stream.send_data(res_data, end_stream=True)  # push
                self.flush()

            push_req_headers = [(':authority', 'localhost:8000'),
                                                (':scheme', 'https'),
                                                (':method', 'GET'),
                                                (':path', '/script.js')]

            push_stream = self.push(self.stream, push_req_headers)
            if push_stream:
                push_res_headers = [(':scheme', 'https')]

                res_data = u'alert("Hello World")'.encode()

                push_res_headers.append((':status', '200'))
                push_res_headers.append(("content-length", len(res_data)))
                push_res_headers.append(("content-type", 'text/javascript'))
                push_res_headers.append(('cache-control', 'public, max-age=3600'))

                push_stream.send_header(push_res_headers)

                push_stream.send_data(res_data, end_stream=True)  # push
                self.flush()

            msg = u"""
                <!doctype html>
                <html>
                <head>
                    <link href="/style.css" rel="stylesheet">
                    <script src="/script.js"></script>
                </head>
                <body>
            """.encode()
            msg += u'<h1>Hello World</h1><hr><p>It working in HTT server('.encode()
            msg += self.request_version.encode()
            msg += u')</p>'.encode()

            msg += u"""
                </body>
                </html>
            """.encode()

            self.send_response(200)
            self.send_header("Content-Length", len(msg))
            self.send_header("Content-Type", 'text/html')
            self.end_headers()

            self.send_data(msg)
            self.flush()
        elif self.path == '/style.css':
            print('style')
            msg = u'h1 {color: red}'.encode()

            self.send_response(200)
            self.send_header("Content-Length", len(msg))
            self.send_header("Content-Type", 'text/css')
            self.end_headers()

            self.send_data(msg)
            self.flush()
        else:
            msg = u''.encode()

            self.send_response(200)
            self.send_header("Content-Length", len(msg))
            self.send_header("Content-Type", 'text/html')
            self.end_headers()

            self.send_data(msg)
            self.flush()


def main():

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.set_npn_protocols(['h2'])
    ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    handler = EchoHTTPRequestHandler

    httpd = HTTP2Server(("", PORT), handler)

    httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)

    print("serving at port", PORT)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
