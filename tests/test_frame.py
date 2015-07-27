"""
    test_frame
    ~~~~~~~~~

    Test http2.frame

"""

from http2.frame import Frame


def test_frame_data():

    frame = Frame()

    try:
        frame.data = bytearray(Frame.FRAME_MAX_SIZE) + 1  # test over-byte
    except Exception:
        pass
    else:
        assert 0  # passed over byte

    frame.data = '\xFF\xFF' + bytearray(Frame.FRAME_MIN_SIZE)

    frame.id = 0x0

    frame_bin = frame.get_frame_bin()

    assert frame_bin[0] << 16 | frame_bin[1] << 8 | frame_bin[2] << 0 == len(frame.data)

    # type is 0
    assert frame_bin[3] == 0

    # flag is 0
    assert frame_bin[4] == 0

    assert frame_bin[5] << 24 | frame_bin[6] << 16 | frame_bin[7] << 8 | frame_bin[8] << 0 == 0x0

    # check payload
    assert frame_bin[9:] == '\xFF\xFF' + bytearray(Frame.FRAME_MIN_SIZE)


def test_frame_header():

    frame = Frame()

    try:
        frame.data = bytearray(Frame.FRAME_MAX_SIZE) + 1  # test over-byte
    except Exception:
        pass
    else:
        assert 0  # passed over byte

    frame.data = '\xFF\xFF' + bytearray(Frame.FRAME_MIN_SIZE)

    frame.type = 0x10

    frame.flag = 0x0D

    frame.id = 0x010CA0

    frame_bin = frame.get_frame_bin()

    assert frame_bin[0] << 16 | frame_bin[1] << 8 | frame_bin[2] << 0 == len(frame.data)

    # type is 0
    assert frame_bin[3] == 0x10

    # flag is 0
    assert frame_bin[4] == 0x0D

    assert frame_bin[5] << 24 | frame_bin[6] << 16 | frame_bin[7] << 8 | frame_bin[8] << 0 == 0x010CA0

    # check payload
    assert frame_bin[9:] == '\xFF\xFF' + bytearray(Frame.FRAME_MIN_SIZE)
