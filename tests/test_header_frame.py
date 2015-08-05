"""
    test_header_frame
    ~~~~~~~~~

    Test header_frame.py

"""

from http2.header_frame import HeaderFrame
from http2.frame import (Frame, FrameType)


def test_header_frame_data():

    frame = HeaderFrame(id=0x0201)

    frame.method = "GET"

    frame.scheme = 'https'

    frame.path = '/'

    frame.add('host', 'localhost')

    frame.add('accept', 'text/html')

    assert frame.type == FrameType.HEADERS

    read_frame = Frame.load(frame.get_frame_bin())

    assert read_frame.method == "GET"

    assert read_frame.scheme == "https"

    assert read_frame.path == "/"

    assert read_frame.get('host') == "localhost"

    assert read_frame.get('accept') == "text/html"


def test_chrom_refresh_frame_data():

    frame_data = b'\x00\x00\x1e\x01%\x00\x00\x00\x07\x00\x00\x00\x00\xb6\xc7\x82\x00\x84\xb9X\xd3?\x89bQ\xf71\x0fR\xe6!\xff\x87\xbf\xc5\xc4\xc2\xbe\xc0'

    frame = Frame.load(frame_data)

    print(frame)


def test_multiple_header_frame_data():

    encoded_frames = []

    frame = HeaderFrame(id=0x0201, end_header=False)

    frame.method = "GET"

    frame.scheme = 'https'

    frame.path = '/'

    assert frame.type == FrameType.HEADERS

    encoded_frames.append(Frame.load(frame.get_frame_bin()))

    assert encoded_frames[0].is_encoded

    second_frame = HeaderFrame(id=0x0201, end_header=False)

    second_frame.add('host', 'localhost')

    second_frame.add('accept', 'text/html')

    encoded_frames.append(Frame.load(second_frame.get_frame_bin()))

    last_frame = HeaderFrame(id=0x0201, end_header=True)

    last_frame.add('accept-language', 'ko')

    read_frame = Frame.load(last_frame.get_frame_bin(), None, encoded_frames)

    assert read_frame.method == "GET"

    assert read_frame.scheme == "https"

    assert read_frame.path == "/"

    assert read_frame.get('host') == "localhost"

    assert read_frame.get('accept') == "text/html"

    assert read_frame.get('accept-language') == "ko"
