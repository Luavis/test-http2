"""
    test_settings_frame
    ~~~~~~~~~

    Test setting_frame.py

"""

from http2.setting_frame import SettingFrame
from http2.frame import (FrameType, Frame)


def test_setting_frame_data():

    frame = SettingFrame()

    frame.set(SettingFrame.SETTINGS_HEADER_TABLE_SIZE, 100)

    frame.set(SettingFrame.SETTINGS_ENABLE_PUSH, 1)

    assert frame.type == FrameType.SETTINGS

    read_frame = Frame.load(frame.get_frame_bin())

    assert read_frame.get(SettingFrame.SETTINGS_HEADER_TABLE_SIZE) == 100

    assert read_frame.get(SettingFrame.SETTINGS_ENABLE_PUSH) == 1


def test_ack_setting_frame():

    frame = SettingFrame(is_ack=True)

    try:
        frame.set(SettingFrame.SETTINGS_HEADER_TABLE_SIZE, 100)
    except:
        pass
    else:
        assert 0  # Exception was not raised

    read_frame = Frame.load(frame.get_frame_bin())

    assert read_frame.is_ack


def test_malform_setting_frame_data():

    try:
        # setting value is not 4 byte
        Frame.load(b'\x00\x00\x04\x04\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01')
    except:
        pass
    else:
        assert 0  # Exception was not raised
