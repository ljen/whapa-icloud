import pytest

from .util import bytes_to_int

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
    ],
)
def test_bytes_to_int(byte_seq, expected):
    """Test converting bytes to integer."""
    assert bytes_to_int(byte_seq) == expected
