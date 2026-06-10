import pytest
from libs.gpsoauth.util import bytes_to_int, int_to_bytes

@pytest.mark.parametrize(
    "byte_seq, expected",
    [
        (b"", 0),
        (b"\x00", 0),
        (b"\x01", 1),
        (b"\x00\x01", 1),
        (b"\x01\x00", 256),
        (b"\xff", 255),
        (b"\x01\x02\x03\x04", 16909060),
        (b"\xff\xff\xff\xff", 4294967295),
        (b"\x00\x00\x01\x00", 256),
    ],
)
def test_bytes_to_int(byte_seq, expected):
    """Test converting bytes to integer."""
    assert bytes_to_int(byte_seq) == expected

def test_int_to_bytes_zero():
    assert int_to_bytes(0) == b"\0"
    assert int_to_bytes(0, pad_multiple=0) == b""
    assert int_to_bytes(0, pad_multiple=1) == b"\0"
    assert int_to_bytes(0, pad_multiple=4) == b"\0\0\0\0"

def test_int_to_bytes_negative():
    with pytest.raises(ValueError, match="Can only convert non-negative numbers."):
        int_to_bytes(-1)

def test_int_to_bytes_positive():
    # 255 is 0xFF
    assert int_to_bytes(255) == b"\xff"
    assert int_to_bytes(255, pad_multiple=1) == b"\xff"
    assert int_to_bytes(255, pad_multiple=2) == b"\x00\xff"
    assert int_to_bytes(255, pad_multiple=4) == b"\x00\x00\x00\xff"

    # 256 is 0x0100
    assert int_to_bytes(256) == b"\x01\x00"
    assert int_to_bytes(256, pad_multiple=2) == b"\x01\x00"
    assert int_to_bytes(256, pad_multiple=4) == b"\x00\x00\x01\x00"

    # 65535 is 0xFFFF
    assert int_to_bytes(65535) == b"\xff\xff"
    assert int_to_bytes(65535, pad_multiple=4) == b"\x00\x00\xff\xff"
