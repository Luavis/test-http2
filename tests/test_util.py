"""
    test_util
    ~~~~~~~~~

    Test util.py

"""

from http2.util import int_to_bytes


def test_int_to_byte():

    byte = int_to_bytes(0x0F4240, 3)

    assert byte[0] == 0x0F

    assert byte[1] == 0x42

    assert byte[2] == 0x40
