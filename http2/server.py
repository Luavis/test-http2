"""

    HTTP server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
try:
    from http.server import (BaseHTTPRequestHandler, HTTPServer)
except:
    from BaseHTTPServer import (BaseHTTPRequestHandler, HTTPServer)

from http2.setting_frame import SettingFrame
from http2.connection import Connection
from http2.frame import Frame
import traceback

__version__ = "0.1"

PREFACE_CODE = b"\x50\x52\x49\x20\x2a\x20\x48\x54\x54\x50\x2f\x32\x2e\x30\x0d\x0a\x0d\x0a\x53\x4d\x0d\x0a\x0d\x0a"
PREFACE_SIZE = len(PREFACE_CODE)
HTTP2_BUFFER_SIZE = 1024


def _quote_html(html):
    return html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class HTTP2Server(HTTPServer):
    pass


class BaseHTTP2RequestHandler(BaseHTTPRequestHandler):

    server_version = "BaseHTTP2/" + __version__

    def parse_http2_request(self):
        try:
            self.raw_requestdata = self.connection.read(HTTP2_BUFFER_SIZE)
            print(self.raw_requestdata)
            frame_header = Frame.parse_header(self.raw_requestdata)
            frm_len, frm_type, frm_flag, frm_id = frame_header

            stream = self.http2_connection.get_stream(frm_id)
            stream.receive_frame(frame_header, self.raw_requestdata)

            if stream.is_closed:

                print('end stream id : ', stream.id, ' frm_id ', frm_id)

                self.headers = stream._client_headers
                # self.request_version = 'HTTP/2.0' always
                self.requestline = stream.method + ' ' + stream.path + ' HTTP/2.0'  # virtual request line
                self.command = stream.method
                self.response_stream = stream

                return True  # handle one request

        except Exception as e:  # TODO : when parse error closed connection
            print('error')
            print(traceback.format_exc())
            print(e)

        return False

    def handle(self):
        """Handle multiple requests if necessary."""
        self.close_connection = True

        # if request version not set check preface first
        preface = self.rfile.peek(PREFACE_SIZE)

        if preface == PREFACE_CODE:  # check code

            self.request_version = 'HTTP/2.0'

            # keep alive connection
            self.close_connection = False

            # send server preface

            setting_frame = SettingFrame(is_ack=True)
            settings_bin = setting_frame.get_frame_bin()

            self.wfile.write(settings_bin)

            self.http2_connection = Connection(self)

        if self.request_version == 'HTTP/2.0':
            try:
                while True:
                    if self.parse_http2_request():

                        # clear
                        self.handle_one_http2_request()
                        self.headers = []
                        # self.request_version = 'HTTP/2.0' always
                        self.requestline = ''
                        self.command = ''
                        self.response_stream = None
            except:
                pass  # end
        else:
            self.handle_one_request()

            while not self.close_connection:
                self.handle_one_request()

    def handle_one_http2_request(self):
        print('create_stream')
        # self.response_stream = self.http2_connection.create_stream()
        self._headers_buffer = []
        # parse request
        mname = 'do_' + self.command

        if not hasattr(self, mname):
            self.send_error(501, "Unsupported method (%r)" % self.command)
            return

        method = getattr(self, mname)
        method()

    def send_response_only(self, code, message=None):
        if self.request_version <= 'HTTP/1.1':
            BaseHTTPRequestHandler.send_response_only(self, code, message)
        elif self.request_version == 'HTTP/2.0':
            self.send_header(':status', str(code))
            self.send_header(':scheme', 'https')  # TODO : fix it later

    def send_header(self, keyword, value):
        if self.request_version <= 'HTTP/1.1':
            BaseHTTPRequestHandler.send_header(self, keyword, value)
        elif self.request_version == 'HTTP/2.0':
            self._headers_buffer.append((keyword.lower(), str(value)))

    def end_headers(self):
        if self.request_version <= 'HTTP/1.1':
            BaseHTTPRequestHandler.end_headers(self)
        elif self.request_version == 'HTTP/2.0':
            self.flush_headers()

    def flush_headers(self):
        if self.request_version <= 'HTTP/1.1':
            BaseHTTPRequestHandler.flush_headers(self)
        elif self.request_version == 'HTTP/2.0':
            print(self._headers_buffer)
            self.response_stream.send_header(self._headers_buffer)
            self._headers_buffer = []

    def send_data(self, data):
        print('send data')
        if self.request_version <= 'HTTP/1.1':
            self.wfile.write(data)
        elif self.request_version == 'HTTP/2.0':
            self.response_stream.send_data(data, end_stream=True)

    def flush(self):
        if self.request_version == 'HTTP/2.0':
            print('end_data')
            # self.response_stream.send_data(bytearray(0), end_stream=True)  # TODO : fix it to RST_STREAM frame

        self.wfile.flush()
