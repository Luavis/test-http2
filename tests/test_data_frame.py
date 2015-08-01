"""
    test_data_frame
    ~~~~~~~~~

    Test data_frame.py

"""

from http2.data_frame import DataFrame
from http2.frame import (Frame, FrameType)


def test_data_frame_data():

    frame = DataFrame(id=0x0201)

    # set data as default html format
    frame.set_text(u'<html><heade></heade><body></body></html>', 'utf-8')

    assert frame.type == FrameType.DATA

    read_frame = Frame.load(frame.get_frame_bin())

    assert read_frame.data == frame.data  # check is same data


def test_padded_data_frame_data():

    frame = DataFrame(id=0x0201)

    # set data as default html format
    data = u'<html><heade></heade><body></body></html>'
    frame.set_text(data, 'utf-8')
    frame.padding(10)

    assert frame.type == FrameType.DATA
    read_frame = Frame.load(frame.get_frame_bin())

    assert read_frame.data == data.encode('utf-8')  # check is same data
