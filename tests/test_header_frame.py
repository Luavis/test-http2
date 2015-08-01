"""
    test_header_frame
    ~~~~~~~~~

    Test header_frame.py

"""

from http2.header_frame import HeaderFrame


def test_header_frame_data():

    frame = HeaderFrame(id=0x0201)

    frame.method("GET")

    frame.scheme('https')

    frame.path('/')

    frame.add('host', 'locahost')

    frame.add('accept', 'text/html')

    frame.get_frame_bin()
